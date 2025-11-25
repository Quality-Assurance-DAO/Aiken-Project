# Unit Test Evidence

**Navigation**: [Home](../../README.md) > [Documentation](../README.md) > [Testing Guide](../testing-guide.md) > Unit Test Evidence

This document provides sample outputs from unit test execution and interpretation guidelines.

## Test Suite Information

- **Test Suite**: Unit Tests
- **Location**: `tests/unit/`
- **Purpose**: Test individual contract functions and validators in isolation
- **Last Updated**: 2025-01-27

## Execution Command

```bash
cd /Users/stephen/Documents/GitHub/Aiken-Project
aiken test tests/unit/
```

## Prerequisites

- Aiken compiler installed
- No Cardano node required (unit tests run in isolation)
- Test data files configured (`test-data/allocations.json`, `test-data/oracles.json`)

## Sample Output

```
Running unit tests...

✓ tests/unit/contract_test.aiken
  ✓ test_allocation_validation
  ✓ test_claim_eligibility
  ✓ test_vesting_calculation

✓ tests/unit/validator_test.aiken
  ✓ test_validator_accepts_valid_claim
  ✓ test_validator_rejects_invalid_claim
  ✓ test_validator_enforces_vesting

All tests passed: 6/6
```

## Interpretation Notes

### Pass Criteria

- **All tests pass**: All assertions evaluate to true
- **No errors**: No compilation or runtime errors
- **Fast execution**: Unit tests should complete quickly (< 5 seconds)

### Fail Criteria

- **Test failures**: Any assertion evaluates to false
- **Compilation errors**: Test code fails to compile
- **Runtime errors**: Tests crash during execution

### Understanding Test Results

- **✓ (checkmark)**: Test passed
- **✗ (cross)**: Test failed
- **Test count**: Shows number of tests run and passed

## Expected Runtime

- **Typical**: < 5 seconds
- **Maximum**: < 10 seconds
- **Note**: Unit tests are fast because they don't require network access

## Environment Context

- **OS**: macOS (tested on macOS 15 / Apple Silicon)
- **Aiken Version**: Latest stable
- **Network**: Not required (unit tests run in isolation)

## Common Issues

**Issue**: Tests fail with "function not found"  
**Solution**: Verify test imports match contract module structure

**Issue**: Tests fail with "datum mismatch"  
**Solution**: Ensure test data matches expected datum structure

**Issue**: Tests timeout  
**Solution**: Check for infinite loops or excessive computation in test code

## Related Documentation

- [Testing Guide](../testing-guide.md) - How to run tests
- [Integration Test Evidence](./integration-tests.md) - Integration test outputs
- [Validator Test Evidence](./validator-tests.md) - Validator test outputs

