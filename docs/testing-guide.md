# Testing Guide

**Navigation**: [Home](../README.md) > [Documentation](./README.md) > Testing Guide

This guide documents how to run all test suites in the project and understand test results.

## Overview

This project includes multiple test suites to verify contract correctness, validator logic, and integration scenarios. All tests use the Aiken test framework.

## Test Suites

### Unit Tests

**Location**: `tests/unit/`  
**Purpose**: Test individual contract functions and validators in isolation  
**Command**: `aiken test` (runs all tests) or `aiken test tests/unit/`  
**Prerequisites**: Aiken compiler installed, no Cardano node required

**See**: [Unit Test Evidence](./test-evidence/unit-tests.md) for sample outputs

### Integration Tests

**Location**: `tests/integration/`  
**Purpose**: Test end-to-end contract interactions and transaction flows  
**Command**: `aiken test tests/integration/`  
**Prerequisites**: Aiken compiler, Cardano node socket (for network tests)

**See**: [Integration Test Evidence](./test-evidence/integration-tests.md) for sample outputs

### Validator Tests

**Location**: `tests/validator/`  
**Purpose**: Test validator logic with various scenarios and edge cases  
**Command**: `aiken test tests/validator/`  
**Prerequisites**: Aiken compiler, test data configured

**See**: [Validator Test Evidence](./test-evidence/validator-tests.md) for sample outputs

## Running Tests

### Prerequisites

1. **Aiken Compiler**: Install Aiken following [Aiken Documentation](https://aiken-lang.org/)
2. **Cardano Node** (for integration tests): See [Cardano CLI Setup](./cardano-cli-setup.md)
3. **Test Data**: Ensure `test-data/allocations.json` and `test-data/oracles.json` are configured

### Running All Tests

```bash
cd /Users/stephen/Documents/GitHub/Aiken-Project
aiken test
```

### Running Specific Test Suites

```bash
# Unit tests only
aiken test tests/unit/

# Integration tests only
aiken test tests/integration/

# Validator tests only
aiken test tests/validator/
```

### Running Individual Tests

```bash
# Run specific test file
aiken test tests/unit/specific_test.aiken

# Run with verbose output
aiken test --verbose
```

## Test Evidence

Sample test outputs and interpretation guides are documented in `docs/test-evidence/`:

- [Unit Test Evidence](./test-evidence/unit-tests.md) - Unit test sample outputs
- [Integration Test Evidence](./test-evidence/integration-tests.md) - Integration test sample outputs
- [Validator Test Evidence](./test-evidence/validator-tests.md) - Validator test sample outputs

Each test evidence document includes:
- Command used to run tests
- Sample output (pass/fail summary)
- Interpretation notes explaining pass/fail criteria
- Prerequisites and environment requirements
- Expected runtime

## Understanding Test Results

### Pass Criteria

Tests pass when:
- All assertions evaluate to true
- Validator logic executes correctly
- Contract state transitions are valid
- No execution budget exceeded

### Fail Criteria

Tests fail when:
- Assertions evaluate to false
- Validator rejects valid transactions
- Contract state transitions are invalid
- Execution budget exceeded
- Test setup errors occur

### Common Issues

**Issue**: Tests fail with "execution budget exceeded"  
**Solution**: Optimize validator logic or reduce test data complexity

**Issue**: Integration tests fail with "socket connection error"  
**Solution**: Ensure Cardano node is running and socket path is correct

**Issue**: Validator tests fail with "datum mismatch"  
**Solution**: Verify test data matches expected datum structure

## Test Maintenance

### Adding New Tests

1. Create test file in appropriate test directory (`tests/unit/`, `tests/integration/`, `tests/validator/`)
2. Follow Aiken test framework patterns
3. Update test evidence documentation if test behavior changes
4. Ensure tests are deterministic and reproducible

### Updating Test Evidence

When test outputs change:
1. Run tests and capture new output
2. Update corresponding test evidence document
3. Note environment differences if applicable
4. Update interpretation notes if pass/fail criteria change

## Related Documentation

- [Cardano CLI Setup](./cardano-cli-setup.md) - Environment setup for integration tests
- [Solution Architecture](./solution-architecture.md) - Understanding test targets
- [Glossary](./glossary.md) - Technical term definitions
- [Contribution Guide](./contribution-guide.md) - Adding new tests



