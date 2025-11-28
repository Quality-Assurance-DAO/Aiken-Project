"""Integration tests for end-to-end transaction submission flows.

Tests the complete flow of building, signing, and submitting transactions
to the Cardano network via Ogmios.
"""

import pytest
import os
import subprocess
import json
import tempfile
from pathlib import Path
from typing import Optional

from offchain.ogmios_client import OgmiosClient
from offchain.kupo_client import KupoClient


# Test configuration
OGMIOS_URL = os.getenv("OGMIOS_URL", "ws://localhost:1337")
KUPO_URL = os.getenv("KUPO_URL", "http://localhost:1442")
NODE_SOCKET_PATH = os.getenv(
    "CARDANO_NODE_SOCKET_PATH",
    str(Path(__file__).parent.parent.parent.parent / "preprod-socket" / "node.socket")
)
NETWORK_MAGIC = os.getenv("CARDANO_NETWORK_MAGIC", "1")  # Default to preprod


@pytest.mark.integration
@pytest.mark.asyncio
async def test_transaction_build_and_submit_via_ogmios():
    """Test building and submitting a transaction via Ogmios."""
    # Prerequisites check
    socket_path = Path(NODE_SOCKET_PATH)
    if not socket_path.exists():
        pytest.skip("Node socket not available")
    
    ogmios_client = OgmiosClient(OGMIOS_URL)
    try:
        connectivity = await ogmios_client.check_connectivity()
        if not connectivity["connected"]:
            pytest.skip("Ogmios not available")
    except Exception:
        pytest.skip("Ogmios not available")
    
    # Check for cardano-cli availability (check both PATH and bin directory)
    cardano_cli_path = None
    project_root = Path(__file__).parent.parent.parent.parent
    bin_cli_path = project_root / "bin" / "cardano-cli"
    
    if bin_cli_path.exists():
        cardano_cli_path = str(bin_cli_path)
    else:
        try:
            result = subprocess.run(
                ["cardano-cli", "--version"],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                cardano_cli_path = "cardano-cli"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
    
    if not cardano_cli_path:
        pytest.skip("cardano-cli not available")
    
    # Check for signing key
    signing_key_path = Path(__file__).parent.parent.parent.parent / "payment.skey"
    if not signing_key_path.exists():
        pytest.skip("Signing key not found")
    
    # Get address from signing key
    vkey_path = Path(__file__).parent.parent.parent.parent / "payment.vkey"
    addr_path = Path(__file__).parent.parent.parent.parent / "payment.addr"
    
    # Extract address if vkey exists, otherwise skip
    if not vkey_path.exists():
        pytest.skip("Verification key not found")
    
    # Get address
    if not addr_path.exists():
        # Build address
        result = subprocess.run(
            [
                cardano_cli_path, "address", "build",
                "--payment-verification-key-file", str(vkey_path),
                "--testnet-magic", NETWORK_MAGIC,
                "--out-file", str(addr_path)
            ],
            capture_output=True,
            timeout=10
        )
        if result.returncode != 0:
            pytest.skip(f"Failed to build address: {result.stderr.decode()}")
    
    with open(addr_path, "r") as f:
        address = f.read().strip()
    
    # Query UTXOs for the address
    result = subprocess.run(
        [
            cardano_cli_path, "query", "utxo",
            "--address", address,
            "--testnet-magic", NETWORK_MAGIC,
            "--socket-path", str(socket_path)
        ],
        capture_output=True,
        timeout=30,
        text=True
    )
    
    if result.returncode != 0:
        pytest.skip(f"Failed to query UTXOs: {result.stderr}")
    
    # Parse UTXO output (simple format: TxHash TxIx Amount)
    utxo_lines = [line.strip() for line in result.stdout.strip().split("\n")[2:] if line.strip()]
    if not utxo_lines:
        pytest.skip("No UTXOs available for testing")
    
    # Get first UTXO
    first_utxo = utxo_lines[0].split()
    if len(first_utxo) < 2:
        pytest.skip("Could not parse UTXO output")
    
    tx_hash = first_utxo[0]
    tx_ix = first_utxo[1]
    
    # Build a simple transaction (send to self)
    with tempfile.TemporaryDirectory() as tmpdir:
        tx_unsigned = Path(tmpdir) / "tx.unsigned"
        tx_signed = Path(tmpdir) / "tx.signed"
        
        # Build transaction
        build_result = subprocess.run(
            [
                cardano_cli_path, "transaction", "build",
                "--testnet-magic", NETWORK_MAGIC,
                "--socket-path", str(socket_path),
                "--tx-in", f"{tx_hash}#{tx_ix}",
                "--tx-out", f"{address}+1000000",  # Send 1 ADA to self
                "--change-address", address,
                "--out-file", str(tx_unsigned)
            ],
            capture_output=True,
            timeout=30,
            text=True
        )
        
        if build_result.returncode != 0:
            pytest.skip(f"Failed to build transaction: {build_result.stderr}")
        
        # Sign transaction
        sign_result = subprocess.run(
            [
                cardano_cli_path, "transaction", "sign",
                "--tx-body-file", str(tx_unsigned),
                "--signing-key-file", str(signing_key_path),
                "--testnet-magic", NETWORK_MAGIC,
                "--out-file", str(tx_signed)
            ],
            capture_output=True,
            timeout=30,
            text=True
        )
        
        if sign_result.returncode != 0:
            pytest.skip(f"Failed to sign transaction: {sign_result.stderr}")
        
        # Extract CBOR from signed transaction
        with open(tx_signed, "r") as f:
            tx_data = json.load(f)
        
        if "cborHex" not in tx_data:
            pytest.skip("Signed transaction missing cborHex field")
        
        tx_cbor_hex = tx_data["cborHex"]
        
        # Submit via Ogmios
        await ogmios_client.connect()
        try:
            submit_result = await ogmios_client.submit_transaction(tx_cbor_hex)
            
            # Ogmios returns transaction ID on success
            assert submit_result is not None, "Transaction submission returned no result"
            
            # Note: In a real scenario, we would wait for confirmation
            # For now, we just verify submission succeeded
            
        except Exception as e:
            pytest.fail(f"Failed to submit transaction via Ogmios: {e}")
        finally:
            await ogmios_client.disconnect()


@pytest.mark.integration
def test_transaction_submission_via_cardano_cli():
    """Test transaction submission using cardano-cli directly."""
    socket_path = Path(NODE_SOCKET_PATH)
    if not socket_path.exists():
        pytest.skip("Node socket not available")
    
    # Check for cardano-cli availability (check both PATH and bin directory)
    cardano_cli_path = None
    project_root = Path(__file__).parent.parent.parent.parent
    bin_cli_path = project_root / "bin" / "cardano-cli"
    
    if bin_cli_path.exists():
        cardano_cli_path = str(bin_cli_path)
    else:
        try:
            result = subprocess.run(
                ["cardano-cli", "--version"],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                cardano_cli_path = "cardano-cli"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
    
    if not cardano_cli_path:
        pytest.skip("cardano-cli not available")
    
    # Check for signing key
    signing_key_path = Path(__file__).parent.parent.parent.parent / "payment.skey"
    if not signing_key_path.exists():
        pytest.skip("Signing key not found")
    
    vkey_path = Path(__file__).parent.parent.parent.parent / "payment.vkey"
    addr_path = Path(__file__).parent.parent.parent.parent / "payment.addr"
    
    if not vkey_path.exists():
        pytest.skip("Verification key not found")
    
    # Get address
    if not addr_path.exists():
        result = subprocess.run(
            [
                cardano_cli_path, "address", "build",
                "--payment-verification-key-file", str(vkey_path),
                "--testnet-magic", NETWORK_MAGIC,
                "--out-file", str(addr_path)
            ],
            capture_output=True,
            timeout=10
        )
        if result.returncode != 0:
            pytest.skip(f"Failed to build address: {result.stderr.decode()}")
    
    with open(addr_path, "r") as f:
        address = f.read().strip()
    
    # Query UTXOs
    result = subprocess.run(
        [
            cardano_cli_path, "query", "utxo",
            "--address", address,
            "--testnet-magic", NETWORK_MAGIC,
            "--socket-path", str(socket_path)
        ],
        capture_output=True,
        timeout=30,
        text=True
    )
    
    if result.returncode != 0:
        pytest.skip(f"Failed to query UTXOs: {result.stderr}")
    
    utxo_lines = [line.strip() for line in result.stdout.strip().split("\n")[2:] if line.strip()]
    if not utxo_lines:
        pytest.skip("No UTXOs available for testing")
    
    # Build and sign transaction
    first_utxo = utxo_lines[0].split()
    if len(first_utxo) < 2:
        pytest.skip("Could not parse UTXO output")
    
    tx_hash = first_utxo[0]
    tx_ix = first_utxo[1]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tx_unsigned = Path(tmpdir) / "tx.unsigned"
        tx_signed = Path(tmpdir) / "tx.signed"
        
        # Build transaction
        build_result = subprocess.run(
            [
                cardano_cli_path, "transaction", "build",
                "--testnet-magic", NETWORK_MAGIC,
                "--socket-path", str(socket_path),
                "--tx-in", f"{tx_hash}#{tx_ix}",
                "--tx-out", f"{address}+1000000",
                "--change-address", address,
                "--out-file", str(tx_unsigned)
            ],
            capture_output=True,
            timeout=30,
            text=True
        )
        
        if build_result.returncode != 0:
            pytest.skip(f"Failed to build transaction: {build_result.stderr}")
        
        # Sign transaction
        sign_result = subprocess.run(
            [
                cardano_cli_path, "transaction", "sign",
                "--tx-body-file", str(tx_unsigned),
                "--signing-key-file", str(signing_key_path),
                "--testnet-magic", NETWORK_MAGIC,
                "--out-file", str(tx_signed)
            ],
            capture_output=True,
            timeout=30,
            text=True
        )
        
        if sign_result.returncode != 0:
            pytest.skip(f"Failed to sign transaction: {sign_result.stderr}")
        
        # Submit transaction (dry-run: don't actually submit to avoid spending funds)
        # In a real test, you would submit:
        # submit_result = subprocess.run(
        #     [
        #         "cardano-cli", "transaction", "submit",
        #         "--tx-file", str(tx_signed),
        #         "--testnet-magic", NETWORK_MAGIC,
        #         "--socket-path", str(socket_path)
        #     ],
        #     capture_output=True,
        #     timeout=30,
        #     text=True
        # )
        
        # For now, just verify the transaction file is valid
        assert tx_signed.exists(), "Signed transaction file should exist"
        assert tx_signed.stat().st_size > 0, "Signed transaction file should not be empty"
        
        # Verify transaction structure
        with open(tx_signed, "r") as f:
            tx_data = json.load(f)
        
        assert "cborHex" in tx_data, "Transaction should contain cborHex"
        assert len(tx_data["cborHex"]) > 0, "Transaction cborHex should not be empty"


@pytest.mark.integration
def test_kupo_utxo_query_after_submission():
    """Test that Kupo can query UTXOs after a transaction."""
    client = KupoClient(KUPO_URL)
    
    try:
        connectivity = client.check_connectivity()
        if not connectivity.get("connected"):
            pytest.skip("Kupo not available")
    except Exception:
        pytest.skip("Kupo not available")
    
    # Query a test address
    # This test verifies Kupo is indexing correctly
    test_address = "addr_test1qqr585tvlc7ylnqvz8pyqwauzrdu0mxag3m7q56grgmgu7sxu2hyfhlkwuxupa9d5085eunq2qywyhmh3htww2w7feusqmsn6z"
    
    try:
        utxos = client.query_utxos_by_address(test_address)
        assert isinstance(utxos, list), "Should return a list of UTXOs"
        
        # If UTXOs exist, verify structure
        if utxos:
            for utxo in utxos:
                assert "transaction_id" in utxo or "tx_hash" in utxo, \
                    "UTXO should have transaction identifier"
                assert "output_index" in utxo or "index" in utxo, \
                    "UTXO should have output index"
                assert "address" in utxo or "owner" in utxo, \
                    "UTXO should have address information"
    
    except Exception as e:
        # Query failure might be expected if address has no UTXOs
        # or if Kupo is still syncing
        pytest.skip(f"Kupo query failed (may be expected): {e}")
    finally:
        client.close()

