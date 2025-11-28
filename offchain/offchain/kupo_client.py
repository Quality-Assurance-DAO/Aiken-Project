"""Kupo HTTP client for UTxO queries."""

import httpx
from typing import Optional, Dict, Any, List
from urllib.parse import quote


class KupoClient:
    """HTTP client for Kupo UTxO indexer."""

    def __init__(self, url: str = "http://localhost:1442"):
        """Initialize Kupo client."""
        self.url = url.rstrip("/")
        self.client = httpx.Client(timeout=30.0)

    def check_connectivity(self) -> Dict[str, Any]:
        """Check if Kupo service is available."""
        try:
            # Kupo /health endpoint returns Prometheus metrics by default
            # Need to request JSON format explicitly
            response = self.client.get(
                f"{self.url}/health",
                headers={"Accept": "application/json"}
            )
            if response.status_code == 200:
                health_data = response.json()
                # Kupo returns different structure than expected
                # Check for connection_status or status field
                connection_status = health_data.get("connection_status", "unknown")
                
                # Determine sync status from various possible fields
                if health_data.get("status") == "synced":
                    sync_status = "synced"
                elif connection_status == "connected":
                    network_sync = health_data.get("network_synchronization")
                    if isinstance(network_sync, (int, float)):
                        sync_status = "synced" if network_sync > 0.9 else "syncing"
                    else:
                        sync_status = network_sync or "synced"
                else:
                    sync_status = health_data.get("status", "unknown")
                
                return {
                    "connected": True,
                    "sync_status": sync_status,
                    "checkpoint": health_data.get("most_recent_checkpoint"),
                    "synchronization": health_data.get("network_synchronization"),
                }
            else:
                return {"connected": False, "error": f"HTTP {response.status_code}"}
        except httpx.RequestError as e:
            return {"connected": False, "error": str(e)}
        except Exception as e:
            return {"connected": False, "error": str(e)}

    def query_utxos_by_address(self, address: str) -> List[Dict[str, Any]]:
        """Query UTxOs by contract address using /matches endpoint.
        
        Note: Kupo's /matches/{pattern} endpoint requires patterns to be registered.
        When Kupo is configured with --match "*", it indexes all addresses but still
        requires pattern registration for direct queries. As a workaround, we query
        the wildcard pattern and filter client-side by address.
        
        Args:
            address: Cardano address to query (e.g., addr_test1...)
            
        Returns:
            List of UTxO dictionaries matching the address
            
        Raises:
            ConnectionError: If Kupo service is unavailable or unreachable
            ValueError: If the response cannot be parsed or endpoint is not found
        """
        try:
            # Kupo's /matches/{pattern} endpoint requires patterns to be registered first.
            # When Kupo is configured with --match "*", it indexes all addresses but
            # the API still requires pattern registration. As a workaround, we query
            # the wildcard pattern (which is always registered when using --match "*")
            # and filter the results client-side by address.
            # Note: Kupo expects ?unspent as a flag without a value, not ?unspent=true
            response = self.client.get(
                f"{self.url}/matches/*?unspent"
            )
            
            response.raise_for_status()
            all_utxos = response.json()
            
            # Filter UTXOs by the target address
            # Kupo returns UTXOs with an "address" field
            matching_utxos = [
                utxo for utxo in all_utxos
                if utxo.get("address") == address
            ]
            
            return matching_utxos
            
        except httpx.HTTPStatusError as e:
            # Handle HTTP errors with better messages
            if e.response.status_code == 404:
                raise ValueError(
                    f"Kupo endpoint not found. "
                    f"Verify Kupo is running at {self.url} and configured with --match \"*\". "
                    f"Check documentation: https://cardanosolutions.github.io/kupo"
                )
            raise ConnectionError(f"Kupo HTTP error {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            raise ConnectionError(
                f"Failed to connect to Kupo at {self.url}. "
                f"Ensure Kupo is running and accessible. Error: {e}"
            )
        except Exception as e:
            raise ValueError(f"Failed to parse Kupo response: {e}")

    def parse_datum_from_utxo(self, utxo: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract and parse contract datum from UTxO response."""
        if "datum" in utxo:
            datum = utxo["datum"]
            if isinstance(datum, dict):
                return datum
            elif isinstance(datum, str):
                # If datum is a hex string, might need to decode
                # For now, return as-is
                return {"cbor": datum}
        return None

    def close(self):
        """Close HTTP client."""
        self.client.close()

