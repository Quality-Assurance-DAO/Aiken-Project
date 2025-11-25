# Integration Test Evidence

**Navigation**: [Home](../../README.md) > [Documentation](../README.md) > [Testing Guide](../testing-guide.md) > Integration Test Evidence

This document provides sample outputs from integration test execution and interpretation guidelines.

## Test Suite Information

- **Test Suite**: Integration Tests
- **Location**: `tests/integration/`
- **Purpose**: Test end-to-end contract interactions and transaction flows
- **Last Updated**: 2025-01-27

## Execution Command

```bash
cd /Users/stephen/Documents/GitHub/Aiken-Project
aiken test tests/integration/
```

## Prerequisites

- Aiken compiler installed
- Cardano node running (for network tests)
- Cardano node socket path configured: `CARDANO_NODE_SOCKET_PATH`
- Test data files configured (`test-data/allocations.json`, `test-data/oracles.json`)
- Testnet access (for network integration tests)

## Sample Output

```
Running integration tests...

✓ tests/integration/deployment_test.aiken
  ✓ test_contract_deployment
  ✓ test_contract_state_initialization

✓ tests/integration/claim_test.aiken
  ✓ test_end_to_end_claim_flow
  ✓ test_oracle_validation_flow
  ✓ test_vesting_enforcement

All tests passed: 5/5
```

## Interpretation Notes

### Pass Criteria

- **All tests pass**: All end-to-end scenarios execute successfully
- **Network connectivity**: Cardano node connection established
- **Transaction submission**: Transactions build and submit successfully
- **State verification**: Contract state updates correctly

### Fail Criteria

- **Test failures**: Any scenario fails to complete
- **Network errors**: Cannot connect to Cardano node
- **Transaction errors**: Transactions fail to build or submit
- **State mismatch**: Contract state doesn't match expected values

### Understanding Test Results

- **✓ (checkmark)**: Test passed
- **✗ (cross)**: Test failed
- **Network indicators**: May show connection status if tests require network

## Expected Runtime

- **Typical**: 30-60 seconds
- **Maximum**: < 2 minutes
- **Note**: Integration tests are slower due to network interactions

## Environment Context

- **OS**: macOS (tested on macOS 15 / Apple Silicon)
- **Aiken Version**: Latest stable
- **Cardano Node Version**: Latest stable
- **Network**: Testnet (Preprod)
- **Socket Path**: `~/cardano/db/testnet/node.socket`

## Common Issues

**Issue**: Tests fail with "socket connection error"  
**Solution**: Ensure Cardano node is running and `CARDANO_NODE_SOCKET_PATH` is set correctly

**Issue**: Tests fail with "transaction submission failed"  
**Solution**: Verify testnet connectivity and sufficient test ADA for fees

**Issue**: Tests timeout  
**Solution**: Check network connectivity and node synchronization status

## Related Documentation

- [Testing Guide](../testing-guide.md) - How to run tests
- [Cardano CLI Setup](../cardano-cli-setup.md) - Node setup
- [Unit Test Evidence](./unit-tests.md) - Unit test outputs
- [Validator Test Evidence](./validator-tests.md) - Validator test outputs


