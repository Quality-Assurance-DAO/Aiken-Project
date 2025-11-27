"""Unit tests for OgmiosClient."""

import pytest
import json
from unittest.mock import AsyncMock, patch
from offchain.ogmios_client import OgmiosClient


@pytest.mark.asyncio
async def test_ogmios_client_connectivity_success():
    """Test successful Ogmios connectivity check."""
    client = OgmiosClient("ws://localhost:1337")
    
    with patch("websockets.connect") as mock_connect:
        mock_ws = AsyncMock()
        mock_ws.send = AsyncMock()
        mock_ws.recv = AsyncMock(return_value=json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "result": {"version": "5.6.0"}
        }))
        mock_ws.close = AsyncMock()
        mock_connect.return_value.__aenter__.return_value = mock_ws
        
        result = await client.check_connectivity()
        
        assert result["connected"] is True
        assert "version" in result


@pytest.mark.asyncio
async def test_ogmios_client_connectivity_failure():
    """Test Ogmios connectivity check failure."""
    client = OgmiosClient("ws://localhost:1337")
    
    with patch("websockets.connect", side_effect=ConnectionRefusedError()):
        result = await client.check_connectivity()
        
        assert result["connected"] is False
        assert "error" in result


@pytest.mark.asyncio
async def test_ogmios_client_query_protocol_parameters():
    """Test querying protocol parameters."""
    client = OgmiosClient("ws://localhost:1337")
    
    with patch("websockets.connect") as mock_connect:
        mock_ws = AsyncMock()
        mock_ws.send = AsyncMock()
        mock_ws.recv = AsyncMock(return_value=json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "minFeeA": 44,
                "minFeeB": 155381,
            }
        }))
        mock_connect.return_value.__aenter__.return_value = mock_ws
        
        client.websocket = mock_ws
        result = await client.query_protocol_parameters()
        
        assert "minFeeA" in result
        assert "minFeeB" in result

