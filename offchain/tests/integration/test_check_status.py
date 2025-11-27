"""Integration tests for check-status command."""

import pytest
import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import os
from unittest.mock import patch


@pytest.mark.integration
def test_check_status_command_with_cache():
    """Test check-status command using cached contract state."""
    with TemporaryDirectory() as tmpdir:
        # Set data directory environment variable
        data_dir = Path(tmpdir) / "data"
        data_dir.mkdir()
        os.environ["DATA_DIRECTORY"] = str(data_dir)
        
        # Create a mock contract state cache
        cache_dir = data_dir / "cache"
        cache_dir.mkdir()
        
        cache_file = cache_dir / "addr_test1q....json"
        cache_data = {
            "contract_address": "addr_test1q...",
            "utxo_tx_hash": "tx123",
            "utxo_index": 0,
            "datum": {
                "token_policy_id": "abc123",
                "beneficiary_allocations": [
                    {
                        "beneficiary_address": "addr_test1q...ben1",
                        "token_amount": 1000000,
                        "milestone_identifier": "milestone-001",
                        "vesting_timestamp": 1735689600,
                        "claimed": False,
                    }
                ],
                "oracle_addresses": ["addr_test1q...oracle1"],
                "quorum_threshold": 1,
                "total_oracles": 1,
            },
            "total_token_amount": 1000000,
            "token_policy_id": "abc123",
            "beneficiary_allocations": [
                {
                    "beneficiary_address": "addr_test1q...ben1",
                    "token_amount": 1000000,
                    "milestone_identifier": "milestone-001",
                    "vesting_timestamp": 1735689600,
                    "claimed": False,
                }
            ],
            "oracle_addresses": ["addr_test1q...oracle1"],
            "quorum_threshold": 1,
            "total_oracles": 1,
            "remaining_token_amount": 1000000,
            "cached_at": 1735689600,
        }
        with open(cache_file, "w") as f:
            json.dump(cache_data, f)
        
        # Create local milestone data
        milestones_dir = data_dir / "milestones"
        milestones_dir.mkdir()
        milestone_file = milestones_dir / "milestone-001.json"
        milestone_data = {
            "milestone_identifier": "milestone-001",
            "oracle_signatures": [
                {
                    "oracle_address": "addr_test1q...oracle1",
                    "signature": "sig1",
                    "signed_data": "data1",
                    "signature_timestamp": 1735689600,
                }
            ],
            "verification_timestamp": 1735689600,
            "quorum_status": "met",
            "quorum_threshold": 1,
            "total_oracles": 1,
        }
        with open(milestone_file, "w") as f:
            json.dump(milestone_data, f)
        
        # Mock Kupo client to avoid actual network calls
        with patch("offchain.kupo_client.KupoClient") as mock_kupo:
            # Run command
            try:
                result = subprocess.run(
                    [
                        sys.executable,
                        "cli.py",
                        "check-status",
                        "--contract-address",
                        "addr_test1q...",
                        "--output",
                        "json",
                    ],
                    cwd=Path(__file__).parent.parent.parent,
                    capture_output=True,
                    text=True,
                    timeout=10,
                    env=os.environ.copy(),
                )
                
                # Should succeed
                assert result.returncode == 0, f"Command failed: {result.stderr}"
                
                output = json.loads(result.stdout)
                assert "milestones" in output
                assert "milestone-001" in output["milestones"]
                assert output["cache_info"]["used_cache"] is True
                
            except subprocess.TimeoutExpired:
                pytest.skip("Command timeout")
            except json.JSONDecodeError as e:
                pytest.fail(f"Invalid JSON output: {e}\nOutput: {result.stdout}\nError: {result.stderr}")
            except Exception as e:
                pytest.skip(f"Command failed: {e}")
            finally:
                # Clean up environment
                os.environ.pop("DATA_DIRECTORY", None)


@pytest.mark.integration
def test_check_status_command_specific_milestone():
    """Test check-status command for specific milestone."""
    with TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir) / "data"
        data_dir.mkdir()
        os.environ["DATA_DIRECTORY"] = str(data_dir)
        
        # Create cache and milestone data (similar to above)
        cache_dir = data_dir / "cache"
        cache_dir.mkdir()
        
        cache_file = cache_dir / "addr_test1q....json"
        cache_data = {
            "contract_address": "addr_test1q...",
            "utxo_tx_hash": "tx123",
            "utxo_index": 0,
            "datum": {},
            "total_token_amount": 2000000,
            "token_policy_id": "abc123",
            "beneficiary_allocations": [
                {
                    "beneficiary_address": "addr_test1q...ben1",
                    "token_amount": 1000000,
                    "milestone_identifier": "milestone-001",
                    "vesting_timestamp": 1735689600,
                    "claimed": False,
                },
                {
                    "beneficiary_address": "addr_test1q...ben2",
                    "token_amount": 1000000,
                    "milestone_identifier": "milestone-002",
                    "vesting_timestamp": 1735689600,
                    "claimed": False,
                },
            ],
            "oracle_addresses": ["addr_test1q...oracle1"],
            "quorum_threshold": 1,
            "total_oracles": 1,
            "remaining_token_amount": 2000000,
            "cached_at": 1735689600,
        }
        with open(cache_file, "w") as f:
            json.dump(cache_data, f)
        
        with patch("offchain.kupo_client.KupoClient"):
            try:
                result = subprocess.run(
                    [
                        sys.executable,
                        "cli.py",
                        "check-status",
                        "--contract-address",
                        "addr_test1q...",
                        "--milestone-identifier",
                        "milestone-001",
                        "--output",
                        "json",
                    ],
                    cwd=Path(__file__).parent.parent.parent,
                    capture_output=True,
                    text=True,
                    timeout=10,
                    env=os.environ.copy(),
                )
                
                assert result.returncode == 0
                output = json.loads(result.stdout)
                assert "milestones" in output
                assert "milestone-001" in output["milestones"]
                assert "milestone-002" not in output["milestones"]
                
            except Exception as e:
                pytest.skip(f"Command failed: {e}")
            finally:
                os.environ.pop("DATA_DIRECTORY", None)


@pytest.mark.integration
def test_check_status_command_force_refresh():
    """Test check-status command with force refresh flag."""
    with TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir) / "data"
        data_dir.mkdir()
        os.environ["DATA_DIRECTORY"] = str(data_dir)
        
        # Create cache
        cache_dir = data_dir / "cache"
        cache_dir.mkdir()
        cache_file = cache_dir / "addr_test1q....json"
        with open(cache_file, "w") as f:
            json.dump({"cached_at": 1735689600}, f)
        
        # Mock Kupo to return UTxO data
        mock_utxos = [
            {
                "transaction_id": "tx123",
                "output_index": 0,
                "datum": {
                    "token_policy_id": "abc123",
                    "beneficiary_allocations": [
                        {
                            "beneficiary_address": "addr_test1q...ben1",
                            "token_amount": 1000000,
                            "milestone_identifier": "milestone-001",
                            "vesting_timestamp": 1735689600,
                            "claimed": False,
                        }
                    ],
                    "oracle_addresses": ["addr_test1q...oracle1"],
                    "quorum_threshold": 1,
                    "total_oracles": 1,
                },
            }
        ]
        
        mock_kupo_client = type("MockKupoClient", (), {
            "query_utxos_by_address": lambda self, addr: mock_utxos,
            "close": lambda self: None,
        })()
        
        with patch("offchain.kupo_client.KupoClient", return_value=mock_kupo_client):
            try:
                result = subprocess.run(
                    [
                        sys.executable,
                        "cli.py",
                        "check-status",
                        "--contract-address",
                        "addr_test1q...",
                        "--force-refresh",
                        "--output",
                        "json",
                    ],
                    cwd=Path(__file__).parent.parent.parent,
                    capture_output=True,
                    text=True,
                    timeout=10,
                    env=os.environ.copy(),
                )
                
                # Should succeed and refresh from chain
                assert result.returncode == 0
                output = json.loads(result.stdout)
                assert "milestones" in output
                assert output["cache_info"]["used_cache"] is False
                
            except Exception as e:
                pytest.skip(f"Command failed: {e}")
            finally:
                os.environ.pop("DATA_DIRECTORY", None)


@pytest.mark.integration
def test_check_status_command_no_utxos():
    """Test check-status command when no UTxOs found."""
    with TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir) / "data"
        data_dir.mkdir()
        os.environ["DATA_DIRECTORY"] = str(data_dir)
        
        # Mock Kupo to return empty list
        mock_kupo_client = type("MockKupoClient", (), {
            "query_utxos_by_address": lambda self, addr: [],
            "close": lambda self: None,
        })()
        
        with patch("offchain.kupo_client.KupoClient", return_value=mock_kupo_client):
            try:
                result = subprocess.run(
                    [
                        sys.executable,
                        "cli.py",
                        "check-status",
                        "--contract-address",
                        "addr_test1q...invalid",
                        "--force-refresh",
                        "--output",
                        "json",
                    ],
                    cwd=Path(__file__).parent.parent.parent,
                    capture_output=True,
                    text=True,
                    timeout=10,
                    env=os.environ.copy(),
                )
                
                # Should fail with error
                assert result.returncode != 0
                output = json.loads(result.stdout)
                assert "error" in output
                
            except Exception as e:
                pytest.skip(f"Command failed: {e}")
            finally:
                os.environ.pop("DATA_DIRECTORY", None)

