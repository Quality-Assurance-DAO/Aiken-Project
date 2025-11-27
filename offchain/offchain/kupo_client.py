"""Kupo HTTP client for UTxO queries."""

import httpx
from typing import Optional, Dict, Any, List


class KupoClient:
    """HTTP client for Kupo UTxO indexer."""

    def __init__(self, url: str = "http://localhost:1442"):
        """Initialize Kupo client."""
        self.url = url.rstrip("/")
        self.client = httpx.Client(timeout=30.0)

    def check_connectivity(self) -> Dict[str, Any]:
        """Check if Kupo service is available."""
        try:
            response = self.client.get(f"{self.url}/health")
            if response.status_code == 200:
                return {
                    "connected": True,
                    "sync_status": response.json().get("status", "unknown"),
                }
            else:
                return {"connected": False, "error": f"HTTP {response.status_code}"}
        except httpx.RequestError as e:
            return {"connected": False, "error": str(e)}
        except Exception as e:
            return {"connected": False, "error": str(e)}

    def query_utxos_by_address(self, address: str) -> List[Dict[str, Any]]:
        """Query UTxOs by contract address using /matches endpoint."""
        try:
            response = self.client.get(
                f"{self.url}/matches/{address}",
                params={"unspent": "true"},
            )
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            raise ConnectionError(f"Failed to query Kupo: {e}")
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

