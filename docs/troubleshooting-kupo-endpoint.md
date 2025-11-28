# Troubleshooting Kupo "Endpoint Not Found" Error

**Navigation**: [Home](../README.md) > [Documentation](./README.md) > Troubleshooting Kupo Endpoint

## Error Message

```
"hint": "Endpoint not found. Make sure to double-check the documentation at: <https://cardanosolutions.github.io/kupo>!"
```

## Common Causes and Solutions

### 1. Kupo Service Not Running

**Symptom**: All Kupo requests fail with connection errors or "endpoint not found"

**Solution**: Start Kupo service

```bash
# Check if Kupo is running
curl http://localhost:1442/health

# If not running, start it using Docker
docker-compose up -d kupo

# Or start natively (if configured)
./scripts/start_services.sh preprod  # or preview
```

**Verify**: 
```bash
curl http://localhost:1442/health
# Should return: {"status":"synced"} or similar
```

### 2. Incorrect Kupo URL Configuration

**Symptom**: Requests fail even though Kupo is running elsewhere

**Solution**: Check and update Kupo URL

```bash
# Check current configuration
echo $KUPO_URL

# Set correct URL (if running on different host/port)
export KUPO_URL="http://localhost:1442"  # Default
# Or for remote instance:
export KUPO_URL="http://your-kupo-host:1442"
```

**In Python code**:
```python
from offchain.kupo_client import KupoClient

# Use custom URL
client = KupoClient(url="http://your-kupo-host:1442")
```

### 3. Invalid Address Format

**Symptom**: Endpoint not found for specific addresses

**Solution**: Verify address format

- Testnet addresses should start with `addr_test1`
- Mainnet addresses should start with `addr1`
- Ensure address is complete and not truncated

```bash
# Verify address format
cardano-cli address info --address <your-address>
```

### 4. Kupo Not Fully Synced

**Symptom**: Endpoint works but returns empty results or errors

**Solution**: Wait for Kupo to sync

```bash
# Check sync status
curl http://localhost:1442/health

# Check Kupo logs
docker logs kupo
# Or if running natively:
tail -f kupo.log
```

**Wait for**: Status should show `"synced"` or `"ready"`

### 5. Address Not Indexed by Kupo

**Symptom**: Valid address returns 404

**Solution**: Ensure Kupo is configured to match all addresses

When starting Kupo, use `--match "*"` to index all addresses:

```bash
kupo \
  --node-socket /path/to/node.socket \
  --node-config /path/to/config.json \
  --workdir /path/to/kupo-db \
  --host 0.0.0.0 \
  --port 1442 \
  --since "origin" \
  --match "*"  # Important: match all addresses
```

**Check Docker Compose**:
```yaml
kupo:
  command:
    - --match
    - "*"  # Ensure this is present
```

### 6. Network Mismatch

**Symptom**: Address exists but Kupo can't find it

**Solution**: Ensure Kupo is connected to the correct network

- Preprod: NetworkMagic 1
- Preview: NetworkMagic 2
- Mainnet: NetworkMagic 764824073

```bash
# Check Kupo configuration
docker exec kupo cat /config/config.json | grep NetworkMagic

# Or check native config
cat /path/to/kupo-config.json | grep NetworkMagic
```

### 7. Endpoint Path Issues

**Symptom**: 404 errors with correct address

**Solution**: The endpoint format is `/matches/{address}` where address is URL-encoded

The updated `KupoClient` now handles URL encoding automatically. If you're making direct requests:

```bash
# Correct format
curl "http://localhost:1442/matches/addr_test1...?unspent"

# Address will be automatically URL-encoded by the client
```

## Diagnostic Steps

### Step 1: Verify Kupo is Running

```bash
# Check health endpoint
curl http://localhost:1442/health

# Expected response:
# {"status":"synced"} or {"status":"ready"}
```

### Step 2: Test Basic Connectivity

```python
from offchain.kupo_client import KupoClient

client = KupoClient("http://localhost:1442")
connectivity = client.check_connectivity()
print(connectivity)
# Should show: {"connected": True, "sync_status": "synced"}
```

### Step 3: Test with Known Address

```python
# Use a known testnet address
test_address = "addr_test1qqr585tvlc7ylnqvz8pyqwauzrdu0mxag3m7q56grgmgu7sxu2hyfhlkwuxupa9d5085eunq2qywyhmh3htww2w7feusqmsn6z"

client = KupoClient("http://localhost:1442")
try:
    utxos = client.query_utxos_by_address(test_address)
    print(f"Found {len(utxos)} UTXOs")
except Exception as e:
    print(f"Error: {e}")
```

### Step 4: Check Kupo Logs

```bash
# Docker
docker logs kupo --tail 50

# Native
tail -f kupo.log
```

Look for:
- Connection errors
- Sync status
- Indexing progress
- Any error messages

### Step 5: Verify Network Configuration

```bash
# Check which network Kupo is connected to
curl http://localhost:1442/health | jq .

# Verify your address matches the network
cardano-cli address info --address <your-address>
```

## Quick Fix Checklist

- [ ] Kupo service is running (`curl http://localhost:1442/health`)
- [ ] Kupo URL is correct (`echo $KUPO_URL` or check code)
- [ ] Address format is valid (starts with `addr_test1` for testnet)
- [ ] Kupo is synced (health check shows "synced")
- [ ] Kupo is configured with `--match "*"` to index all addresses
- [ ] Network matches (Preprod/Preview/Mainnet)
- [ ] No firewall blocking port 1442

## Testing the Fix

After applying fixes, test with:

```bash
# Using the CLI (use python3 on macOS if python is not available)
python3 -m offchain.cli check-status \
  --contract-address addr_test1... \
  --kupo-url http://localhost:1442

# Or using Python directly
python3 -c "
from offchain.kupo_client import KupoClient
client = KupoClient('http://localhost:1442')
print(client.check_connectivity())
utxos = client.query_utxos_by_address('addr_test1...')
print(f'Found {len(utxos)} UTXOs')
"
```

## Additional Resources

- [Kupo Documentation](https://cardanosolutions.github.io/kupo)
- [Kupo GitHub Repository](https://github.com/CardanoSolutions/kupo)
- [Project Testnet Deployment Guide](./testnet-deployment.md)

## Still Having Issues?

If the problem persists:

1. Check Kupo version compatibility
2. Review Kupo logs for specific error messages
3. Verify cardano-node is running and accessible
4. Check network connectivity between services
5. Ensure sufficient disk space for Kupo database

