# Validator Test Evidence

**Navigation**: [Home](../../README.md) > [Documentation](../README.md) > [Testing Guide](../testing-guide.md) > Validator Test Evidence

This document provides sample outputs from validator test execution and interpretation guidelines.

## Test Suite Information

- **Test Suite**: Validator Tests
- **Location**: `tests/validator/`
- **Purpose**: Test validator logic with various scenarios and edge cases
- **Last Updated**: 2025-01-27

## Execution Command

```bash
cd /Users/stephen/Documents/GitHub/Aiken-Project
aiken test tests/validator/
```

## Prerequisites

- Aiken compiler installed
- Test data files configured (`test-data/allocations.json`, `test-data/oracles.json`)
- No Cardano node required (validator tests simulate on-chain execution)

## Sample Output

```
Running validator tests...

✓ tests/validator/milestone_validation_test.aiken
  ✓ test_milestone_completion_validation
  ✓ test_oracle_quorum_validation
  ✓ test_invalid_oracle_signature_rejection

✓ tests/validator/claim_validation_test.aiken
  ✓ test_valid_claim_acceptance
  ✓ test_invalid_claim_rejection
  ✓ test_vesting_timestamp_enforcement
  ✓ test_duplicate_claim_prevention

✓ tests/validator/edge_cases_test.aiken
  ✓ test_empty_allocation_handling
  ✓ test_max_allocation_limits
  ✓ test_boundary_conditions

All tests passed: 10/10
```

## Interpretation Notes

### Pass Criteria

- **All tests pass**: Validator logic correctly validates all scenarios
- **Edge cases handled**: Boundary conditions and error cases handled correctly
- **Execution budget**: Validator operates within execution budget limits
- **State transitions**: Validator correctly updates contract state

### Fail Criteria

- **Test failures**: Validator incorrectly accepts or rejects transactions
- **Execution budget exceeded**: Validator uses too many resources
- **State errors**: Validator fails to update state correctly
- **Logic errors**: Validator logic doesn't match expected behavior

### Understanding Test Results

- **✓ (checkmark)**: Test passed
- **✗ (cross)**: Test failed
- **Execution units**: May show CPU/memory usage if available

## Expected Runtime

- **Typical**: 10-20 seconds
- **Maximum**: < 30 seconds
- **Note**: Validator tests are faster than integration tests but slower than unit tests

## Environment Context

- **OS**: macOS (tested on macOS 15 / Apple Silicon)
- **Aiken Version**: Latest stable
- **Network**: Not required (validator tests simulate on-chain execution)
- **Plutus Version**: V2 (target)

## Common Issues

**Issue**: Tests fail with "execution budget exceeded"  
**Solution**: Optimize validator logic or reduce test data complexity

**Issue**: Tests fail with "validator rejected valid transaction"  
**Solution**: Review validator logic and test data for mismatches

**Issue**: Tests fail with "datum mismatch"  
**Solution**: Verify test data matches expected datum structure

## Related Documentation

- [Testing Guide](../testing-guide.md) - How to run tests
- [Unit Test Evidence](./unit-tests.md) - Unit test outputs
- [Integration Test Evidence](./integration-tests.md) - Integration test outputs
- [Solution Architecture](../solution-architecture.md) - Validator architecture


