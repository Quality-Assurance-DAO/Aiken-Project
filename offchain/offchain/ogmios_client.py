"""Ogmios WebSocket client for Cardano blockchain queries."""

import asyncio
import json
from typing import Optional, Dict, Any
import websockets
from websockets.exceptions import ConnectionClosed, InvalidURI


class OgmiosClient:
    """WebSocket JSON-RPC client for Ogmios."""

    def __init__(self, url: str = "ws://localhost:1337"):
        """Initialize Ogmios client."""
        self.url = url
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.request_id = 0

    async def connect(self) -> bool:
        """Establish WebSocket connection to Ogmios."""
        try:
            self.websocket = await websockets.connect(self.url)
            return True
        except (ConnectionRefusedError, InvalidURI, Exception) as e:
            return False

    async def disconnect(self):
        """Close WebSocket connection."""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None

    async def _send_request(self, method: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Send JSON-RPC request and wait for response."""
        if not self.websocket:
            raise ConnectionError("Not connected to Ogmios")

        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "id": self.request_id,
        }
        if params:
            request["params"] = params

        await self.websocket.send(json.dumps(request))
        response = await self.websocket.recv()
        return json.loads(response)

    async def check_connectivity(self) -> Dict[str, Any]:
        """Check if Ogmios service is available."""
        try:
            if not await self.connect():
                return {"connected": False, "error": "Connection failed"}
            
            # Try a simple query to verify connectivity
            try:
                response = await self._send_request("queryLedgerState/protocolParameters")
                await self.disconnect()
                return {
                    "connected": True,
                    "version": response.get("result", {}).get("version", "unknown"),
                }
            except Exception as e:
                await self.disconnect()
                return {"connected": False, "error": str(e)}
        except Exception as e:
            return {"connected": False, "error": str(e)}

    async def query_protocol_parameters(self) -> Dict[str, Any]:
        """Query current protocol parameters."""
        response = await self._send_request("queryLedgerState/protocolParameters")
        return response.get("result", {})

    async def submit_transaction(self, transaction_cbor: str) -> Dict[str, Any]:
        """Submit transaction via Ogmios."""
        response = await self._send_request(
            "submitTransaction",
            {"transaction": {"cbor": transaction_cbor}},
        )
        return response.get("result", {})

