#!/bin/bash
# Script to set up environment variables for Cardano node
# Usage: source scripts/setup_env.sh [preprod|preview|mainnet]

NETWORK="${1:-preprod}"

# Get the project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Network-specific configuration
case "$NETWORK" in
  preprod)
    SOCKET_PATH="$PROJECT_ROOT/preprod-socket/node.socket"
    MAGIC="--testnet-magic 1"
    ;;
  preview)
    SOCKET_PATH="$PROJECT_ROOT/preview-socket/node.socket"
    MAGIC="--testnet-magic 2"
    ;;
  mainnet)
    SOCKET_PATH="$PROJECT_ROOT/mainnet-socket/node.socket"
    MAGIC="--mainnet"
    ;;
  *)
    echo "Error: Unknown network: $NETWORK" >&2
    echo "Usage: source $0 [preprod|preview|mainnet]" >&2
    return 1 2>/dev/null || exit 1
    ;;
esac

export CARDANO_NODE_SOCKET_PATH="$SOCKET_PATH"
export CARDANO_NETWORK="$NETWORK"
export CARDANO_MAGIC="$MAGIC"

# Add bin directory to PATH if not already present
BIN_DIR="$PROJECT_ROOT/bin"
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
  export PATH="$BIN_DIR:$PATH"
fi

echo "Environment variables set for $NETWORK network:"
echo "  CARDANO_NODE_SOCKET_PATH=$CARDANO_NODE_SOCKET_PATH"
echo "  CARDANO_NETWORK=$CARDANO_NETWORK"
echo "  CARDANO_MAGIC=$CARDANO_MAGIC"
echo "  PATH updated to include: $BIN_DIR"

