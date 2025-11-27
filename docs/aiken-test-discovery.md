# Aiken Test Discovery Mechanism Investigation

## Summary

**Answer to your question**: No, tests do **not** need to be "run" first to be discovered. Test discovery happens automatically during `aiken check` compilation. However, tests are currently not being discovered in this project.

## Current State

When running `aiken check`, the output shows:
```json
{
  "summary": {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "kind": {
      "unit": 0,
      "property": 0
    }
  },
  "modules": []
}
```

The `"modules": []` indicates that **no modules are being scanned for tests**, even though test functions exist in the codebase.

## Test Locations Found

Tests are defined in multiple locations:

### In `src/` directory (should be discovered):
1. `src/contract/oracle.aiken` - Contains 3 test functions:
   - `test "valid_quorum_acceptance"`
   - `test "quorum_failure_rejection"`
   - `test "duplicate_signature_handling"`

2. `src/lib/validation.aiken` - Contains 1 test function:
   - `test "test_validate_amount"`

3. `src/contract/oracle_test.aiken` - Contains 3 test functions
4. `src/contract/simple_test.aiken` - Contains 1 test function
5. `src/test_simple.aiken` - Contains 1 test function

### In `tests/` directory (may not be auto-discovered):
- `tests/validator/oracle_test.aiken` - 3 tests
- `tests/validator/validator_test.aiken` - 4 tests
- `tests/validator/datum_test.aiken` - 2 tests
- `tests/integration/` - Multiple integration tests

## How Aiken Test Discovery Works

Based on investigation:

1. **Test Discovery Happens During Compilation**: Tests are discovered when `aiken check` compiles the project, not after running them.

2. **Tests Must Be in Compiled Modules**: Aiken discovers tests from modules that are part of the compiled project structure in `src/`.

3. **Test Syntax**: Tests use the `test "name" { ... }` syntax and should return a boolean.

4. **Module Structure**: In Aiken, files in `src/` automatically become modules based on their path:
   - `src/contract/oracle.aiken` → module `contract/oracle`
   - `src/lib/validation.aiken` → module `lib/validation`

## Why Tests Aren't Being Discovered

Possible reasons:

1. **Module Not Part of Project Graph**: Tests might only be discovered from modules that are:
   - Explicitly imported/used by other modules
   - Part of the main project exports
   - Referenced in the module dependency graph

2. **Tests Directory Not Scanned**: The `tests/` directory might not be automatically scanned. Tests may need to be in `src/` to be discovered.

3. **Compilation Issues**: While `aiken check --skip-tests` compiles successfully, there might be subtle issues preventing test extraction.

4. **Configuration**: The `aiken.toml` file doesn't specify test directories, suggesting Aiken uses defaults.

## Test Discovery Requirements

Based on Aiken's behavior:

- ✅ Tests can be inline with code (like in `oracle.aiken`)
- ✅ Tests can be in separate files (like `oracle_test.aiken`)
- ❓ Tests in `tests/` directory may not be auto-discovered
- ❓ Tests might need to be in modules that are part of the dependency graph

## Recommendations

1. **Verify Module Compilation**: Ensure modules containing tests are being compiled:
   ```bash
   aiken check --skip-tests
   ```

2. **Check Module Dependencies**: Tests might need to be in modules that are imported/used by other parts of the project.

3. **Test File Location**: Try moving tests from `tests/` directory into `src/` to see if they're discovered.

4. **Explicit Module Declaration**: While not required, ensure test files are proper Aiken modules.

5. **Check Aiken Version**: Test discovery behavior might vary by Aiken version.

## Next Steps

1. Verify if tests in `src/contract/oracle.aiken` should be discovered (they're in a compiled module)
2. Check if `tests/` directory needs special configuration
3. Investigate if tests need to be explicitly referenced/imported
4. Review Aiken documentation for test discovery requirements

## Related Documentation

- [Testing Guide](./testing-guide.md) - Project testing documentation
- [Unit Test Evidence](./test-evidence/unit-tests.md) - Expected test outputs
- [Aiken Documentation](https://aiken-lang.org/) - Official Aiken docs

