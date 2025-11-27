# Aiken v1.1.19 Test Discovery Requirements

**Date**: 2025-11-27  
**Aiken Version**: v1.1.19  
**Source**: Official Aiken Documentation & CLI Help

## Overview

Aiken v1.1.19 automatically discovers and executes tests during the `aiken check` command. Test discovery happens as part of the compilation process, not as a separate step.

## Core Requirements

### 1. Test Location

**Tests must be in modules within the `src/` directory:**

- ✅ Tests can be inline with production code (e.g., `src/contract/oracle.aiken`)
- ✅ Tests can be in separate test files (e.g., `src/contract/oracle_test.aiken`)
- ✅ Tests can be in any module file within `src/`
- ❌ Tests in `tests/` directory are **NOT automatically discovered** by default

### 2. Module Compilation Requirement

**Tests are only discovered from modules that are part of the compilation graph:**

- Modules must be compiled during `aiken check`
- A module is compiled if it is:
  - Explicitly imported by another module (`use module/path`)
  - Part of the main project exports (referenced in entry points)
  - Referenced in the module dependency graph

**Important**: If a module containing tests is not imported or referenced, its tests will **not** be discovered, even if the file exists in `src/`.

### 3. Test Syntax

Tests use the following syntax:

```aiken
test "test_name" {
  // Test body that returns a boolean
  expression == expected_value
}
```

- Test name must be a string literal
- Test body must evaluate to a boolean (`True` = pass, `False` = fail)
- Tests have access to all functions and constants in the module

### 4. Module Structure

Files in `src/` automatically become modules based on their path:

- `src/contract/oracle.aiken` → module `contract/oracle`
- `src/lib/validation.aiken` → module `lib/validation`
- `src/test_simple.aiken` → module `test_simple`

## Test Discovery Process

1. **Compilation**: `aiken check` compiles all modules in `src/` that are part of the dependency graph
2. **Discovery**: During compilation, Aiken automatically scans compiled modules for `test` declarations
3. **Execution**: All discovered tests are executed and results are reported

## Ensuring Test Discovery

### Method 1: Import Test Modules

Import test modules in a module that's part of the compilation graph:

```aiken
// In src/onchain_exports.aiken or another compiled module
use contract/oracle_test
use contract/simple_test
use test_simple
```

### Method 2: Place Tests in Used Modules

Place tests directly in modules that are already imported/used:

```aiken
// In src/contract/oracle.aiken (already imported)
pub fn some_function() { ... }

test "my_test" {
  some_function() == expected_value
}
```

### Method 3: Reference Test Modules in Entry Points

Ensure test modules are referenced in your main entry points or exports.

## CLI Options for Test Discovery

### Basic Usage

```bash
# Discover and run all tests
aiken check

# Skip tests (only type-check)
aiken check --skip-tests

# Match specific modules or tests
aiken check -m "contract/oracle"           # Match module
aiken check -m "contract/oracle.{test_name}"  # Match specific test
```

### Test Matching

- `-m, --match-tests <MATCH_TESTS>`: Only run tests matching the pattern
  - Module match: `-m aiken/list` or `-m list`
  - Test match: `-m "aiken/list.{map}"` or `-m "aiken/option.{flatten_1}"`
- `-e, --exact-match`: Force exact name matching (used with `--match-tests`)

## Common Issues

### Tests Not Discovered

**Symptom**: `aiken check` shows `"modules": []` or `"total": 0` in JSON output

**Possible Causes**:
1. Test modules are not imported/referenced in the compilation graph
2. Tests are in `tests/` directory instead of `src/`
3. Module compilation errors prevent test discovery
4. Test syntax is incorrect

**Solutions**:
1. Import test modules in a compiled module (e.g., `src/onchain_exports.aiken`)
2. Move tests from `tests/` to `src/` directory
3. Fix compilation errors with `aiken check --skip-tests`
4. Verify test syntax matches `test "name" { boolean_expression }`

### Module Not Compiled

**Symptom**: Module exists in `src/` but tests aren't discovered

**Solution**: Ensure the module is imported somewhere in your codebase:

```aiken
// In any compiled module
use your/module/path
```

## Best Practices

1. **Organize Tests**: Keep tests close to the code they test (inline) or in dedicated `*_test.aiken` files
2. **Ensure Discovery**: Import test modules explicitly if they're in separate files
3. **Use Descriptive Names**: Test names should clearly describe what they verify
4. **Leverage Module Matching**: Use `-m` flag to run specific test suites during development

## Example Project Structure

```
src/
├── contract/
│   ├── oracle.aiken          # Production code + inline tests ✅
│   └── oracle_test.aiken     # Separate test file ✅
├── lib/
│   └── validation.aiken      # Production code + inline tests ✅
├── test_simple.aiken         # Standalone test module ✅
└── onchain_exports.aiken     # Entry point that imports test modules ✅

tests/                         # ❌ Not auto-discovered
├── validator/
└── integration/
```

## References

- [Official Aiken Documentation - Tests](https://aiken-lang.org/language-tour/tests)
- [Aiken CLI Help](https://aiken-lang.org/) - Run `aiken check --help` for latest options
- [Project Test Discovery Investigation](./aiken-test-discovery.md) - Local investigation notes

## Summary

**Key Takeaway**: In Aiken v1.1.19, tests are automatically discovered from modules in `src/` that are part of the compilation graph. Ensure test modules are imported or referenced to guarantee discovery.

