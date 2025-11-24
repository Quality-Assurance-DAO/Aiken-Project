# Quickstart Guide: Milestone-Based Token Distribution System

**Date**: 2025-01-27  
**Feature**: 001-milestone-token-distribution

## Prerequisites

- Aiken development environment installed
- Cardano CLI tools installed and configured
- Access to Cardano testnet (or local testnet node)
- Basic understanding of Cardano UTXO model and smart contracts

## Installation

### 1. Install Aiken

```bash
# Install Aiken via cargo (recommended)
cargo install aiken

# Or via npm
npm install -g aiken-lang

# Verify installation
aiken --version
```

### 2. Install Cardano CLI

```bash
# Follow official Cardano documentation
# https://developers.cardano.org/docs/get-started/installing-cardano-node

# Verify installation
cardano-cli --version
```

### 3. Setup Project

```bash
# Clone or navigate to project directory
cd /path/to/Aiken-Project

# Initialize Aiken project (if not already done)
aiken init

# Build the project
aiken build
```

## Project Structure

```
src/
├── validator/          # On-chain validator logic
├── cli/                # CLI command implementations
└── lib/                # Shared utilities

tests/
├── validator/          # Validator unit tests
├── integration/        # End-to-end tests
└── unit/               # Unit tests
```

## Quick Test

### 1. Run Unit Tests

```bash
# Run all tests
aiken test

# Run specific test file
aiken test tests/validator/validator_test.aiken
```

### 2. Build Validator

```bash
# Build validator script
aiken build

# Output will be in build/ directory
```

## Development Workflow

### 1. Write Tests First (TDD)

```aiken
// tests/validator/validator_test.aiken
use aiken

test "beneficiary can claim tokens after vesting" {
  // Write test that fails
  // Then implement validator logic
  // Verify test passes
}
```

### 2. Implement Validator Logic

```aiken
// src/contract/lib.aiken
validator {
  fn validate(datum: DistributionContract, redeemer: ClaimRedeemer, context: ScriptContext) -> Bool {
    // Implementation here
  }
}
```

### 3. Test Iteratively

```bash
# Run tests after each change
aiken test

# Build and check for errors
aiken build
```

## Testnet Deployment

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
    "addr_test1...",
    "addr_test1..."
  ]
}
```

### 2. Mint Test Tokens

```bash
# Use scripts/mint_test_tokens.sh
./scripts/mint_test_tokens.sh \
  --policy-id <policy-id> \
  --amount 10000000 \
  --testnet
```

### 3. Create Distribution Contract

```bash
# Use CLI create command
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
# Build transaction to lock tokens in contract
cardano-cli transaction build \
  --testnet-magic 1097911063 \
  --tx-in <utxo> \
  --tx-out <contract-address>+<amount>+"<tokens>" \
  --tx-out-datum-file contract-datum.json \
  --tx-out-datum-hash-file contract-datum.json \
  --change-address <your-address> \
  --out-file tx.unsigned

# Sign and submit
cardano-cli transaction sign \
  --tx-body-file tx.unsigned \
  --signing-key-file <key-file> \
  --testnet-magic 1097911063 \
  --out-file tx.signed

cardano-cli transaction submit \
  --tx-file tx.signed \
  --testnet-magic 1097911063
```

## Testing Scenarios

### Scenario 1: Valid Claim

1. Create contract with beneficiary allocation
2. Wait for vesting timestamp to pass
3. Collect oracle signatures (simulate on testnet)
4. Submit claim transaction
5. Verify tokens transferred to beneficiary

**Test Command**:
```bash
aiken-distribution claim \
  --contract-address <address> \
  --beneficiary-index 0 \
  --milestone-verification-file verification.json \
  --signing-key-file beneficiary.skey \
  --testnet \
  --submit
```

### Scenario 2: Double-Claim Prevention

1. Submit valid claim transaction (should succeed)
2. Submit same claim again (should fail)
3. Verify error message indicates already claimed

### Scenario 3: Quorum Failure

1. Create milestone verification with insufficient signatures
2. Attempt claim transaction
3. Verify transaction rejected with quorum error

### Scenario 4: Vesting Enforcement

1. Create allocation with future vesting timestamp
2. Attempt claim before vesting time
3. Verify transaction rejected
4. Wait for vesting time
5. Retry claim (should succeed)

### Scenario 5: Multi-Recipient Claims

1. Create contract with 5 beneficiary allocations
2. Have beneficiary 0 claim (should succeed)
3. Verify contract still has allocations for beneficiaries 1-4
4. Have beneficiary 1 claim (should succeed)
5. Continue until all claimed

## Monitoring Testnet Transactions

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

### Monitor Contract UTXO

```bash
cardano-cli query utxo \
  --address <contract-address> \
  --testnet-magic 1097911063
```

## Common Issues and Solutions

### Issue: Transaction Size Too Large

**Solution**: 
- Reduce number of beneficiary allocations per contract
- Optimize datum structure
- Use compressed encoding for oracle signatures

### Issue: Execution Budget Exceeded

**Solution**:
- Optimize validator logic
- Reduce quorum verification complexity
- Test execution units on testnet first

### Issue: Invalid Oracle Signatures

**Solution**:
- Verify signatures off-chain before submission
- Use `verify-milestone` command to check
- Ensure oracle addresses match authorized set

### Issue: Vesting Timestamp Not Met

**Solution**:
- Check current slot/time on testnet
- Verify vesting timestamp is in POSIXTime format
- Wait for vesting period to start

## Next Steps

1. **Complete Implementation**: Implement validator logic based on data-model.md
2. **Write Tests**: Create comprehensive test suite covering all scenarios
3. **Build CLI**: Implement CLI commands for contract interaction
4. **Testnet Testing**: Deploy and test on testnet with various scenarios
5. **Mainnet Preparation**: Replace test tokens/oracles with production values

## Resources

- [Aiken Documentation](https://aiken-lang.org)
- [Cardano Developer Portal](https://developers.cardano.org)
- [QA-DAO Token Distribution Framework](https://github.com/Quality-Assurance-DAO/Token-Distribution-Framework)
- Project Documentation:
  - [Data Model](./data-model.md)
  - [Research Findings](./research.md)
  - [Validator Contract](./contracts/validator-contract.md)
  - [CLI Interface](./contracts/cli-interface.md)

## Getting Help

- Check test output for detailed error messages
- Review validator logs (if enabled)
- Consult Aiken and Cardano documentation
- Review test scenarios in `tests/integration/` directory

