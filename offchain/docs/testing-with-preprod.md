# Testing Python Functions with Cardano Node on Preprod

This guide explains how to set up and run Python integration tests against a real cardano-node on the Preprod testnet.

## Prerequisites

- Docker and Docker Compose (for Ogmios/Kupo) OR local installations
- Cardano node binary (`bin/cardano-node`)
- Preprod network configuration files in `share/preprod/`

## Option 1: Using Local Cardano Node (Recommended)

### Step 1: Start Cardano Node for Preprod

```bash
# From project root
./scripts/start_node.sh preprod
```

This will:
- Start cardano-node using `share/preprod/` configuration
- Create socket at `preprod-socket/node.socket`
- Use database directory `db-preprod/`

**Note**: The node will take time to sync. Monitor progress:
```bash
tail -f preprod.log
```

### Step 2: Set Up Ogmios and Kupo

You have two options:

#### Option A: Docker Compose (Easier)

Create a `docker-compose.preprod.yml` file:

```yaml
version: '3.8'

services:
  ogmios:
    image: cardanosolutions/ogmios:latest
    container_name: ogmios-preprod
    volumes:
      - ./preprod-socket:/ipc:ro
    ports:
      - "1337:1337"
    environment:
      - OGMIOS_HOST=0.0.0.0
      - OGMIOS_PORT=1337
      - OGMIOS_NODE_SOCKET=/ipc/node.socket
      - OGMIOS_NODE_NETWORK=preprod
    restart: unless-stopped

  kupo:
    image: cardanosolutions/kupo:latest
    container_name: kupo-preprod
    volumes:
      - ./preprod-socket:/ipc:ro
      - ./share/preprod:/config:ro
      - kupo-preprod-db:/data
    ports:
      - "1442:1442"
    environment:
      - KUPO_HOST=0.0.0.0
      - KUPO_PORT=1442
      - KUPO_NODE_SOCKET=/ipc/node.socket
      - KUPO_NODE_CONFIG=/config/config.json
      - KUPO_DB_PATH=/data
      - KUPO_SERVER_HOST=0.0.0.0
      - KUPO_SERVER_PORT=1442
    restart: unless-stopped

volumes:
  kupo-preprod-db:
```

Start services:
```bash
docker-compose -f docker-compose.preprod.yml up -d
```

#### Option B: Local Installation

Install Ogmios and Kupo locally and configure them to use `preprod-socket/node.socket`.

### Step 3: Verify Services Are Running

```bash
# Check Ogmios (should return version info)
curl http://localhost:1337/health

# Check Kupo (should return health status)
curl http://localhost:1442/health

# Check cardano-node socket exists
ls -l preprod-socket/node.socket
```

### Step 4: Configure Python Tests for Preprod

Set environment variables:

```bash
export CARDANO_NETWORK=preprod
export OGMIOS_URL=ws://localhost:1337
export KUPO_URL=http://localhost:1442
export CARDANO_NODE_SOCKET=$(pwd)/preprod-socket/node.socket
export DATA_DIRECTORY=$(pwd)/offchain/data-preprod
```

Or create a test configuration file `offchain/config.preprod.yaml`:

```yaml
network:
  network: preprod
  ogmios_url: ws://localhost:1337
  kupo_url: http://localhost:1442
  cardano_node_socket: /path/to/preprod-socket/node.socket

storage:
  data_directory: offchain/data-preprod
```

### Step 5: Test Connectivity

```bash
cd offchain
source venv/bin/activate

# Test connectivity
python cli.py init \
  --network preprod \
  --ogmios-url ws://localhost:1337 \
  --kupo-url http://localhost:1442 \
  --cardano-node-socket ../preprod-socket/node.socket
```

Expected output:
```json
{
  "status": "success",
  "services": {
    "ogmios": {"connected": true, "version": "..."},
    "kupo": {"connected": true},
    "cardano_node": {"connected": true, "network": "preprod"}
  }
}
```

### Step 6: Run Integration Tests

```bash
# Run all integration tests
pytest tests/integration/ -v

# Run specific test
pytest tests/integration/test_init.py::test_init_command_with_real_services -v

# Run with preprod environment
CARDANO_NETWORK=preprod \
OGMIOS_URL=ws://localhost:1337 \
KUPO_URL=http://localhost:1442 \
CARDANO_NODE_SOCKET=../preprod-socket/node.socket \
pytest tests/integration/ -v
```

## Option 2: Using Docker Compose for Everything

If you prefer to run everything via Docker:

1. Update `infra/docker-compose.yml` to use preprod config
2. Mount preprod socket directory
3. Start all services together

## Writing Tests for Preprod

### Example: Test with Real Preprod Services

```python
import pytest
import os
from pathlib import Path

@pytest.mark.integration
def test_with_preprod():
    """Test with real preprod services."""
    # Set environment for preprod
    os.environ["CARDANO_NETWORK"] = "preprod"
    os.environ["OGMIOS_URL"] = "ws://localhost:1337"
    os.environ["KUPO_URL"] = "http://localhost:1442"
    os.environ["CARDANO_NODE_SOCKET"] = str(
        Path(__file__).parent.parent.parent.parent / "preprod-socket" / "node.socket"
    )
    
    # Your test code here
    from offchain.ogmios_client import OgmiosClient
    from offchain.kupo_client import KupoClient
    
    ogmios = OgmiosClient("ws://localhost:1337")
    # ... test code
```

### Example: Test Contract State Query

```python
@pytest.mark.integration
def test_query_contract_on_preprod():
    """Query a real contract on preprod."""
    import asyncio
    from offchain.milestone_manager import MilestoneManager
    from offchain.kupo_client import KupoClient
    from offchain.config import DataStorageConfiguration
    
    # Setup
    storage_config = DataStorageConfiguration()
    manager = MilestoneManager(storage_config.data_directory)
    kupo = KupoClient("http://localhost:1442")
    
    # Query contract address (replace with real address)
    contract_address = "addr_test1q..."
    utxos = kupo.query_utxos_by_address(contract_address)
    
    if utxos:
        contract_state = manager.parse_contract_state_from_utxo(utxos[0], contract_address)
        assert contract_state is not None
        print(f"Contract state: {contract_state}")
    else:
        pytest.skip("No UTxOs found at contract address")
```

## Troubleshooting

### Node Not Syncing

```bash
# Check node logs
tail -f preprod.log

# Check if node is connected to peers
grep "ConnectionAttemptEndPoint" preprod.log
```

### Ogmios/Kupo Can't Connect

```bash
# Verify socket permissions
ls -l preprod-socket/node.socket

# Check if socket is accessible from Docker
docker exec ogmios-preprod ls -l /ipc/node.socket
```

### Tests Timeout

- Ensure node is fully synced
- Check service health endpoints
- Verify network connectivity

### Port Conflicts

If ports 1337 or 1442 are already in use:

```bash
# Find process using port
lsof -i :1337
lsof -i :1442

# Kill process or change ports in docker-compose
```

## Quick Start Script

Save this as `scripts/test_preprod.sh`:

```bash
#!/bin/bash
set -e

# Start node (in background)
echo "Starting cardano-node for preprod..."
./scripts/start_node.sh preprod > preprod.log 2>&1 &
NODE_PID=$!

# Wait for socket to appear
echo "Waiting for node socket..."
timeout=60
elapsed=0
while [ ! -S preprod-socket/node.socket ] && [ $elapsed -lt $timeout ]; do
    sleep 2
    elapsed=$((elapsed + 2))
done

if [ ! -S preprod-socket/node.socket ]; then
    echo "Error: Node socket not created"
    kill $NODE_PID 2>/dev/null || true
    exit 1
fi

# Start Ogmios/Kupo
echo "Starting Ogmios and Kupo..."
docker-compose -f docker-compose.preprod.yml up -d

# Wait for services
sleep 5

# Run tests
echo "Running tests..."
cd offchain
source venv/bin/activate
export CARDANO_NETWORK=preprod
export OGMIOS_URL=ws://localhost:1337
export KUPO_URL=http://localhost:1442
export CARDANO_NODE_SOCKET=../preprod-socket/node.socket

pytest tests/integration/ -v

# Cleanup
echo "Cleaning up..."
docker-compose -f docker-compose.preprod.yml down
kill $NODE_PID 2>/dev/null || true
```

Make it executable:
```bash
chmod +x scripts/test_preprod.sh
```

Run:
```bash
./scripts/test_preprod.sh
```

## Next Steps

- Test milestone registration
- Test contract state queries
- Test milestone completion data
- Test transaction building (when implemented)

