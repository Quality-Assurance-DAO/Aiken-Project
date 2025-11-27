# Testnet Deployment Guide

**Navigation**: [Home](../README.md) > [Documentation](./README.md) > Testnet Deployment

**Date**: 2025-01-27  
**Feature**: 001-milestone-token-distribution

## Overview

This guide provides step-by-step instructions for deploying the [milestone token distribution](./glossary.md#milestone-token-distribution) system to Cardano [testnet](./glossary.md#testnet).

## Network Selection

This project supports two Cardano testnets:

- **Preprod** (NetworkMagic 1) - Stable testnet, recommended for production-like testing
- **Preview** (NetworkMagic 2) - Bleeding-edge testnet for testing latest features

Choose Preprod for stable testing or Preview for testing cutting-edge features. Both networks use test tokens (tADA) and have separate database directories to prevent conflicts.

## Prerequisites

- Aiken development environment installed
- [Cardano CLI](./glossary.md#cardano-cli) tools installed and configured (see `docs/cardano-cli-setup.md`)
- Access to Cardano [testnet](./glossary.md#testnet) node or API
- Testnet ADA for transaction fees
- Test signing keys for contract deployment

> **Note:** Set up your environment for the chosen network:
> ```bash
> # For Preprod
> source scripts/setup_env.sh preprod
> 
> # For Preview
> source scripts/setup_env.sh preview
> ```

## Testing Signing Keys

Before deploying contracts, verify that your signing keys work correctly. This prevents deployment failures and ensures you can sign transactions successfully.

> **Quick Start:** Use the automated helper script to test your keys:
> ```bash
> # For Preprod
> ./scripts/test_signing_keys.sh preprod payment.skey
> 
> # For Preview
> ./scripts/test_signing_keys.sh preview payment.skey
> ```
> 
> The script automates all verification steps below. For manual testing, continue with the steps below.

### 1. Verify Key Files Exist

Ensure your signing key files are present and readable:

```bash
# Check if payment signing key exists
ls -lh payment.skey

# Verify file permissions (should be readable by owner only)
ls -l payment.skey
# Expected: -rw------- (600 permissions)
```

**Security Note:** Signing keys should have restrictive permissions (600) to prevent unauthorized access. If permissions are too open, fix them:

```bash
chmod 600 payment.skey
```

### 2. Extract Verification Key

Extract the verification key from your signing key to verify it matches your address:

```bash
# Extract verification key from signing key
cardano-cli key verification-key \
  --signing-key-file payment.skey \
  --verification-key-file payment.vkey

# Verify the verification key was created
cat payment.vkey
```

The verification key should show a JSON structure with `type` and `description` fields.

### 3. Verify Address Matches

Ensure the address derived from your key matches what you expect:

```bash
# For Preprod (NetworkMagic 1)
cardano-cli address build \
  --payment-verification-key-file payment.vkey \
  --testnet-magic 1 \
  --out-file payment.addr

# For Preview (NetworkMagic 2)
cardano-cli address build \
  --payment-verification-key-file payment.vkey \
  --testnet-magic 2 \
  --out-file payment.addr

# Display the address
cat payment.addr
```

**Verify:**
- Address starts with `addr_test1` for testnet addresses
- Address matches the one you're using for deployment
- Address matches what you provided to faucets (if applicable)

### 4. Test Signing Capability (Dry Run)

Test that you can sign a transaction without submitting it to the network:

```bash
# First, get a UTXO from your address
# For Preprod (NetworkMagic 1)
cardano-cli query utxo \
  --address $(cat payment.addr) \
  --testnet-magic 1

# For Preview (NetworkMagic 2)
cardano-cli query utxo \
  --address $(cat payment.addr) \
  --testnet-magic 2
```

Create a test transaction that you'll sign but not submit:

```bash
# Build a test transaction (replace <utxo-hash> and <utxo-index> with actual values)
# For Preprod (NetworkMagic 1)
cardano-cli transaction build \
  --testnet-magic 1 \
  --tx-in <utxo-hash>#<utxo-index> \
  --tx-out $(cat payment.addr)+1000000 \
  --change-address $(cat payment.addr) \
  --out-file test-tx.unsigned

# For Preview (NetworkMagic 2)
cardano-cli transaction build \
  --testnet-magic 2 \
  --tx-in <utxo-hash>#<utxo-index> \
  --tx-out $(cat payment.addr)+1000000 \
  --change-address $(cat payment.addr) \
  --out-file test-tx.unsigned
```

Sign the transaction to verify your key works:

```bash
# Sign the transaction
# For Preprod (NetworkMagic 1)
cardano-cli transaction sign \
  --tx-body-file test-tx.unsigned \
  --signing-key-file payment.skey \
  --testnet-magic 1 \
  --out-file test-tx.signed

# For Preview (NetworkMagic 2)
cardano-cli transaction sign \
  --tx-body-file test-tx.unsigned \
  --signing-key-file payment.skey \
  --testnet-magic 2 \
  --out-file test-tx.signed
```

**Verify signing succeeded:**
- No error messages during signing
- `test-tx.signed` file was created
- File size is larger than the unsigned transaction

### 5. Verify Signature Validity

Check that the signed transaction is valid (without submitting it):

```bash
# Verify the transaction structure
cardano-cli transaction view \
  --tx-file test-tx.signed

# Check transaction witness (signature) is present
cardano-cli transaction view \
  --tx-file test-tx.signed | grep -i witness
```

**Expected output:** Should show witness information including the signature.

### 6. Test Transaction Validation (Optional)

For a more thorough test, validate the transaction body matches the signature:

```bash
# Extract transaction body from signed transaction
cardano-cli transaction txid \
  --tx-file test-tx.signed

# This should complete without errors, confirming the transaction structure is valid
```

### 7. Clean Up Test Files

After verifying your keys work, remove test transaction files:

```bash
rm -f test-tx.unsigned test-tx.signed
```

**Important:** Do NOT submit the test transaction (`test-tx.signed`) to the network. This is only for verifying your signing keys work.

### Troubleshooting Key Testing

**Error: "signing-key-file: openFile: does not exist"**
- Verify the key file path is correct
- Check file permissions (should be readable)
- Ensure you're in the correct directory

**Error: "SigningKeyDecodeError"**
- Key file may be corrupted or in wrong format
- Regenerate keys if necessary
- Verify key file is valid JSON

**Error: "AddressNotInUTxO"**
- The UTXO you're trying to use doesn't exist or was already spent
- Query UTXOs again to get current values
- Ensure you're querying the correct network

**Address mismatch**
- Verify you're using the correct network magic (1 for Preprod, 2 for Preview)
- Check that verification key matches signing key
- Regenerate address if needed

### Key Testing Checklist

Before deploying contracts, verify:

- [ ] Signing key file exists and is readable
- [ ] Verification key can be extracted from signing key
- [ ] Address derived from key matches expected address
- [ ] Can build a transaction successfully
- [ ] Can sign a transaction without errors
- [ ] Signed transaction has valid structure
- [ ] Key permissions are secure (600)

Once all checks pass, your signing keys are ready for contract deployment.

> **Tip:** The `scripts/test_signing_keys.sh` helper script automates all these checks. Run it before deployment to quickly verify your keys:
> ```bash
> ./scripts/test_signing_keys.sh preprod payment.skey
> ```

## Obtaining Testnet ADA (tADA)

To perform transactions on testnet, you need testnet ADA (tADA) for transaction fees. Here's how to obtain it:

### Preprod Testnet (NetworkMagic 1)

**Option 1: Cardano Testnet Faucet (Recommended)**
1. Visit the [Cardano Testnet Faucet](https://docs.cardano.org/cardano-testnet/tools/faucet)
2. Enter your testnet address (starts with `addr_test1...`)
3. Request tADA (typically 1000-10000 tADA per request)
4. Wait a few minutes for the transaction to confirm

**Option 2: IOG Testnet Faucet**
- Visit: https://testnets.cardano.org/en/testnets/cardano/tools/faucet/
- Enter your Preprod testnet address
- Complete any required verification
- Receive tADA within a few minutes

**Option 3: Community Faucets**
- Search for "Cardano Preprod faucet" for community-maintained options
- Always verify faucet URLs are legitimate before entering addresses

### Preview Testnet (NetworkMagic 2)

**Cardano Testnet Faucet**
1. Visit the [Cardano Testnet Faucet](https://docs.cardano.org/cardano-testnet/tools/faucet)
2. Select "Preview" network
3. Enter your Preview testnet address (starts with `addr_test1...`)
4. Request tADA

### Generating a Testnet Address

If you don't have a testnet address yet, create one:

```bash
# Generate a new payment key pair
cardano-cli address key-gen \
  --verification-key-file payment.vkey \
  --signing-key-file payment.skey

# Generate a testnet address (for Preprod)
cardano-cli address build \
  --payment-verification-key-file payment.vkey \
  --testnet-magic 1 \
  --out-file payment.addr

# Or for Preview
cardano-cli address build \
  --payment-verification-key-file payment.vkey \
  --testnet-magic 2 \
  --out-file payment.addr

# Display your address
cat payment.addr
```

### Verifying tADA Balance

After receiving tADA from a faucet, verify your balance:

```bash
# For Preprod (NetworkMagic 1)
cardano-cli query utxo \
  --address $(cat payment.addr) \
  --testnet-magic 1

# For Preview (NetworkMagic 2)
cardano-cli query utxo \
  --address $(cat payment.addr) \
  --testnet-magic 2
```

### Verifying Faucet Transactions

When a faucet sends you tADA, you'll receive a transaction hash. Here's how to verify the transaction:

#### Method 1: Using Cardano CLI (Command Line)

**Note:** Cardano CLI doesn't have a direct command to query transaction details by hash. Instead, verify transactions by checking UTXOs at the addresses involved.

**Check your address for the received UTXO:**

```bash
# For Preprod (NetworkMagic 1)
cardano-cli query utxo \
  --address addr_test1vrcdypxnqghpw336a3ygc7xsheeq7g506q7wtt00tvtu4hsjhkg43 \
  --testnet-magic 1

# For Preview (NetworkMagic 2)
cardano-cli query utxo \
  --address <your-address> \
  --testnet-magic 2
```

The output will show UTXOs at your address. Look for a new UTXO with the tADA amount you requested.

**Example output:**
```
                           TxHash                                 TxIx        Amount
--------------------------------------------------------------------------------------
d1cad836ac125a53ea525b9ef498a6b7b66ed9da007b8a10886d0ddccf1b89f3     0        1000000000 lovelace
```

Note: Amounts are shown in **lovelace** (1 ADA = 1,000,000 lovelace). So `1000000000 lovelace` = 1000 tADA.

#### Method 2: Using Block Explorers (Web Interface)

**Preprod Testnet Block Explorers:**
- **CardanoScan Preprod**: https://preprod.cardanoscan.io/transaction/<transaction-hash>
- **Cexplorer Preprod**: https://preprod.cexplorer.io/tx/<transaction-hash>

**Preview Testnet Block Explorers:**
- **CardanoScan Preview**: https://preview.cardanoscan.io/transaction/<transaction-hash>
- **Cexplorer Preview**: https://preview.cexplorer.io/tx/<transaction-hash>

**Example for your transaction:**
```
https://preprod.cardanoscan.io/transaction/d1cad836ac125a53ea525b9ef498a6b7b66ed9da007b8a10886d0ddccf1b89f3
```

On the block explorer, you can see:
- Transaction status (confirmed/pending)
- Inputs and outputs
- Transaction fees
- Block height and slot number
- Timestamp

#### What to Look For

When verifying a faucet transaction:
1. **Transaction Status**: Should show as "Confirmed" (not pending)
2. **Output Address**: Should match your testnet address
3. **Amount**: Should match the amount requested from the faucet
4. **Confirmations**: At least 1 confirmation means the transaction is on-chain

#### Troubleshooting Verification

**Transaction not found:**
- Wait a few minutes - transactions can take 1-5 minutes to appear
- Double-check the transaction hash is correct
- Ensure you're querying the correct network (Preprod vs Preview)

**Transaction shows as pending:**
- This is normal - wait for the next block (usually 20 seconds)
- Check again after 1-2 minutes

**No UTXO at your address:**
- Verify you're checking the correct address
- Ensure the transaction hash matches what the faucet provided
- Check that you're querying the correct network

### Tips

- **Transaction fees**: Simple transactions typically cost 0.17-0.2 tADA, complex smart contract transactions may cost 1-5 tADA
- **Request enough**: Request 1000-10000 tADA to have sufficient funds for multiple transactions
- **Rate limits**: Most faucets have rate limits (e.g., once per hour or day)
- **Keep keys safe**: Store your `payment.skey` file securely - losing it means losing access to your testnet funds

## Step-by-Step Deployment

### 1. Prepare Test Data

Create `test-data/allocations.json`:
```json
{
  "allocations": [
    {
      "beneficiary_address": "addr_test1...",
      "token_amount": 1000000,
      "milestone_identifier": "milestone-001",
      "vesting_timestamp": 1735689600
    }
  ]
}
```

Create `test-data/oracles.json`:
```json
{
  "oracle_addresses": [
    "addr_test1...",
    "addr_test2...",
    "addr_test3..."
  ]
}
```

### 2. Mint Test Tokens

```bash
# For Preprod (NetworkMagic 1)
./scripts/mint_test_tokens.sh \
  --policy-id <your-policy-id> \
  --amount 10000000 \
  --testnet-magic 1

# For Preview (NetworkMagic 2)
./scripts/mint_test_tokens.sh \
  --policy-id <your-policy-id> \
  --amount 10000000 \
  --testnet-magic 2
```

### 3. Create Distribution Contract

```bash
# For Preprod (NetworkMagic 1)
aiken-distribution create \
  --allocations-file test-data/allocations.json \
  --oracles-file test-data/oracles.json \
  --quorum-threshold 3 \
  --token-policy-id <policy-id> \
  --output-datum contract-datum.json \
  --testnet-magic 1

# For Preview (NetworkMagic 2)
aiken-distribution create \
  --allocations-file test-data/allocations.json \
  --oracles-file test-data/oracles.json \
  --quorum-threshold 3 \
  --token-policy-id <policy-id> \
  --output-datum contract-datum.json \
  --testnet-magic 2
```

### 4. Deploy Contract

```bash
# For Preprod
./scripts/deploy.sh preprod contract-datum.json <contract-address>

# For Preview
./scripts/deploy.sh preview contract-datum.json <contract-address>
```

Or manually using Cardano CLI:

```bash
# For Preprod (NetworkMagic 1)
cardano-cli transaction build \
  --testnet-magic 1 \
  --tx-in <utxo> \
  --tx-out <contract-address>+<amount>+"<tokens>" \
  --tx-out-datum-file contract-datum.json \
  --tx-out-datum-hash-file contract-datum.json \
  --change-address <your-address> \
  --out-file tx.unsigned

cardano-cli transaction sign \
  --tx-body-file tx.unsigned \
  --signing-key-file <key-file> \
  --testnet-magic 1 \
  --out-file tx.signed

cardano-cli transaction submit \
  --tx-file tx.signed \
  --testnet-magic 1

# For Preview (NetworkMagic 2) - replace --testnet-magic 1 with --testnet-magic 2
```

### 5. Verify Deployment

```bash
# For Preprod (NetworkMagic 1)
cardano-cli query utxo \
  --address <contract-address> \
  --testnet-magic 1

# For Preview (NetworkMagic 2)
cardano-cli query utxo \
  --address <contract-address> \
  --testnet-magic 2
```

### 6. Simulate Oracle Signatures

```bash
./scripts/simulate_oracles.sh \
  milestone-001 \
  test-data/oracles.json \
  test-data/oracle-keys \
  test-data/verification.json
```

### 7. Test Claim Transaction

```bash
# For Preprod (NetworkMagic 1)
aiken-distribution claim \
  --contract-address <address> \
  --beneficiary-index 0 \
  --milestone-verification-file test-data/verification.json \
  --signing-key-file beneficiary.skey \
  --testnet-magic 1 \
  --submit

# For Preview (NetworkMagic 2)
aiken-distribution claim \
  --contract-address <address> \
  --beneficiary-index 0 \
  --milestone-verification-file test-data/verification.json \
  --signing-key-file beneficiary.skey \
  --testnet-magic 2 \
  --submit
```

## Monitoring

### Query Contract State

```bash
# For Preprod (NetworkMagic 1)
aiken-distribution query \
  --contract-address <address> \
  --testnet-magic 1 \
  --format json

# For Preview (NetworkMagic 2)
aiken-distribution query \
  --contract-address <address> \
  --testnet-magic 2 \
  --format json
```

### Check Transaction Status

**Note:** Cardano CLI doesn't support querying transactions directly by hash. Use block explorers for detailed transaction information, or verify transactions by checking UTXOs.

**Using Block Explorers:**

- **Preprod**: https://preprod.cardanoscan.io/transaction/<transaction-hash>
- **Preview**: https://preview.cardanoscan.io/transaction/<transaction-hash>

**Understanding Transaction Status:**
- **Confirmed**: Transaction is on-chain and final
- **Pending**: Transaction is submitted but not yet in a block (wait 20-60 seconds)
- **Not Found**: Transaction hash is invalid or transaction hasn't been submitted yet

**Check UTXO after transaction:**
```bash
# Verify funds were received/sent
cardano-cli query utxo \
  --address <your-address> \
  --testnet-magic 1  # or 2 for Preview
```

## Troubleshooting

### Transaction Size Too Large
- Reduce number of beneficiary allocations per contract
- Optimize datum structure
- Use compressed encoding for oracle signatures

### Execution Budget Exceeded
- Optimize validator logic
- Reduce quorum verification complexity
- Test execution units on testnet first

### Invalid Oracle Signatures
- Verify signatures off-chain before submission
- Use `verify-milestone` command to check
- Ensure oracle addresses match authorized set

### Vesting Timestamp Not Met
- Check current slot/time on testnet
- Verify vesting timestamp is in POSIXTime format
- Wait for vesting period to start

## Next Steps

After successful testnet deployment:
1. Test all user stories and scenarios
2. Monitor execution budget and transaction fees
3. Verify all acceptance criteria are met
4. Prepare for mainnet migration (see mainnet-migration.md)

