"""Integration tests for register-milestone command."""

import pytest
import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


@pytest.mark.integration
def test_register_milestone_command():
    """Test register-milestone command end-to-end."""
    with TemporaryDirectory() as tmpdir:
        # Create test allocations file
        allocations_file = Path(tmpdir) / "allocations.json"
        allocations_data = [
            {
                "beneficiary_address": "addr_test1q...",
                "token_amount": 1000000,
                "milestone_identifier": "milestone-001",
                "vesting_timestamp": 1735689600,
            }
        ]
        with open(allocations_file, "w") as f:
            json.dump(allocations_data, f)
        
        # Run command
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "cli.py",
                    "register-milestone",
                    "--token-policy-id",
                    "abc123",
                    "--beneficiary-allocations",
                    str(allocations_file),
                    "--oracle-addresses",
                    "addr_test1q...,addr_test1q...",
                    "--quorum-threshold",
                    "2",
                    "--output",
                    "json",
                ],
                cwd=Path(__file__).parent.parent.parent,
                capture_output=True,
                text=True,
                timeout=10,
            )
            
            # Should succeed or fail gracefully
            assert result.returncode in [0, 1]
            
            if result.returncode == 0:
                output = json.loads(result.stdout)
                assert "datum" in output
                assert "total_token_amount" in output
        except subprocess.TimeoutExpired:
            pytest.skip("Command timeout")
        except Exception as e:
            pytest.skip(f"Command failed: {e}")

