# Python Off-Chain Backend

Python off-chain backend for milestone-based token distribution on Cardano.

## Overview

This backend provides CLI commands for managing milestone schedules, tracking milestone completions, and submitting token release transactions on the Cardano blockchain.

## Installation

### Prerequisites

- Python 3.8 or later
- Docker and Docker Compose (for infrastructure services)
- Local cardano-node, Ogmios, and Kupo services

### Install Dependencies

```bash
pip install -r requirements.txt
```

Or install as a package:

```bash
pip install -e .
```

## Quick Start

### 1. Start Infrastructure Services

```bash
cd ../infra/
docker-compose up -d
```

### 2. Initialize Environment

```bash
# Use python3 (or python if available in your environment)
python3 cli.py init --network testnet
```

### 3. Register Milestone Schedule

```bash
python3 cli.py register-milestone \
  --token-policy-id "abc123..." \
  --beneficiary-allocations allocations.json \
  --oracle-addresses addr1...,addr2... \
  --quorum-threshold 2
```

**Note**: On macOS, use `python3`. In a virtual environment, `python` may also work.

## CLI Commands

- `init` - Initialize and verify connectivity to Cardano services
- `register-milestone` - Register a new milestone schedule
- `commit-milestone` - Commit milestone completion data
- `check-status` - Check milestone completion status
- `calculate-distribution` - Calculate token distribution amounts
- `submit-release` - Submit token release transaction

## Project Structure

```
offchain/
├── offchain/          # Main package
│   ├── config.py      # Configuration management
│   ├── models.py      # Data models
│   ├── ogmios_client.py  # Ogmios WebSocket client
│   ├── kupo_client.py    # Kupo HTTP client
│   ├── milestone_manager.py  # Business logic
│   ├── tx_builder.py     # Transaction building
│   ├── wallet.py         # Wallet management
│   └── validator_loader.py  # Validator loading
├── cli.py             # CLI entry point
├── tests/             # Test suite
└── requirements.txt   # Dependencies
```

## Configuration

Default configuration file: `config.yaml` (optional)

Override with environment variables:
- `CARDANO_NETWORK` - Network (testnet/mainnet/preview/preprod)
- `OGMIOS_URL` - Ogmios WebSocket URL
- `KUPO_URL` - Kupo HTTP URL
- `DATA_DIRECTORY` - Data storage directory

## Documentation

See the [specs/003-python-offchain-backend/](../specs/003-python-offchain-backend/) directory for:
- [plan.md](../specs/003-python-offchain-backend/plan.md) - Implementation plan
- [data-model.md](../specs/003-python-offchain-backend/data-model.md) - Data structures
- [quickstart.md](../specs/003-python-offchain-backend/quickstart.md) - Detailed quickstart guide
- [research.md](../specs/003-python-offchain-backend/research.md) - Technical decisions

## Testing

Run tests:

```bash
pytest
```

Run specific test categories:

```bash
pytest tests/unit/          # Unit tests
pytest tests/integration/   # Integration tests
pytest tests/contract/      # Contract tests
```

## License

MIT

