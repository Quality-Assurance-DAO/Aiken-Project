#!/bin/bash
# Script to start Cardano node, Ogmios, and Kupo services
# Usage: ./scripts/start_services.sh [preprod|preview|mainnet]

set -e

NETWORK="${1:-preprod}"

# Get the project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Network-specific configuration
case "$NETWORK" in
  preprod)
    CONFIG_DIR="$PROJECT_ROOT/share/preprod"
    SOCKET_DIR="$PROJECT_ROOT/preprod-socket"
    DB_DIR="$PROJECT_ROOT/db-preprod"
    LOG_FILE="$PROJECT_ROOT/preprod.log"
    DOCKER_COMPOSE_FILE="$PROJECT_ROOT/docker-compose.preprod.yml"
    ;;
  preview)
    CONFIG_DIR="$PROJECT_ROOT/share/preview"
    SOCKET_DIR="$PROJECT_ROOT/preview-socket"
    DB_DIR="$PROJECT_ROOT/db-preview"
    LOG_FILE="$PROJECT_ROOT/preview.log"
    echo "Preview network not yet configured in docker-compose"
    exit 1
    ;;
  mainnet)
    CONFIG_DIR="$PROJECT_ROOT/share/mainnet"
    SOCKET_DIR="$PROJECT_ROOT/mainnet-socket"
    DB_DIR="$PROJECT_ROOT/db-mainnet"
    LOG_FILE="$PROJECT_ROOT/mainnet.log"
    echo "Mainnet network not yet configured in docker-compose"
    exit 1
    ;;
  *)
    echo "Error: Unknown network: $NETWORK" >&2
    echo "Usage: $0 [preprod|preview|mainnet]" >&2
    exit 1
    ;;
esac

echo "Starting services for $NETWORK network..."
echo ""

# Check if Cardano node is running
SOCKET_PATH="$SOCKET_DIR/node.socket"
if [ -S "$SOCKET_PATH" ] && lsof "$SOCKET_PATH" > /dev/null 2>&1; then
    echo "✓ Cardano node is already running"
else
    echo "Starting Cardano node..."
    # Start node in background
    cd "$PROJECT_ROOT"
    nohup "$PROJECT_ROOT/scripts/start_node.sh" "$NETWORK" > "$LOG_FILE" 2>&1 &
    NODE_PID=$!
    echo "Cardano node starting (PID: $NODE_PID)"
    echo "Logs: tail -f $LOG_FILE"
    
    # Wait for socket to be created
    echo "Waiting for node socket to be created..."
    for i in {1..30}; do
        if [ -S "$SOCKET_PATH" ]; then
            echo "✓ Node socket created"
            break
        fi
        sleep 1
    done
    
    if [ ! -S "$SOCKET_PATH" ]; then
        echo "Error: Node socket not created after 30 seconds"
        exit 1
    fi
fi

# Check if native Ogmios/Kupo binaries are available
USE_NATIVE=false
if command -v ogmios > /dev/null 2>&1 && command -v kupo > /dev/null 2>&1; then
    USE_NATIVE=true
    echo "✓ Native Ogmios and Kupo binaries found"
fi

# Check if Ogmios and Kupo are already running
OGMIOS_RUNNING=false
KUPO_RUNNING=false

if [ "$USE_NATIVE" = true ]; then
    # Check for native processes
    if pgrep -f "ogmios.*--node-socket.*$SOCKET_PATH" > /dev/null 2>&1; then
        OGMIOS_RUNNING=true
    fi
    if pgrep -f "kupo.*--node-socket.*$SOCKET_PATH" > /dev/null 2>&1; then
        KUPO_RUNNING=true
    fi
else
    # Check for Docker containers
    if docker ps --format '{{.Names}}' | grep -q "ogmios-preprod\|kupo-preprod"; then
        OGMIOS_RUNNING=true
        KUPO_RUNNING=true
    fi
fi

if [ "$OGMIOS_RUNNING" = true ] && [ "$KUPO_RUNNING" = true ]; then
    echo "Ogmios/Kupo already running"
    if [ "$USE_NATIVE" = true ]; then
        echo "Native processes detected"
    else
        docker ps --filter "name=ogmios-preprod" --filter "name=kupo-preprod" --format "table {{.Names}}\t{{.Status}}"
    fi
else
    if [ "$USE_NATIVE" = true ]; then
        echo ""
        echo "Starting Ogmios and Kupo natively..."
        echo ""
        
        # Start Ogmios
        if [ "$OGMIOS_RUNNING" = false ]; then
            cd "$PROJECT_ROOT"
            nohup ogmios \
                --node-socket "$SOCKET_PATH" \
                --node-config "$CONFIG_DIR/config.json" \
                --host "0.0.0.0" \
                --port 1337 \
                > "$PROJECT_ROOT/ogmios.log" 2>&1 &
            OGMIOS_PID=$!
            echo "Ogmios starting (PID: $OGMIOS_PID)"
        fi
        
        # Start Kupo
        if [ "$KUPO_RUNNING" = false ]; then
            mkdir -p "$PROJECT_ROOT/kupo-preprod-db"
            cd "$PROJECT_ROOT"
            nohup kupo \
                --node-socket "$SOCKET_PATH" \
                --node-config "$CONFIG_DIR/config.json" \
                --workdir "$PROJECT_ROOT/kupo-preprod-db" \
                --host "0.0.0.0" \
                --port 1442 \
                --since "origin" \
                --match "*" \
                > "$PROJECT_ROOT/kupo.log" 2>&1 &
            KUPO_PID=$!
            echo "Kupo starting (PID: $KUPO_PID)"
        fi
        
        # Wait for services to start
        sleep 3
        
        # Check if services are healthy
        echo ""
        echo "Checking service health..."
        
        # Check Ogmios
        sleep 2
        if curl -s http://localhost:1337/health > /dev/null 2>&1; then
            echo "✓ Ogmios is responding"
        else
            echo "⚠ Ogmios may not be ready yet. Check logs: tail -f $PROJECT_ROOT/ogmios.log"
        fi
        
        # Check Kupo
        sleep 2
        if curl -s http://localhost:1442/health > /dev/null 2>&1; then
            echo "✓ Kupo is responding"
        else
            echo "⚠ Kupo may not be ready yet. Check logs: tail -f $PROJECT_ROOT/kupo.log"
        fi
    else
        echo ""
        echo "Starting Ogmios and Kupo via Docker..."
        
        # Detect macOS
        if [[ "$OSTYPE" == "darwin"* ]]; then
            echo ""
            echo "⚠ WARNING: On macOS, Docker has known issues with Unix domain sockets."
            echo "   If services fail to start, install Ogmios/Kupo natively:"
            echo ""
            echo "   Option 1 - Build from source (recommended):"
            echo "     See: docs/install-ogmios-kupo-macos.md"
            echo ""
            echo "   Option 2 - Try Homebrew:"
            echo "     brew tap cardanosolutions/cardano-services"
            echo "     brew install ogmios kupo"
            echo ""
            echo "   Option 3 - Try Nix (may not work):"
            echo "     nix-env -iA ogmios kupo -f https://github.com/NixOS/nixpkgs/archive/nixos-unstable.tar.gz"
            echo "     See: https://github.com/CardanoSolutions/ogmios"
            echo "     See: https://github.com/CardanoSolutions/kupo"
            echo ""
        fi
        
        cd "$PROJECT_ROOT"
        docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
        
        # Wait a bit for services to start
        sleep 3
        
        # Check status
        echo ""
        echo "Service status:"
        docker ps --filter "name=ogmios-preprod" --filter "name=kupo-preprod" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        
        # Check if services are healthy
        echo ""
        echo "Checking service health..."
        
        # Check Ogmios
        sleep 2
        if curl -s http://localhost:1337/health > /dev/null 2>&1; then
            echo "✓ Ogmios is responding"
        else
            echo "⚠ Ogmios may not be ready yet. Check logs: docker logs ogmios-preprod"
            if [[ "$OSTYPE" == "darwin"* ]]; then
                echo ""
                echo "   This is likely a macOS Docker socket issue."
                echo "   Consider installing Ogmios/Kupo natively (see instructions above)."
            fi
        fi
        
        # Check Kupo
        sleep 2
        if curl -s http://localhost:1442/health > /dev/null 2>&1; then
            echo "✓ Kupo is responding"
        else
            echo "⚠ Kupo may not be ready yet. Check logs: docker logs kupo-preprod"
            if [[ "$OSTYPE" == "darwin"* ]]; then
                echo ""
                echo "   This is likely a macOS Docker socket issue."
                echo "   Consider installing Ogmios/Kupo natively (see instructions above)."
            fi
        fi
    fi
fi

echo ""
echo "Services started!"
echo ""
echo "Ogmios: ws://localhost:1337"
echo "Kupo:   http://localhost:1442"
echo "Node:   $SOCKET_PATH"
echo ""
echo "To check logs:"
echo "  Node:   tail -f $LOG_FILE"
if [ "$USE_NATIVE" = true ]; then
    echo "  Ogmios: tail -f $PROJECT_ROOT/ogmios.log"
    echo "  Kupo:   tail -f $PROJECT_ROOT/kupo.log"
else
    echo "  Ogmios: docker logs -f ogmios-preprod"
    echo "  Kupo:   docker logs -f kupo-preprod"
fi
echo ""
echo "To stop services:"
if [ "$USE_NATIVE" = true ]; then
    echo "  pkill -f ogmios"
    echo "  pkill -f kupo"
else
    echo "  docker-compose -f $DOCKER_COMPOSE_FILE down"
fi
echo "  pkill -f cardano-node"

