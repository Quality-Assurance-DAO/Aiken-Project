#!/bin/bash
# Script to start Cardano node
# Default: preprod (development target)
# Usage: ./scripts/start_node.sh [preprod|preview|mainnet]
#   - No argument: starts preprod (default development network)
#   - preprod: Preprod testnet (default)
#   - preview: Preview testnet
#   - mainnet: Mainnet (production)

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
    ;;
  preview)
    CONFIG_DIR="$PROJECT_ROOT/share/preview"
    SOCKET_DIR="$PROJECT_ROOT/preview-socket"
    DB_DIR="$PROJECT_ROOT/db-preview"
    ;;
  mainnet)
    CONFIG_DIR="$PROJECT_ROOT/share/mainnet"
    SOCKET_DIR="$PROJECT_ROOT/mainnet-socket"
    DB_DIR="$PROJECT_ROOT/db-mainnet"
    ;;
  *)
    echo "Error: Unknown network: $NETWORK" >&2
    echo "Usage: $0 [preprod|preview|mainnet]" >&2
    exit 1
    ;;
esac

# Check if config directory exists
if [ ! -d "$CONFIG_DIR" ]; then
  echo "Error: Config directory not found: $CONFIG_DIR" >&2
  exit 1
fi

# Create socket directory if it doesn't exist
mkdir -p "$SOCKET_DIR"

# Create database directory if it doesn't exist
mkdir -p "$DB_DIR"

# Node executable path
NODE_BIN="$PROJECT_ROOT/bin/cardano-node"

if [ ! -f "$NODE_BIN" ]; then
  echo "Error: cardano-node not found at: $NODE_BIN" >&2
  exit 1
fi

# Change to config directory to use relative paths
cd "$CONFIG_DIR"

echo "Starting Cardano node for $NETWORK network..."
echo "Config directory: $CONFIG_DIR"
echo "Socket path: $SOCKET_DIR/node.socket"
echo "Database path: $DB_DIR"
echo ""

# Start the node
exec "$NODE_BIN" run \
  --config config.json \
  --topology topology.json \
  --database-path "$DB_DIR" \
  --socket-path "$SOCKET_DIR/node.socket" \
  --host-addr 0.0.0.0 \
  --port 3001

