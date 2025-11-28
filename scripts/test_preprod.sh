#!/bin/bash
# Script to test Python functions with cardano-node on preprod
# Usage: ./scripts/test_preprod.sh

set -e

# Get project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "=========================================="
echo "Testing Python Functions with Preprod Node"
echo "=========================================="
echo ""

# Check if node is already running
if [ -S preprod-socket/node.socket ]; then
    echo "✓ Cardano node socket found at preprod-socket/node.socket"
    echo "  (Assuming node is already running)"
else
    echo "Starting cardano-node for preprod..."
    echo "  This may take a while to sync..."
    ./scripts/start_node.sh preprod > preprod.log 2>&1 &
    NODE_PID=$!
    echo "  Node started with PID: $NODE_PID"
    
    # Wait for socket to appear
    echo "Waiting for node socket to be created..."
    timeout=120
    elapsed=0
    while [ ! -S preprod-socket/node.socket ] && [ $elapsed -lt $timeout ]; do
        sleep 2
        elapsed=$((elapsed + 2))
        echo -n "."
    done
    echo ""
    
    if [ ! -S preprod-socket/node.socket ]; then
        echo "✗ Error: Node socket not created within $timeout seconds"
        kill $NODE_PID 2>/dev/null || true
        exit 1
    fi
    echo "✓ Node socket created"
fi

# Check if Ogmios/Kupo are running
if docker ps | grep -q ogmios-preprod; then
    echo "✓ Ogmios container is running"
else
    echo "Starting Ogmios and Kupo..."
    docker-compose -f docker-compose.preprod.yml up -d
    
    echo "Waiting for services to be ready..."
    sleep 10
    
    # Check health
    if curl -s http://localhost:1337/health > /dev/null 2>&1; then
        echo "✓ Ogmios is healthy"
    else
        echo "⚠ Warning: Ogmios health check failed"
    fi
    
    if curl -s http://localhost:1442/health > /dev/null 2>&1; then
        echo "✓ Kupo is healthy"
    else
        echo "⚠ Warning: Kupo health check failed"
    fi
fi

# Set up Python environment
echo ""
echo "Setting up Python test environment..."
cd offchain

if [ ! -d venv ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Install dependencies if needed
# After venv activation, python should be available, but use python3 as fallback
PYTHON_CMD="python3"
if command -v python &> /dev/null; then
    PYTHON_CMD="python"
fi

if ! $PYTHON_CMD -c "import pytest" 2>/dev/null; then
    echo "Installing test dependencies..."
    pip install -q -r requirements.txt pytest pytest-asyncio
fi

# Set environment variables
export CARDANO_NETWORK=preprod
export OGMIOS_URL=ws://localhost:1337
export KUPO_URL=http://localhost:1442
export CARDANO_NODE_SOCKET="$PROJECT_ROOT/preprod-socket/node.socket"
export DATA_DIRECTORY="$PROJECT_ROOT/offchain/data-preprod"

echo ""
echo "Environment variables:"
echo "  CARDANO_NETWORK=$CARDANO_NETWORK"
echo "  OGMIOS_URL=$OGMIOS_URL"
echo "  KUPO_URL=$KUPO_URL"
echo "  CARDANO_NODE_SOCKET=$CARDANO_NODE_SOCKET"
echo "  DATA_DIRECTORY=$DATA_DIRECTORY"
echo ""

# Test connectivity first
echo "Testing connectivity..."
$PYTHON_CMD cli.py init \
    --network preprod \
    --ogmios-url "$OGMIOS_URL" \
    --kupo-url "$KUPO_URL" \
    --cardano-node-socket "$CARDANO_NODE_SOCKET" \
    --output json || {
    echo "✗ Connectivity test failed"
    echo "  Make sure all services are running and synced"
    exit 1
}

echo ""
echo "✓ Connectivity test passed"
echo ""

# Run tests
echo "Running integration tests..."
echo ""

pytest tests/integration/ -v --tb=short

TEST_EXIT_CODE=$?

echo ""
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "=========================================="
    echo "✓ All tests passed!"
    echo "=========================================="
else
    echo "=========================================="
    echo "✗ Some tests failed (exit code: $TEST_EXIT_CODE)"
    echo "=========================================="
fi

exit $TEST_EXIT_CODE

