# Quickstart Guide: Python Off-Chain Backend

**Date**: 2025-01-27  
**Feature**: 003-python-offchain-backend

## Overview

This guide provides a quick start for using the Python off-chain backend for milestone-based token distribution on Cardano. The backend provides CLI commands for managing milestone schedules, tracking completions, and submitting token release transactions.

## Prerequisites

- Python 3.8 or later
- Docker and Docker Compose (for infrastructure services)
- Local cardano-node, Ogmios, and Kupo services (or use Docker Compose)
- Wallet signing keys for transaction signing
- Compiled Aiken validator artifacts (`plutus.json`)

## Installation

### 1. Install Python Dependencies

```bash
cd /path/to/Aiken-Project
pip install -r offchain/requirements.txt
```

**Required packages** (from `research.md`):
- `pycardano>=0.9.0` - Cardano transaction building
- `typer>=0.9.0` - CLI framework
- `websockets>=11.0` - WebSocket client for Ogmios
- `httpx>=0.25.0` - HTTP client for Kupo
- `pydantic>=2.0` - Data validation
- `pytest` and `pytest-asyncio` - Testing

### 2. Start Infrastructure Services

Using Docker Compose (recommended):

```bash
cd infra/
docker-compose up -d
```

This starts:
- **cardano-node**: Cardano blockchain node
- **Ogmios**: WebSocket JSON-RPC interface (port 1337)
- **Kupo**: UTxO indexer (port 1442)

Verify services are running:

```bash
# Check Ogmios
curl http://localhost:1337/health

# Check Kupo
curl http://localhost:1442/health
```

### 3. Verify Validator Artifacts

Ensure `plutus.json` exists in project root with compiled validators:

```bash
ls -la plutus.json
```

## Quick Start Workflow

### Step 1: Initialize Environment

Initialize and verify connectivity to all services:

```bash
python cli.py init --network testnet
```

**Expected output**:
```json
{
  "status": "success",
  "services": {
    "ogmios": {"connected": true, "version": "..."},
    "kupo": {"connected": true, "sync_status": "synced"},
    "cardano_node": {"connected": true, "network": "testnet"}
  }
}
```

### Step 2: Register Milestone Schedule

Create a new milestone schedule for token distribution:

```bash
python cli.py register-milestone \
  --token-policy-id "abc123..." \
  --beneficiary-allocations allocations.json \
  --oracle-addresses addr1...,addr2...,addr3... \
  --quorum-threshold 2
```

**Example `allocations.json`**:
```json
[
  {
    "beneficiary_address": "addr1...",
    "token_amount": 1000000,
    "milestone_identifier": "milestone-001",
    "vesting_timestamp": 1735689600
  },
  {
    "beneficiary_address": "addr1...",
    "token_amount": 2000000,
    "milestone_identifier": "milestone-002",
    "vesting_timestamp": 1738281600
  }
]
```

**Output**: Distribution contract datum and contract address ready for on-chain deployment.

### Step 3: Deploy Contract On-Chain

Deploy the contract using Cardano CLI or your preferred method:

```bash
# Build transaction with contract datum
cardano-cli transaction build \
  --tx-in <funding_utxo> \
  --tx-out "$(cat contract.addr)+2000000+1 <token_policy_id>.<token_name>" \
  --tx-out-datum-hash-file contract_datum.json \
  --change-address <your_address> \
  --testnet-magic 1097911063 \
  --out-file tx.unsigned

# Sign and submit
cardano-cli transaction sign --tx-body-file tx.unsigned --signing-key-file payment.skey --testnet-magic 1097911063 --out-file tx.signed
cardano-cli transaction submit --tx-file tx.signed --testnet-magic 1097911063
```

### Step 4: Commit Milestone Completion Data

Record milestone completion with oracle signatures:

```bash
python cli.py commit-milestone \
  --milestone-identifier "milestone-001" \
  --oracle-signatures signatures.json \
  --quorum-threshold 2 \
  --total-oracles 3
```

**Example `signatures.json`**:
```json
[
  {
    "oracle_address": "addr1...",
    "signature": "abc123...",
    "signed_data": "def456...",
    "signature_timestamp": 1735689600
  },
  {
    "oracle_address": "addr2...",
    "signature": "ghi789...",
    "signed_data": "def456...",
    "signature_timestamp": 1735689610
  }
]
```

**Output**: Milestone completion data stored locally in `offchain/data/milestones/milestone-001.json`.

### Step 5: Check Milestone Status

Query milestone completion status:

```bash
python cli.py check-status \
  --contract-address "addr1..." \
  --milestone-identifier "milestone-001"
```

**Output**:
```json
{
  "contract_address": "addr1...",
  "milestones": [
    {
      "milestone_identifier": "milestone-001",
      "verified": true,
      "quorum_status": "met",
      "signature_count": 2,
      "quorum_threshold": 2,
      "vesting_passed": true
    }
  ],
  "contract_state": {
    "total_token_amount": 3000000,
    "remaining_token_amount": 3000000,
    "claimed_count": 0,
    "unclaimed_count": 2
  }
}
```

### Step 6: Calculate Distribution Amount

Calculate claimable tokens for a beneficiary:

```bash
python cli.py calculate-distribution \
  --contract-address "addr1..." \
  --beneficiary-address "addr1..."
```

**Output**:
```json
{
  "beneficiary_address": "addr1...",
  "claimable_amount": 1000000,
  "allocations": [
    {
      "milestone_identifier": "milestone-001",
      "token_amount": 1000000,
      "claimable": true,
      "reason": "claimable",
      "vesting_passed": true
    }
  ]
}
```

### Step 7: Submit Release Transaction

Build, sign, and submit a token release transaction:

```bash
python cli.py submit-release \
  --contract-address "addr1..." \
  --beneficiary-address "addr1..." \
  --beneficiary-index 0 \
  --milestone-identifier "milestone-001" \
  --signing-key-path payment.skey
```

**Output**:
```json
{
  "transaction_hash": "abc123...",
  "status": "submitted",
  "fee_estimate": 200000,
  "collateral_amount": 5000000
}
```

## Configuration

### Network Configuration

Default configuration file: `offchain/config.yaml`

```yaml
network: testnet
ogmios_url: ws://localhost:1337
kupo_url: http://localhost:1442
data_directory: offchain/data
```

Override with environment variables:

```bash
export CARDANO_NETWORK=testnet
export OGMIOS_URL=ws://localhost:1337
export KUPO_URL=http://localhost:1442
```

### Data Storage

Default data directory: `offchain/data/`

```
offchain/data/
├── milestones/          # Milestone completion JSON files
│   └── milestone-001.json
└── cache/              # Cached contract states
    └── contract_*.json
```

Change data directory:

```bash
python cli.py --data-dir /custom/path/to/data <command>
```

## Common Workflows

### Workflow 1: Complete Milestone Distribution Cycle

1. Initialize environment: `cli.py init`
2. Register schedule: `cli.py register-milestone`
3. Deploy contract on-chain (using Cardano CLI)
4. Commit milestone completion: `cli.py commit-milestone`
5. Check status: `cli.py check-status`
6. Calculate distribution: `cli.py calculate-distribution`
7. Submit release: `cli.py submit-release`

### Workflow 2: Query Existing Contract

1. Initialize environment: `cli.py init`
2. Check status: `cli.py check-status --contract-address <addr>`
3. Calculate distribution: `cli.py calculate-distribution --contract-address <addr>`

### Workflow 3: Batch Milestone Commitments

1. Commit multiple milestones:
   ```bash
   for milestone in milestone-001 milestone-002 milestone-003; do
     python cli.py commit-milestone \
       --milestone-identifier "$milestone" \
       --oracle-signatures "signatures_${milestone}.json"
   done
   ```

## Troubleshooting

### Service Connection Issues

**Problem**: `init` command reports services unavailable

**Solution**:
1. Verify Docker containers are running: `docker ps`
2. Check service ports: `netstat -an | grep -E '1337|1442'`
3. Check service logs: `docker-compose logs ogmios kupo`

### Transaction Building Failures

**Problem**: `submit-release` fails with validation errors

**Solution**:
1. Verify milestone is verified: `cli.py check-status`
2. Verify vesting timestamp passed: Check allocation in contract state
3. Verify sufficient ADA for fees: Check wallet balance
4. Verify quorum threshold met: Check milestone completion data

### File Corruption Recovery

**Problem**: Milestone completion data file is corrupted

**Solution**:
The system automatically recovers by querying on-chain state:
1. Delete corrupted file: `rm offchain/data/milestones/milestone-001.json`
2. Query status: `cli.py check-status --contract-address <addr>`
3. System rebuilds local cache from chain data

## Next Steps

- Review [data-model.md](./data-model.md) for detailed data structures
- Review [research.md](./research.md) for technical decisions
- Review [contracts/cli-api.yaml](./contracts/cli-api.yaml) for API documentation
- See [plan.md](./plan.md) for implementation details

## Support

For issues or questions:
- Check service logs: `docker-compose logs`
- Verify network connectivity: `cli.py init`
- Review error messages for specific validation failures

