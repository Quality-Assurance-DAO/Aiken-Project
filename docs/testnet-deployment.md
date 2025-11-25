# Testnet Deployment Guide

**Navigation**: [Home](../README.md) > [Documentation](./README.md) > Testnet Deployment

**Date**: 2025-01-27  
**Feature**: 001-milestone-token-distribution

## Overview

This guide provides step-by-step instructions for deploying the [milestone token distribution](./glossary.md#milestone-token-distribution) system to Cardano [testnet](./glossary.md#testnet).

## Prerequisites

- Aiken development environment installed
- [Cardano CLI](./glossary.md#cardano-cli) tools installed and configured (see `docs/cardano-cli-setup.md`)
- Access to Cardano [testnet](./glossary.md#testnet) node or API
- Testnet ADA for transaction fees
- Test signing keys for contract deployment

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
./scripts/mint_test_tokens.sh \
  --policy-id <your-policy-id> \
  --amount 10000000 \
  --testnet
```

### 3. Create Distribution Contract

```bash
aiken-distribution create \
  --allocations-file test-data/allocations.json \
  --oracles-file test-data/oracles.json \
  --quorum-threshold 3 \
  --token-policy-id <policy-id> \
  --output-datum contract-datum.json \
  --testnet
```

### 4. Deploy Contract

```bash
./scripts/deploy.sh testnet contract-datum.json <contract-address>
```

Or manually using Cardano CLI:

```bash
cardano-cli transaction build \
  --testnet-magic 1097911063 \
  --tx-in <utxo> \
  --tx-out <contract-address>+<amount>+"<tokens>" \
  --tx-out-datum-file contract-datum.json \
  --tx-out-datum-hash-file contract-datum.json \
  --change-address <your-address> \
  --out-file tx.unsigned

cardano-cli transaction sign \
  --tx-body-file tx.unsigned \
  --signing-key-file <key-file> \
  --testnet-magic 1097911063 \
  --out-file tx.signed

cardano-cli transaction submit \
  --tx-file tx.signed \
  --testnet-magic 1097911063
```

### 5. Verify Deployment

```bash
cardano-cli query utxo \
  --address <contract-address> \
  --testnet-magic 1097911063
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
aiken-distribution claim \
  --contract-address <address> \
  --beneficiary-index 0 \
  --milestone-verification-file test-data/verification.json \
  --signing-key-file beneficiary.skey \
  --testnet \
  --submit
```

## Monitoring

### Query Contract State

```bash
aiken-distribution query \
  --contract-address <address> \
  --testnet \
  --format json
```

### Check Transaction Status

```bash
cardano-cli query tx \
  --tx-id <transaction-hash> \
  --testnet-magic 1097911063
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

