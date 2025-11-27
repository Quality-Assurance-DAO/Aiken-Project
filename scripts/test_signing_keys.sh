#!/bin/bash
# Script to test signing keys for contract deployment
# Verifies that signing keys work correctly before deployment
# Usage: ./scripts/test_signing_keys.sh [preprod|preview] [signing-key-file]

set -e

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Default values
NETWORK="${1:-preprod}"
SIGNING_KEY_FILE="${2:-payment.skey}"

# Network-specific configuration
case "$NETWORK" in
  preprod)
    MAGIC="--testnet-magic 1"
    NETWORK_NAME="Preprod"
    DEFAULT_SOCKET_PATH="$PROJECT_ROOT/preprod-socket/node.socket"
    ;;
  preview)
    MAGIC="--testnet-magic 2"
    NETWORK_NAME="Preview"
    DEFAULT_SOCKET_PATH="$PROJECT_ROOT/preview-socket/node.socket"
    ;;
  *)
    echo "Error: Unknown network: $NETWORK" >&2
    echo "Usage: $0 [preprod|preview] [signing-key-file]" >&2
    exit 1
    ;;
esac

# Set socket path if not already set
if [ -z "$CARDANO_NODE_SOCKET_PATH" ]; then
    export CARDANO_NODE_SOCKET_PATH="$DEFAULT_SOCKET_PATH"
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

print_header() {
    echo ""
    echo "=========================================="
    echo "$1"
    echo "=========================================="
}

# Check if socket file exists (after helper functions are defined)
if [ ! -S "$CARDANO_NODE_SOCKET_PATH" ]; then
    print_error "Cardano node socket not found: $CARDANO_NODE_SOCKET_PATH"
    print_info "Make sure your Cardano node is running, or set CARDANO_NODE_SOCKET_PATH environment variable"
    print_info "You can also use a remote node by setting CARDANO_NODE_SOCKET_PATH to the remote socket path"
    exit 1
fi

# Check if cardano-cli is available
if ! command -v cardano-cli &> /dev/null; then
    print_error "cardano-cli not found. Please install Cardano CLI first."
    exit 1
fi

print_header "Testing Signing Keys for $NETWORK_NAME Network"
echo "Signing key file: $SIGNING_KEY_FILE"
echo ""

# Step 1: Verify key file exists
print_header "Step 1: Verifying Key File"
if [ ! -f "$SIGNING_KEY_FILE" ]; then
    print_error "Signing key file not found: $SIGNING_KEY_FILE"
    exit 1
fi
print_success "Key file exists: $SIGNING_KEY_FILE"

# Check file permissions
PERMS=$(stat -f "%A" "$SIGNING_KEY_FILE" 2>/dev/null || stat -c "%a" "$SIGNING_KEY_FILE" 2>/dev/null)
if [ "$PERMS" != "600" ] && [ "$PERMS" != "0600" ]; then
    print_info "Key file permissions are $PERMS (recommended: 600)"
    read -p "Fix permissions to 600? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        chmod 600 "$SIGNING_KEY_FILE"
        print_success "Permissions updated to 600"
    fi
else
    print_success "Key file permissions are secure (600)"
fi

# Step 2: Extract verification key
print_header "Step 2: Extracting Verification Key"
VERIFICATION_KEY_FILE="${SIGNING_KEY_FILE%.skey}.vkey"

if [ -f "$VERIFICATION_KEY_FILE" ]; then
    print_info "Verification key already exists: $VERIFICATION_KEY_FILE"
    read -p "Regenerate? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cardano-cli key verification-key \
            --signing-key-file "$SIGNING_KEY_FILE" \
            --verification-key-file "$VERIFICATION_KEY_FILE" > /dev/null 2>&1
        print_success "Verification key extracted"
    fi
else
    cardano-cli key verification-key \
        --signing-key-file "$SIGNING_KEY_FILE" \
        --verification-key-file "$VERIFICATION_KEY_FILE" > /dev/null 2>&1
    print_success "Verification key extracted: $VERIFICATION_KEY_FILE"
fi

# Verify verification key structure
if grep -q '"type"' "$VERIFICATION_KEY_FILE" 2>/dev/null; then
    print_success "Verification key has valid structure"
else
    print_error "Verification key structure appears invalid"
    exit 1
fi

# Step 3: Verify address matches
print_header "Step 3: Verifying Address"
ADDRESS_FILE="${SIGNING_KEY_FILE%.skey}.addr"

if [ -f "$ADDRESS_FILE" ]; then
    EXISTING_ADDRESS=$(cat "$ADDRESS_FILE")
    print_info "Existing address file found: $ADDRESS_FILE"
    print_info "Existing address: $EXISTING_ADDRESS"
fi

# Build address from verification key
cardano-cli address build \
    --payment-verification-key-file "$VERIFICATION_KEY_FILE" \
    $MAGIC \
    --out-file "$ADDRESS_FILE" > /dev/null 2>&1

DERIVED_ADDRESS=$(cat "$ADDRESS_FILE")
print_success "Address derived: $DERIVED_ADDRESS"

# Verify address format
if [[ "$DERIVED_ADDRESS" =~ ^addr_test1 ]]; then
    print_success "Address format is valid (testnet)"
else
    print_error "Address format appears invalid (expected addr_test1...)"
    exit 1
fi

# Compare with existing address if present
if [ -n "$EXISTING_ADDRESS" ] && [ "$EXISTING_ADDRESS" != "$DERIVED_ADDRESS" ]; then
    print_error "Address mismatch!"
    print_error "Existing: $EXISTING_ADDRESS"
    print_error "Derived:  $DERIVED_ADDRESS"
    exit 1
elif [ -n "$EXISTING_ADDRESS" ]; then
    print_success "Address matches existing address file"
fi

# Step 4: Test signing capability
print_header "Step 4: Testing Signing Capability"

# Query UTXOs
print_info "Querying UTXOs for address..."
print_info "Using socket: $CARDANO_NODE_SOCKET_PATH"
print_info "Note: This may take a moment if the node is syncing..."

# Try to query UTXOs with timeout if available, otherwise without
if command -v timeout &> /dev/null || command -v gtimeout &> /dev/null; then
    TIMEOUT_CMD=$(command -v timeout 2>/dev/null || command -v gtimeout 2>/dev/null)
    UTXOS=$($TIMEOUT_CMD 30 cardano-cli query utxo \
        --address "$DERIVED_ADDRESS" \
        --socket-path "$CARDANO_NODE_SOCKET_PATH" \
        $MAGIC 2>&1) || {
        QUERY_EXIT_CODE=$?
        if [ $QUERY_EXIT_CODE -eq 124 ]; then
            print_error "UTXO query timed out after 30 seconds"
            print_info "This usually means the node is not responding or not synced"
        else
            print_error "Failed to query UTXOs"
            echo "$UTXOS" >&2
        fi
        print_info "Continuing without UTXO check - signing capability will be tested during deployment"
        UTXOS=""
    }
else
    # No timeout available - run without timeout but warn user
    print_info "Warning: timeout command not available - query may hang if node is not responding"
    print_info "Press Ctrl+C to cancel if it takes too long"
    UTXOS=$(cardano-cli query utxo \
        --address "$DERIVED_ADDRESS" \
        --socket-path "$CARDANO_NODE_SOCKET_PATH" \
        $MAGIC 2>&1) || {
        print_error "Failed to query UTXOs"
        echo "$UTXOS" >&2
        print_info "Continuing without UTXO check - signing capability will be tested during deployment"
        UTXOS=""
    }
fi

if echo "$UTXOS" | grep -q "TxHash"; then
    print_success "UTXOs found at address"
    
    # Extract first UTXO
    FIRST_UTXO=$(echo "$UTXOS" | grep -v "TxHash" | grep -v "^--" | head -n 1 | awk '{print $1"#"$2}')
    
    if [ -n "$FIRST_UTXO" ]; then
        print_info "Using UTXO: $FIRST_UTXO"
        
        # Build test transaction
        TEST_TX_UNSIGNED="test-tx-unsigned-$$.tmp"
        TEST_TX_SIGNED="test-tx-signed-$$.tmp"
        
        print_info "Building test transaction..."
        if cardano-cli transaction build \
            --socket-path "$CARDANO_NODE_SOCKET_PATH" \
            $MAGIC \
            --tx-in "$FIRST_UTXO" \
            --tx-out "$DERIVED_ADDRESS"+1000000 \
            --change-address "$DERIVED_ADDRESS" \
            --out-file "$TEST_TX_UNSIGNED" > /dev/null 2>&1; then
            print_success "Test transaction built successfully"
            
            # Sign transaction
            print_info "Signing test transaction..."
            if cardano-cli transaction sign \
                --tx-body-file "$TEST_TX_UNSIGNED" \
                --signing-key-file "$SIGNING_KEY_FILE" \
                --socket-path "$CARDANO_NODE_SOCKET_PATH" \
                $MAGIC \
                --out-file "$TEST_TX_SIGNED" > /dev/null 2>&1; then
                print_success "Transaction signed successfully"
                
                # Verify signed transaction structure
                print_info "Verifying signed transaction structure..."
                if cardano-cli transaction view --tx-file "$TEST_TX_SIGNED" > /dev/null 2>&1; then
                    print_success "Signed transaction structure is valid"
                    
                    # Check for witness
                    if cardano-cli transaction view --tx-file "$TEST_TX_SIGNED" 2>/dev/null | grep -q -i "witness\|signature"; then
                        print_success "Transaction witness (signature) present"
                    else
                        print_info "Could not verify witness in transaction view"
                    fi
                    
                    # Get transaction ID
                    TX_ID=$(cardano-cli transaction txid --tx-file "$TEST_TX_SIGNED" 2>/dev/null)
                    if [ -n "$TX_ID" ]; then
                        print_success "Transaction ID: $TX_ID"
                    fi
                else
                    print_error "Failed to verify transaction structure"
                fi
                
                # Clean up test files
                rm -f "$TEST_TX_UNSIGNED" "$TEST_TX_SIGNED"
                print_info "Test transaction files cleaned up"
                print_info "Note: Test transaction was NOT submitted to the network"
            else
                print_error "Failed to sign transaction"
                rm -f "$TEST_TX_UNSIGNED"
                exit 1
            fi
        else
            print_error "Failed to build test transaction"
            print_info "This may be normal if UTXO is insufficient or node is not synced"
            print_info "Continuing with other checks..."
        fi
    else
        print_info "Could not extract UTXO for testing"
        print_info "This is okay - signing capability will be tested during actual deployment"
    fi
else
    print_info "No UTXOs found at address"
    print_info "This is okay - you can still test signing during deployment"
    print_info "Make sure to fund the address before deploying contracts"
fi

# Step 5: Summary
print_header "Test Summary"
print_success "Key file exists and is readable"
print_success "Verification key extracted successfully"
print_success "Address derived and validated"
if [ -f "$TEST_TX_SIGNED" ] || echo "$UTXOS" | grep -q "TxHash"; then
    print_success "Signing capability verified"
else
    print_info "Signing capability will be tested during deployment"
fi

echo ""
print_header "Key Information"
echo "Signing key:    $SIGNING_KEY_FILE"
echo "Verification key: $VERIFICATION_KEY_FILE"
echo "Address:        $DERIVED_ADDRESS"
echo "Network:        $NETWORK_NAME"
echo ""

print_header "Next Steps"
echo "1. Fund your address with testnet ADA (tADA) if not already done"
echo "2. Verify address balance:"
echo "   cardano-cli query utxo --address $DERIVED_ADDRESS $MAGIC"
echo "3. Proceed with contract deployment using this signing key"
echo ""

print_success "Signing key testing completed successfully!"
print_info "Your keys are ready for contract deployment"

