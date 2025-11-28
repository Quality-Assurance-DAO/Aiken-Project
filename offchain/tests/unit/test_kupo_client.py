"""Unit tests for KupoClient."""

import pytest
from unittest.mock import Mock, patch
from offchain.kupo_client import KupoClient


def test_kupo_client_connectivity_success():
    """Test successful Kupo connectivity check."""
    client = KupoClient("http://localhost:1442")
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "synced"}
    
    with patch.object(client.client, "get", return_value=mock_response):
        result = client.check_connectivity()
        
        assert result["connected"] is True
        assert result["sync_status"] == "synced"


def test_kupo_client_connectivity_failure():
    """Test Kupo connectivity check failure."""
    client = KupoClient("http://localhost:1442")
    
    with patch.object(client.client, "get", side_effect=Exception("Connection error")):
        result = client.check_connectivity()
        
        assert result["connected"] is False
        assert "error" in result


def test_kupo_client_query_utxos_by_address():
    """Test querying UTxOs by address."""
    client = KupoClient("http://localhost:1442")
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "transaction_id": "abc123",
            "output_index": 0,
            "address": "addr1...",
            "datum": {"cbor": "1234"},
        }
    ]
    mock_response.raise_for_status = Mock()
    
    with patch.object(client.client, "get", return_value=mock_response):
        result = client.query_utxos_by_address("addr1...")
        
        assert len(result) == 1
        assert result[0]["transaction_id"] == "abc123"


def test_kupo_client_parse_datum_from_utxo():
    """Test parsing datum from UTxO."""
    client = KupoClient("http://localhost:1442")
    
    utxo = {
        "transaction_id": "abc123",
        "output_index": 0,
        "datum": {"cbor": "1234"},
    }
    
    datum = client.parse_datum_from_utxo(utxo)
    assert datum is not None
    assert datum["cbor"] == "1234"


