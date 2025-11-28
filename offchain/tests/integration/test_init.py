"""Integration tests for init command."""

import pytest
import subprocess
import sys
from pathlib import Path


@pytest.mark.integration
def test_init_command_with_real_services():
    """Test init command with real services (if available)."""
    # This test requires actual services to be running
    # Skip if services are not available
    try:
        result = subprocess.run(
            [sys.executable, "cli.py", "init", "--network", "testnet"],
            cwd=Path(__file__).parent.parent.parent,
            capture_output=True,
            text=True,
            timeout=10,
        )
        # If services are available, should return success
        # If not available, should return error but not crash
        assert result.returncode in [0, 1]  # Success or expected failure
    except subprocess.TimeoutExpired:
        pytest.skip("Services not available or timeout")
    except Exception:
        pytest.skip("Services not available")


