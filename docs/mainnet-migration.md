# Mainnet Migration Checklist

**Date**: 2025-01-27  
**Feature**: 001-milestone-token-distribution

## Overview

This checklist provides steps for migrating the milestone-based token distribution system from testnet to mainnet.

## Pre-Migration Checklist

- [ ] All testnet tests pass successfully
- [ ] Execution budget verified within limits (<10M CPU, <10M memory)
- [ ] Transaction size verified within limits (~16KB)
- [ ] All user stories tested and validated
- [ ] Security audit completed
- [ ] Oracle infrastructure ready for mainnet

## Configuration Changes

### 1. Replace Testnet Values

- [ ] **Oracle Addresses**: Replace testnet oracle addresses with mainnet addresses
  - Update `test-data/oracles.json` with mainnet addresses
  - Verify all oracle addresses are valid mainnet addresses

- [ ] **Token Policy ID**: Replace test token policy ID with production policy ID
  - Update contract creation scripts
  - Verify policy ID is correct for mainnet

- [ ] **Network Configuration**: Update all scripts to use mainnet
  - Change `--testnet-magic` to `--mainnet` in all scripts
  - Update Cardano CLI commands

### 2. Update Contract Parameters

- [ ] **Quorum Threshold**: Verify quorum threshold is appropriate for mainnet
- [ ] **Vesting Timestamps**: Update vesting timestamps to mainnet time
- [ ] **Contract Metadata**: Update contract version and description

### 3. Security Verification

- [ ] **Oracle Keys**: Ensure mainnet oracle signing keys are secure
- [ ] **Contract Address**: Verify contract address is correct
- [ ] **Token Amounts**: Double-check all token amounts are correct
- [ ] **Beneficiary Addresses**: Verify all beneficiary addresses are valid mainnet addresses

## Migration Steps

### Step 1: Prepare Mainnet Configuration

```bash
# Create mainnet configuration
cp test-data/oracles.json mainnet-data/oracles.json
# Update with mainnet oracle addresses

cp test-data/allocations.json mainnet-data/allocations.json
# Update with mainnet beneficiary addresses and timestamps
```

### Step 2: Build Mainnet Contract

```bash
aiken build
# Verify build succeeds without errors
```

### Step 3: Deploy to Mainnet

```bash
# Create contract datum
aiken-distribution create \
  --allocations-file mainnet-data/allocations.json \
  --oracles-file mainnet-data/oracles.json \
  --quorum-threshold 3 \
  --token-policy-id <mainnet-policy-id> \
  --output-datum mainnet-contract-datum.json \
  --mainnet

# Deploy contract
./scripts/deploy.sh mainnet mainnet-contract-datum.json <contract-address>
```

### Step 4: Verify Deployment

```bash
# Query contract state
aiken-distribution query \
  --contract-address <address> \
  --mainnet \
  --format json

# Verify UTXO
cardano-cli query utxo \
  --address <contract-address> \
  --mainnet
```

### Step 5: Test First Claim

- [ ] Verify milestone with mainnet oracles
- [ ] Submit test claim transaction
- [ ] Verify tokens transfer correctly
- [ ] Verify datum updates correctly

## Post-Migration Verification

- [ ] All allocations created correctly
- [ ] Oracle addresses verified
- [ ] Quorum threshold working
- [ ] Vesting timestamps correct
- [ ] Token amounts correct
- [ ] Contract address verified
- [ ] First claim transaction successful

## Rollback Plan

If issues are discovered:

1. **Stop all claim transactions**
2. **Document the issue**
3. **Revert to testnet for testing**
4. **Fix the issue**
5. **Re-deploy after verification**

## Monitoring

After mainnet deployment:

- [ ] Monitor transaction fees
- [ ] Monitor execution budget usage
- [ ] Monitor contract UTXO state
- [ ] Monitor claim transaction success rate
- [ ] Monitor oracle signature verification

## Support

For issues during migration:
- Check transaction logs
- Verify contract state
- Review validator logs
- Consult Cardano documentation


