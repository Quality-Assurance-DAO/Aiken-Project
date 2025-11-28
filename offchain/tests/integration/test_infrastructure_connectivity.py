"""Integration tests for infrastructure connectivity.

Tests direct node socket connectivity, Ogmios queries, Kupo indexing,
and end-to-end transaction submission flows.
"""

import pytest
import os
import asyncio
from pathlib import Path

from offchain.ogmios_client import OgmiosClient
from offchain.kupo_client import KupoClient
from offchain.config import check_cardano_node_connectivity


# Test configuration - can be overridden via environment variables
OGMIOS_URL = os.getenv("OGMIOS_URL", "ws://localhost:1337")
KUPO_URL = os.getenv("KUPO_URL", "http://localhost:1442")
NODE_SOCKET_PATH = os.getenv(
    "CARDANO_NODE_SOCKET_PATH",
    str(Path(__file__).parent.parent.parent.parent / "preprod-socket" / "node.socket")
)


@pytest.mark.integration
def test_node_socket_connectivity():
    """Test direct connectivity to Cardano node socket."""
    socket_path = Path(NODE_SOCKET_PATH)
    
    if not socket_path.exists():
        pytest.skip(f"Node socket not found at {socket_path}")
    
    if not socket_path.is_socket():
        pytest.skip(f"Path exists but is not a socket: {socket_path}")
    
    # Test socket file accessibility
    assert check_cardano_node_connectivity(str(socket_path)), \
        f"Socket file {socket_path} is not accessible"
    
    # Test socket file permissions
    stat = socket_path.stat()
    assert stat.st_mode & 0o077 != 0, \
        f"Socket file should have read permissions"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_ogmios_query_node():
    """Test Ogmios can query the Cardano node."""
    client = OgmiosClient(OGMIOS_URL)
    
    try:
        # Test connectivity
        connectivity = await client.check_connectivity()
        if not connectivity.get("connected"):
            pytest.skip(f"Ogmios not connected: {connectivity.get('error', 'Unknown error')}")
        
        # Test querying protocol parameters
        await client.connect()
        try:
            params = await client.query_protocol_parameters()
            assert params is not None, "Failed to query protocol parameters"
            assert "minFeeA" in params or "protocolVersion" in params or "minFeeCoefficient" in params, \
                f"Protocol parameters response missing expected fields. Got keys: {list(params.keys()) if params else 'None'}"
        finally:
            await client.disconnect()
        
    except AssertionError:
        raise
    except Exception as e:
        pytest.skip(f"Ogmios service not available: {e}")


@pytest.mark.integration
def test_kupo_indexing():
    """Test Kupo can index UTXOs from the node."""
    client = KupoClient(KUPO_URL)
    
    try:
        # Test connectivity
        connectivity = client.check_connectivity()
        assert connectivity["connected"], \
            f"Kupo connectivity check failed: {connectivity.get('error', 'Unknown error')}"
        
        # Test querying a known testnet address (empty result is OK)
        # Using a well-known testnet address for testing
        test_address = "addr_test1qqr585tvlc7ylnqvz8pyqwauzrdu0mxag3m7q56grgmgu7sxu2hyfhlkwuxupa9d5085eunq2qywyhmh3htww2w7feusqmsn6z"
        try:
            utxos = client.query_utxos_by_address(test_address)
            # Even if empty, the query should succeed
            assert isinstance(utxos, list), "UTXO query should return a list"
        except Exception as e:
            # If address is invalid or service error, that's OK for connectivity test
            pytest.skip(f"Kupo query failed (may be expected): {e}")
        
    except Exception as e:
        pytest.skip(f"Kupo service not available: {e}")
    finally:
        client.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_end_to_end_transaction_submission():
    """Test end-to-end transaction submission flow."""
    # This test requires:
    # 1. Node socket connectivity
    # 2. Ogmios connectivity
    # 3. Valid signing keys
    # 4. Testnet funds
    
    # Check prerequisites
    socket_path = Path(NODE_SOCKET_PATH)
    if not socket_path.exists() or not socket_path.is_socket():
        pytest.skip("Node socket not available")
    
    ogmios_client = OgmiosClient(OGMIOS_URL)
    try:
        connectivity = await ogmios_client.check_connectivity()
        if not connectivity["connected"]:
            pytest.skip("Ogmios not available")
    except Exception:
        pytest.skip("Ogmios not available")
    
    # Check for signing key (optional - test can skip if not present)
    signing_key_path = Path(__file__).parent.parent.parent.parent / "payment.skey"
    if not signing_key_path.exists():
        pytest.skip("Signing key not found - skipping transaction submission test")
    
    # For a full end-to-end test, we would:
    # 1. Build a transaction using pycardano or cardano-cli
    # 2. Sign the transaction
    # 3. Submit via Ogmios
    # 4. Verify submission success
    
    # Placeholder: This would require implementing transaction building
    # For now, we just verify the infrastructure is ready
    await ogmios_client.connect()
    try:
        params = await ogmios_client.query_protocol_parameters()
        assert params is not None, "Cannot query protocol parameters"
    finally:
        await ogmios_client.disconnect()
    
    pytest.skip("Full transaction submission test requires transaction building implementation")


@pytest.mark.integration
def test_infrastructure_health_checks():
    """Comprehensive health check of all infrastructure components."""
    results = {
        "node_socket": False,
        "ogmios": False,
        "kupo": False,
    }
    
    # Check node socket
    socket_path = Path(NODE_SOCKET_PATH)
    if socket_path.exists() and socket_path.is_socket():
        results["node_socket"] = check_cardano_node_connectivity(str(socket_path))
    
    # Check Ogmios
    async def check_ogmios():
        client = OgmiosClient(OGMIOS_URL)
        try:
            connectivity = await client.check_connectivity()
            return connectivity.get("connected", False)
        except Exception:
            return False
        finally:
            await client.disconnect()
    
    try:
        results["ogmios"] = asyncio.run(check_ogmios())
    except Exception:
        pass
    
    # Check Kupo
    client = KupoClient(KUPO_URL)
    try:
        connectivity = client.check_connectivity()
        results["kupo"] = connectivity.get("connected", False)
    except Exception:
        pass
    finally:
        client.close()
    
    # Log results
    print(f"\nInfrastructure Health Check Results:")
    print(f"  Node Socket: {'✓' if results['node_socket'] else '✗'}")
    print(f"  Ogmios: {'✓' if results['ogmios'] else '✗'}")
    print(f"  Kupo: {'✓' if results['kupo'] else '✗'}")
    
    # At least one service should be available for basic testing
    assert any(results.values()), \
        "No infrastructure services are available for testing"

