# Testing Guide

This guide explains how to run tests for the Python off-chain backend.

## Prerequisites

1. **Activate the virtual environment** (if not already active):
   ```bash
   cd offchain/
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate     # On Windows
   ```

2. **Install dependencies** (if needed):
   ```bash
   pip install -r requirements.txt
   # or
   pip install -e .[dev]  # Installs package with dev dependencies
   ```

## Running Tests

### Run All Tests

Run all tests in the project:
```bash
cd offchain/
pytest
```

### Run Tests by Category

**Unit tests only:**
```bash
pytest tests/unit/
```

**Integration tests only:**
```bash
pytest tests/integration/
```

**Contract tests only:**
```bash
pytest tests/contract/
```

### Run Specific Test Files

**Run milestone manager tests:**
```bash
pytest tests/unit/test_milestone_manager.py
```

**Run commit-milestone integration tests:**
```bash
pytest tests/integration/test_commit_milestone.py
```

### Run Specific Test Functions

**Run a single test function:**
```bash
pytest tests/unit/test_milestone_manager.py::test_milestone_data_storage_file_io
```

**Run multiple specific tests:**
```bash
pytest tests/unit/test_milestone_manager.py::test_milestone_data_storage_file_io tests/unit/test_milestone_manager.py::test_quorum_calculation_various_counts
```

### Run Tests with Verbose Output

**Show detailed output:**
```bash
pytest -v
```

**Show even more detail (print statements):**
```bash
pytest -v -s
```

**Show test names only:**
```bash
pytest -v --collect-only
```

## Test Categories

### Unit Tests (`tests/unit/`)

Unit tests test individual components in isolation:
- `test_milestone_manager.py` - Milestone management logic
- `test_ogmios_client.py` - Ogmios client connectivity
- `test_kupo_client.py` - Kupo client connectivity

**Run unit tests:**
```bash
pytest tests/unit/ -v
```

### Integration Tests (`tests/integration/`)

Integration tests test CLI commands end-to-end:
- `test_init.py` - Environment initialization
- `test_register_milestone.py` - Milestone registration
- `test_commit_milestone.py` - Milestone completion data commitment

**Note:** Some integration tests may require services to be running. They will skip gracefully if services are unavailable.

**Run integration tests:**
```bash
pytest tests/integration/ -v
```

### Contract Tests (`tests/contract/`)

Contract tests verify validator loading and serialization:
- Tests for loading compiled Aiken validators
- Tests for datum/redeemer serialization

**Run contract tests:**
```bash
pytest tests/contract/ -v
```

## Test Markers

Some tests are marked with pytest markers:

**Run only integration tests:**
```bash
pytest -m integration
```

**Skip integration tests:**
```bash
pytest -m "not integration"
```

## Common Test Scenarios

### Test Phase 5 Implementation (Milestone Commitment)

**Run all milestone commitment tests:**
```bash
# Unit tests for milestone manager
pytest tests/unit/test_milestone_manager.py -v

# Integration tests for commit-milestone command
pytest tests/integration/test_commit_milestone.py -v
```

**Run specific Phase 5 tests:**
```bash
# Test milestone data storage
pytest tests/unit/test_milestone_manager.py::test_milestone_data_storage_file_io -v

# Test quorum calculation
pytest tests/unit/test_milestone_manager.py::test_quorum_calculation_various_counts -v

# Test incremental signature addition
pytest tests/unit/test_milestone_manager.py::test_commit_milestone_completion_data_incremental -v

# Test duplicate prevention
pytest tests/unit/test_milestone_manager.py::test_commit_milestone_completion_data_duplicate_prevention -v
```

## Troubleshooting

### Tests Fail with Import Errors

Make sure you're in the `offchain/` directory and the virtual environment is activated:
```bash
cd offchain/
source venv/bin/activate
pytest
```

### Tests Fail with Missing Dependencies

Install dependencies:
```bash
pip install -r requirements.txt
```

### Integration Tests Skip

Integration tests may skip if services aren't available. This is expected behavior. To run integration tests, ensure:
- Cardano node is running (if required)
- Ogmios service is available (if required)
- Kupo service is available (if required)

### View Test Coverage

Install coverage tools and run:
```bash
pip install pytest-cov
pytest --cov=offchain --cov-report=html
```

Then open `htmlcov/index.html` in your browser.

## Quick Test Commands Reference

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_milestone_manager.py

# Run specific test function
pytest tests/unit/test_milestone_manager.py::test_milestone_data_storage_file_io

# Run and show print statements
pytest -v -s

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run tests matching a pattern
pytest -k "milestone" -v
```

