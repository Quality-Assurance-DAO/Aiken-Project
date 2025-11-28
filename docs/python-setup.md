# Python Setup Guide

**Navigation**: [Home](../README.md) > [Documentation](./README.md) > Python Setup

## Python Command on macOS

On macOS, Python 3 is typically installed as `python3` rather than `python`. This project uses `python3` in all scripts and documentation to ensure compatibility.

### Quick Check

```bash
# Check if python3 is available
which python3

# Check Python version
python3 --version
# Should show: Python 3.8.x or later
```

### Using Python Commands

**In scripts and terminal:**
```bash
# Use python3 explicitly
python3 cli.py init --network testnet

# Or use python if available (e.g., in virtual environment)
python cli.py init --network testnet
```

**In virtual environments:**
After activating a virtual environment, `python` should work:
```bash
python3 -m venv venv
source venv/bin/activate
python cli.py init --network testnet  # Works in venv
```

### Installation

If Python 3 is not installed:

**macOS (using Homebrew):**
```bash
brew install python3
```

**Verify installation:**
```bash
python3 --version
pip3 --version
```

### Virtual Environment Setup

The project scripts automatically create and use virtual environments. For manual setup:

```bash
cd offchain
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Troubleshooting

**Error: "command not found: python"**
- Use `python3` instead of `python`
- Or create/activate a virtual environment where `python` is available

**Error: "No module named 'offchain'"**
- Ensure you're in the `offchain/` directory
- Or install the package: `pip install -e .`

**Scripts automatically handle this:**
The `scripts/test_preprod.sh` script detects and uses the correct Python command automatically.


