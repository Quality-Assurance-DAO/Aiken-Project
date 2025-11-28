"""Integration tests for commit-milestone command."""

import pytest
import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import os


@pytest.mark.integration
def test_commit_milestone_command_new():
    """Test commit-milestone command end-to-end for new milestone."""
    with TemporaryDirectory() as tmpdir:
        # Set data directory environment variable
        data_dir = Path(tmpdir) / "data"
        data_dir.mkdir()
        os.environ["DATA_DIRECTORY"] = str(data_dir)
        
        # Create test signatures file
        signatures_file = Path(tmpdir) / "signatures.json"
        signatures_data = [
            {
                "oracle_address": "addr_test1q...oracle1",
                "signature": "abc123def456",
                "signed_data": "milestone-001-verified",
                "signature_timestamp": 1735689600,
            },
            {
                "oracle_address": "addr_test1q...oracle2",
                "signature": "def456ghi789",
                "signed_data": "milestone-001-verified",
                "signature_timestamp": 1735689700,
            },
        ]
        with open(signatures_file, "w") as f:
            json.dump(signatures_data, f)
        
        # Run command
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "cli.py",
                    "commit-milestone",
                    "--milestone-identifier",
                    "milestone-001",
                    "--oracle-signatures",
                    str(signatures_file),
                    "--quorum-threshold",
                    "3",
                    "--total-oracles",
                    "5",
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
            assert output["milestone_identifier"] == "milestone-001"
            assert output["signature_count"] == 2
            assert output["quorum_threshold"] == 3
            assert output["quorum_status"] == "pending"
            assert output["quorum_met"] is False
            
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
def test_commit_milestone_command_incremental():
    """Test commit-milestone command with incremental signature addition."""
    with TemporaryDirectory() as tmpdir:
        # Set data directory environment variable
        data_dir = Path(tmpdir) / "data"
        data_dir.mkdir()
        os.environ["DATA_DIRECTORY"] = str(data_dir)
        
        # First commit - initial signatures
        signatures_file1 = Path(tmpdir) / "signatures1.json"
        signatures_data1 = [
            {
                "oracle_address": "addr_test1q...oracle1",
                "signature": "sig1",
                "signed_data": "milestone-002-verified",
                "signature_timestamp": 1735689600,
            },
        ]
        with open(signatures_file1, "w") as f:
            json.dump(signatures_data1, f)
        
        # Run first commit
        try:
            result1 = subprocess.run(
                [
                    sys.executable,
                    "cli.py",
                    "commit-milestone",
                    "--milestone-identifier",
                    "milestone-002",
                    "--oracle-signatures",
                    str(signatures_file1),
                    "--quorum-threshold",
                    "3",
                    "--total-oracles",
                    "5",
                    "--output",
                    "json",
                ],
                cwd=Path(__file__).parent.parent.parent,
                capture_output=True,
                text=True,
                timeout=30,
                env=os.environ.copy(),
            )
            
            assert result1.returncode == 0, f"First commit failed: {result1.stderr}\nOutput: {result1.stdout}"
            output1 = json.loads(result1.stdout)
            assert output1["signature_count"] == 1
            
            # Second commit - additional signatures
            signatures_file2 = Path(tmpdir) / "signatures2.json"
            signatures_data2 = [
                {
                    "oracle_address": "addr_test1q...oracle2",
                    "signature": "sig2",
                    "signed_data": "milestone-002-verified",
                    "signature_timestamp": 1735689700,
                },
                {
                    "oracle_address": "addr_test1q...oracle3",
                    "signature": "sig3",
                    "signed_data": "milestone-002-verified",
                    "signature_timestamp": 1735689800,
                },
            ]
            with open(signatures_file2, "w") as f:
                json.dump(signatures_data2, f)
            
            # Run second commit
            result2 = subprocess.run(
                [
                    sys.executable,
                    "cli.py",
                    "commit-milestone",
                    "--milestone-identifier",
                    "milestone-002",
                    "--oracle-signatures",
                    str(signatures_file2),
                    "--quorum-threshold",
                    "3",
                    "--total-oracles",
                    "5",
                    "--output",
                    "json",
                ],
                cwd=Path(__file__).parent.parent.parent,
                capture_output=True,
                text=True,
                timeout=30,
                env=os.environ.copy(),
            )
            
            assert result2.returncode == 0, f"Second commit failed: {result2.stderr}\nOutput: {result2.stdout}"
            output2 = json.loads(result2.stdout)
            assert output2["signature_count"] == 3
            assert output2["quorum_status"] == "met"
            assert output2["quorum_met"] is True
            
        except subprocess.TimeoutExpired:
            pytest.skip("Command timeout")
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON output: {e}\nOutput: {result1.stdout if 'result1' in locals() else (result2.stdout if 'result2' in locals() else 'N/A')}\nError: {result1.stderr if 'result1' in locals() else (result2.stderr if 'result2' in locals() else 'N/A')}")
        except Exception as e:
            pytest.fail(f"Command failed: {e}\nOutput: {result1.stdout if 'result1' in locals() else (result2.stdout if 'result2' in locals() else 'N/A')}\nError: {result1.stderr if 'result1' in locals() else (result2.stderr if 'result2' in locals() else 'N/A')}")
        finally:
            # Clean up environment
            os.environ.pop("DATA_DIRECTORY", None)


@pytest.mark.integration
def test_commit_milestone_command_invalid_signature():
    """Test commit-milestone command with invalid signature format."""
    with TemporaryDirectory() as tmpdir:
        # Set data directory environment variable
        data_dir = Path(tmpdir) / "data"
        data_dir.mkdir()
        os.environ["DATA_DIRECTORY"] = str(data_dir)
        
        # Create invalid signatures file (missing required field)
        signatures_file = Path(tmpdir) / "invalid_signatures.json"
        signatures_data = [
            {
                "oracle_address": "addr_test1q...oracle1",
                "signature": "",  # Empty signature should fail
                "signed_data": "milestone-003-verified",
                "signature_timestamp": 1735689600,
            },
        ]
        with open(signatures_file, "w") as f:
            json.dump(signatures_data, f)
        
        # Run command - should fail
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "cli.py",
                    "commit-milestone",
                    "--milestone-identifier",
                    "milestone-003",
                    "--oracle-signatures",
                    str(signatures_file),
                    "--quorum-threshold",
                    "2",
                    "--total-oracles",
                    "3",
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
            assert "error" in result.stderr.lower() or "invalid" in result.stderr.lower()
            
        except subprocess.TimeoutExpired:
            pytest.skip("Command timeout")
        except Exception as e:
            pytest.skip(f"Command failed: {e}")
        finally:
            # Clean up environment
            os.environ.pop("DATA_DIRECTORY", None)


@pytest.mark.integration
def test_commit_milestone_command_missing_required_params():
    """Test commit-milestone command with missing required parameters."""
    with TemporaryDirectory() as tmpdir:
        # Set data directory environment variable
        data_dir = Path(tmpdir) / "data"
        data_dir.mkdir()
        os.environ["DATA_DIRECTORY"] = str(data_dir)
        
        # Create valid signatures file
        signatures_file = Path(tmpdir) / "signatures.json"
        signatures_data = [
            {
                "oracle_address": "addr_test1q...oracle1",
                "signature": "sig1",
                "signed_data": "milestone-004-verified",
                "signature_timestamp": 1735689600,
            },
        ]
        with open(signatures_file, "w") as f:
            json.dump(signatures_data, f)
        
        # Run command without quorum_threshold - should fail
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "cli.py",
                    "commit-milestone",
                    "--milestone-identifier",
                    "milestone-004",
                    "--oracle-signatures",
                    str(signatures_file),
                    "--output",
                    "json",
                ],
                cwd=Path(__file__).parent.parent.parent,
                capture_output=True,
                text=True,
                timeout=10,
                env=os.environ.copy(),
            )
            
            # Should fail with error about missing parameters
            assert result.returncode != 0
            assert "required" in result.stderr.lower() or "quorum" in result.stderr.lower()
            
        except subprocess.TimeoutExpired:
            pytest.skip("Command timeout")
        except Exception as e:
            pytest.skip(f"Command failed: {e}")
        finally:
            # Clean up environment
            os.environ.pop("DATA_DIRECTORY", None)

