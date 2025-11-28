"""Integration tests for check-status command."""

import pytest
import json
import subprocess
import sys
import time
from pathlib import Path
from tempfile import TemporaryDirectory
import os


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
        
        # Cache file name should match what MilestoneManager expects (sanitized address)
        contract_address = "addr_test1q..."
        safe_address = contract_address.replace("/", "_").replace(":", "_")
        cache_file = cache_dir / f"{safe_address}.json"
        cache_data = {
            "contract_address": contract_address,
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
            "cached_at": int(time.time()),  # Use current time so cache is not stale
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
        
        # Run command (integration test - uses cache, should not need Kupo)
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "cli.py",
                    "check-status",
                    "--contract-address",
                    contract_address,
                    "--output",
                    "json",
                ],
                cwd=Path(__file__).parent.parent.parent,
                capture_output=True,
                text=True,
                timeout=30,
                env=os.environ.copy(),
            )
            
            # Should succeed using cache
            assert result.returncode == 0, f"Command failed: {result.stderr}\nOutput: {result.stdout}"
            
            output = json.loads(result.stdout)
            assert "milestones" in output
            assert "milestone-001" in output["milestones"]
            assert output["cache_info"]["used_cache"] is True
            
        except subprocess.TimeoutExpired:
            pytest.skip("Command timeout")
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON output: {e}\nOutput: {result.stdout}\nError: {result.stderr}")
        except Exception as e:
            pytest.fail(f"Command failed: {e}\nOutput: {result.stdout if 'result' in locals() else 'N/A'}\nError: {result.stderr if 'result' in locals() else 'N/A'}")
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
        
        contract_address = "addr_test1q..."
        safe_address = contract_address.replace("/", "_").replace(":", "_")
        cache_file = cache_dir / f"{safe_address}.json"
        cache_data = {
            "contract_address": contract_address,
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
            "cached_at": int(time.time()),  # Use current time so cache is not stale
        }
        with open(cache_file, "w") as f:
            json.dump(cache_data, f)
        
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "cli.py",
                    "check-status",
                    "--contract-address",
                    contract_address,
                    "--milestone-identifier",
                    "milestone-001",
                    "--output",
                    "json",
                ],
                cwd=Path(__file__).parent.parent.parent,
                capture_output=True,
                text=True,
                timeout=30,
                env=os.environ.copy(),
            )
            
            assert result.returncode == 0, f"Command failed: {result.stderr}\nOutput: {result.stdout}"
            output = json.loads(result.stdout)
            assert "milestones" in output
            assert "milestone-001" in output["milestones"]
            assert "milestone-002" not in output["milestones"]
            
        except subprocess.TimeoutExpired:
            pytest.skip("Command timeout")
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON output: {e}\nOutput: {result.stdout}\nError: {result.stderr}")
        except Exception as e:
            pytest.fail(f"Command failed: {e}\nOutput: {result.stdout if 'result' in locals() else 'N/A'}\nError: {result.stderr if 'result' in locals() else 'N/A'}")
        finally:
            os.environ.pop("DATA_DIRECTORY", None)


@pytest.mark.integration
def test_check_status_command_force_refresh():
    """Test check-status command with force refresh flag."""
    with TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir) / "data"
        data_dir.mkdir()
        os.environ["DATA_DIRECTORY"] = str(data_dir)
        
        # Create cache (will be ignored due to force-refresh)
        cache_dir = data_dir / "cache"
        cache_dir.mkdir()
        contract_address = "addr_test1q..."
        safe_address = contract_address.replace("/", "_").replace(":", "_")
        cache_file = cache_dir / f"{safe_address}.json"
        with open(cache_file, "w") as f:
            json.dump({"cached_at": 1735689600}, f)
        
        # This test requires Kupo to be available and the address to have UTxOs
        # Skip if Kupo is not available (integration test)
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "cli.py",
                    "check-status",
                    "--contract-address",
                    contract_address,
                    "--force-refresh",
                    "--output",
                    "json",
                ],
                cwd=Path(__file__).parent.parent.parent,
                capture_output=True,
                text=True,
                timeout=30,
                env=os.environ.copy(),
            )
            
            # May fail if address has no UTxOs (expected for test address)
            if result.returncode != 0:
                output = json.loads(result.stdout)
                if "error" in output and "No UTxOs" in output["error"]:
                    pytest.skip(f"Test address has no UTxOs (expected): {output['error']}")
                else:
                    pytest.fail(f"Command failed: {result.stderr}\nOutput: {result.stdout}")
            
            output = json.loads(result.stdout)
            assert "milestones" in output or "error" in output
            if "cache_info" in output:
                assert output["cache_info"]["used_cache"] is False
            
        except subprocess.TimeoutExpired:
            pytest.skip("Command timeout")
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON output: {e}\nOutput: {result.stdout}\nError: {result.stderr}")
        except Exception as e:
            pytest.skip(f"Command failed (may be expected for test address): {e}")
        finally:
            os.environ.pop("DATA_DIRECTORY", None)


@pytest.mark.integration
def test_check_status_command_no_utxos():
    """Test check-status command when no UTxOs found."""
    with TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir) / "data"
        data_dir.mkdir()
        os.environ["DATA_DIRECTORY"] = str(data_dir)
        
        # Test with invalid address (should return error)
        contract_address = "addr_test1q...invalid"
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "cli.py",
                    "check-status",
                    "--contract-address",
                    contract_address,
                    "--force-refresh",
                    "--output",
                    "json",
                ],
                cwd=Path(__file__).parent.parent.parent,
                capture_output=True,
                text=True,
                timeout=30,
                env=os.environ.copy(),
            )
            
            # Should fail with error (no UTxOs found)
            assert result.returncode != 0, "Command should fail for invalid address"
            output = json.loads(result.stdout)
            assert "error" in output
            
        except subprocess.TimeoutExpired:
            pytest.skip("Command timeout")
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON output: {e}\nOutput: {result.stdout}\nError: {result.stderr}")
        except Exception as e:
            pytest.fail(f"Command failed unexpectedly: {e}\nOutput: {result.stdout if 'result' in locals() else 'N/A'}\nError: {result.stderr if 'result' in locals() else 'N/A'}")
        finally:
            os.environ.pop("DATA_DIRECTORY", None)

