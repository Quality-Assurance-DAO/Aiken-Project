# CLI Interface Specification

**Date**: 2025-01-27  
**Feature**: 001-milestone-token-distribution

## Overview

This document specifies the command-line interface for interacting with the milestone-based token distribution system. The CLI provides commands for contract creation, claim transactions, and utility operations.

## Command Structure

All commands follow the pattern:
```bash
aiken-distribution <command> [options] [arguments]
```

## Commands

### 1. Create Distribution Contract

**Command**: `create`

**Purpose**: Create a new distribution contract with beneficiary allocations.

**Usage**:
```bash
aiken-distribution create \
  --allocations-file <path> \
  --oracles-file <path> \
  --quorum-threshold <N> \
  --token-policy-id <policy-id> \
  --output-datum <path> \
  [--metadata-file <path>]
```

**Arguments**:
- `--allocations-file`: JSON file containing beneficiary allocations (see format below)
- `--oracles-file`: JSON file containing list of authorized oracle addresses
- `--quorum-threshold`: Minimum number of oracle signatures required (integer)
- `--token-policy-id`: Policy ID of tokens to distribute (hex string)
- `--output-datum`: Path to write the generated datum JSON
- `--metadata-file`: Optional JSON file with contract metadata

**Allocations File Format** (`allocations.json`):
```json
{
  "allocations": [
    {
      "beneficiary_address": "addr_test1...",
      "token_amount": 1000000,
      "milestone_identifier": "milestone-001",
      "vesting_timestamp": 1735689600
    },
    {
      "beneficiary_address": "addr_test1...",
      "token_amount": 2000000,
      "milestone_identifier": "milestone-002",
      "vesting_timestamp": 1735776000
    }
  ]
}
```

**Oracles File Format** (`oracles.json`):
```json
{
  "oracle_addresses": [
    "addr_test1...",
    "addr_test1...",
    "addr_test1..."
  ]
}
```

**Output**: 
- Generates datum JSON file
- Prints contract address and total token amount
- Validates all inputs before generation

**Validation**:
- All beneficiary addresses must be valid Cardano addresses
- Token amounts must be > 0
- Vesting timestamps must be in the future
- Quorum threshold must be <= number of oracles
- Total token amount calculated and validated

---

### 2. Claim Tokens

**Command**: `claim`

**Purpose**: Construct and submit a claim transaction for a beneficiary.

**Usage**:
```bash
aiken-distribution claim \
  --contract-address <address> \
  --beneficiary-index <index> \
  --milestone-verification-file <path> \
  --signing-key-file <path> \
  [--testnet] \
  [--submit]
```

**Arguments**:
- `--contract-address`: Address of the distribution contract UTXO
- `--beneficiary-index`: Index of beneficiary allocation (0-based)
- `--milestone-verification-file`: JSON file with milestone verification data
- `--signing-key-file`: Path to beneficiary's signing key file
- `--testnet`: Use testnet (default: mainnet)
- `--submit`: Submit transaction to network (default: build only)

**Milestone Verification File Format** (`verification.json`):
```json
{
  "milestone_identifier": "milestone-001",
  "oracle_signatures": [
    {
      "oracle_address": "addr_test1...",
      "signature_hash": "abc123...",
      "signed_data": "milestone-001|1735689600",
      "signature_timestamp": 1735689600
    },
    {
      "oracle_address": "addr_test1...",
      "signature_hash": "def456...",
      "signed_data": "milestone-001|1735689600",
      "signature_timestamp": 1735689600
    }
  ],
  "verification_timestamp": 1735689600
}
```

**Output**:
- Builds transaction using Cardano CLI
- Prints transaction details (fees, outputs, etc.)
- If `--submit`: Submits transaction and prints transaction hash
- If not `--submit`: Saves transaction file for manual submission

**Validation**:
- Verifies milestone identifier matches allocation
- Checks quorum threshold is met
- Validates oracle signatures (off-chain verification)
- Ensures vesting timestamp has passed
- Confirms allocation not already claimed

---

### 3. Verify Milestone

**Command**: `verify-milestone`

**Purpose**: Verify oracle signatures for a milestone (off-chain verification before claim).

**Usage**:
```bash
aiken-distribution verify-milestone \
  --milestone-verification-file <path> \
  --oracles-file <path> \
  --quorum-threshold <N>
```

**Arguments**:
- `--milestone-verification-file`: JSON file with milestone verification data
- `--oracles-file`: JSON file with authorized oracle addresses
- `--quorum-threshold`: Minimum signatures required

**Output**:
- Prints verification status (PASS/FAIL)
- Lists valid signatures found
- Lists invalid/unauthorized signatures
- Shows quorum status (X of Y signatures, threshold: N)

**Use Case**: Verify signatures before constructing claim transaction to avoid failed transactions.

---

### 4. Query Contract State

**Command**: `query`

**Purpose**: Query the current state of a distribution contract.

**Usage**:
```bash
aiken-distribution query \
  --contract-address <address> \
  [--testnet] \
  [--format json|human]
```

**Arguments**:
- `--contract-address`: Address of the distribution contract
- `--testnet`: Use testnet (default: mainnet)
- `--format`: Output format (default: human-readable)

**Output**:
- Contract datum (all allocations, claimed status)
- Total tokens remaining
- Number of claimed vs unclaimed allocations
- Oracle addresses and quorum threshold
- Contract metadata

**Format Examples**:

Human-readable:
```
Distribution Contract: addr_test1...
Total Tokens: 10,000,000
Remaining: 7,500,000
Allocations: 10 total, 3 claimed, 7 unclaimed
Quorum: 3 of 5 oracles required
```

JSON:
```json
{
  "contract_address": "addr_test1...",
  "total_token_amount": 10000000,
  "remaining_tokens": 7500000,
  "allocations": {
    "total": 10,
    "claimed": 3,
    "unclaimed": 7
  },
  "quorum": {
    "threshold": 3,
    "total_oracles": 5
  }
}
```

---

### 5. Simulate Oracle Signatures (Testnet)

**Command**: `simulate-oracles`

**Purpose**: Generate simulated oracle signatures for testing (testnet only).

**Usage**:
```bash
aiken-distribution simulate-oracles \
  --milestone-id <id> \
  --oracles-file <path> \
  --signing-keys-dir <path> \
  --output-file <path>
```

**Arguments**:
- `--milestone-id`: Milestone identifier to sign
- `--oracles-file`: JSON file with oracle addresses
- `--signing-keys-dir`: Directory containing test signing keys for oracles
- `--output-file`: Path to write verification JSON file

**Output**:
- Generates milestone verification JSON with simulated signatures
- Uses test keys to create Ed25519 signatures
- Includes all oracles (or subset if specified)

**Use Case**: Testing milestone verification and claim transactions on testnet.

---

## Error Handling

All commands return:
- **Exit Code 0**: Success
- **Exit Code 1**: Validation error (invalid input, missing files, etc.)
- **Exit Code 2**: Network error (connection failed, transaction rejected, etc.)
- **Exit Code 3**: Internal error (unexpected failure)

Error messages are written to `stderr` in human-readable format.

## Configuration

Default configuration file: `~/.aiken-distribution/config.json`

```json
{
  "default_network": "testnet",
  "cardano_cli_path": "cardano-cli",
  "testnet_magic": 1097911063,
  "default_output_format": "human"
}
```

## Examples

### Create Contract
```bash
aiken-distribution create \
  --allocations-file allocations.json \
  --oracles-file oracles.json \
  --quorum-threshold 3 \
  --token-policy-id abc123... \
  --output-datum contract-datum.json
```

### Claim Tokens
```bash
aiken-distribution claim \
  --contract-address addr_test1... \
  --beneficiary-index 0 \
  --milestone-verification-file verification.json \
  --signing-key-file beneficiary.skey \
  --testnet \
  --submit
```

### Query State
```bash
aiken-distribution query \
  --contract-address addr_test1... \
  --testnet \
  --format json
```

## Implementation Notes

- Commands wrap Cardano CLI for transaction building
- Use Aiken's transaction building utilities where available
- Support both testnet and mainnet
- Provide helpful error messages for common issues
- Validate inputs before network interaction


