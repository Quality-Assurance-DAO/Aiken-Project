"""Unit tests for MilestoneManager."""

import pytest
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from offchain.milestone_manager import MilestoneManager
from offchain.models import (
    MilestoneSchedule,
    BeneficiaryAllocationInput,
    MilestoneCompletionData,
    OracleSignatureData,
)


def test_milestone_schedule_validation_valid():
    """Test milestone schedule validation with valid input."""
    with TemporaryDirectory() as tmpdir:
        manager = MilestoneManager(Path(tmpdir))
        
        schedule = MilestoneSchedule(
            token_policy_id="abc123",
            beneficiary_allocations=[
                BeneficiaryAllocationInput(
                    beneficiary_address="addr_test1q...",
                    token_amount=1000000,
                    milestone_identifier="milestone-001",
                    vesting_timestamp=1735689600,
                )
            ],
            oracle_addresses=["addr_test1q...", "addr_test1q..."],
            quorum_threshold=2,
        )
        
        errors = manager.validate_milestone_schedule(schedule)
        assert len(errors) == 0


def test_milestone_schedule_validation_invalid_quorum():
    """Test milestone schedule validation with invalid quorum threshold."""
    with TemporaryDirectory() as tmpdir:
        manager = MilestoneManager(Path(tmpdir))
        
        schedule = MilestoneSchedule(
            token_policy_id="abc123",
            beneficiary_allocations=[
                BeneficiaryAllocationInput(
                    beneficiary_address="addr_test1q...",
                    token_amount=1000000,
                    milestone_identifier="milestone-001",
                    vesting_timestamp=1735689600,
                )
            ],
            oracle_addresses=["addr_test1q..."],
            quorum_threshold=5,  # Exceeds oracle count
        )
        
        errors = manager.validate_milestone_schedule(schedule)
        assert len(errors) > 0
        assert any("quorum threshold" in error.lower() for error in errors)


def test_datum_generation():
    """Test datum generation from milestone schedule."""
    with TemporaryDirectory() as tmpdir:
        manager = MilestoneManager(Path(tmpdir))
        
        schedule = MilestoneSchedule(
            token_policy_id="abc123",
            beneficiary_allocations=[
                BeneficiaryAllocationInput(
                    beneficiary_address="addr_test1q...",
                    token_amount=1000000,
                    milestone_identifier="milestone-001",
                    vesting_timestamp=1735689600,
                )
            ],
            oracle_addresses=["addr_test1q...", "addr_test1q..."],
            quorum_threshold=2,
        )
        
        datum = manager.generate_datum(schedule)
        
        assert datum["token_policy_id"] == "abc123"
        assert len(datum["beneficiary_allocations"]) == 1
        assert datum["beneficiary_allocations"][0]["token_amount"] == 1000000
        assert datum["beneficiary_allocations"][0]["claimed"] is False
        assert datum["quorum_threshold"] == 2


def test_milestone_completion_data_save_and_load():
    """Test saving and loading milestone completion data."""
    with TemporaryDirectory() as tmpdir:
        manager = MilestoneManager(Path(tmpdir))
        
        milestone_data = MilestoneCompletionData(
            milestone_identifier="milestone-001",
            quorum_threshold=2,
            total_oracles=3,
        )
        
        # Save
        file_path = manager.save_milestone_completion_data(milestone_data)
        assert file_path.exists()
        
        # Load
        loaded_data = manager.load_milestone_completion_data("milestone-001")
        assert loaded_data is not None
        assert loaded_data.milestone_identifier == "milestone-001"
        assert loaded_data.quorum_threshold == 2


def test_oracle_signature_format_validation():
    """Test oracle signature format validation."""
    with TemporaryDirectory() as tmpdir:
        manager = MilestoneManager(Path(tmpdir))
        
        # Valid signature
        valid_sig = {
            "oracle_address": "addr_test1q...",
            "signature": "abc123",
            "signed_data": "def456",
            "signature_timestamp": 1735689600,
        }
        errors = manager.validate_oracle_signature_format(valid_sig)
        assert len(errors) == 0
        
        # Invalid signature (missing field)
        invalid_sig = {
            "oracle_address": "addr_test1q...",
            "signature": "abc123",
            # Missing signed_data and signature_timestamp
        }
        errors = manager.validate_oracle_signature_format(invalid_sig)
        assert len(errors) > 0


def test_quorum_status_calculation():
    """Test quorum status calculation."""
    with TemporaryDirectory() as tmpdir:
        manager = MilestoneManager(Path(tmpdir))
        
        assert manager.calculate_quorum_status(1, 2) == "pending"
        assert manager.calculate_quorum_status(2, 2) == "met"
        assert manager.calculate_quorum_status(3, 2) == "exceeded"


def test_duplicate_oracle_signature_detection():
    """Test duplicate oracle signature detection."""
    with TemporaryDirectory() as tmpdir:
        manager = MilestoneManager(Path(tmpdir))
        
        milestone_data = MilestoneCompletionData(
            milestone_identifier="milestone-001",
            quorum_threshold=2,
            total_oracles=3,
        )
        
        milestone_data.oracle_signatures.append(
            OracleSignatureData(
                oracle_address="addr_test1q...",
                signature="sig1",
                signed_data="data1",
                signature_timestamp=1735689600,
            )
        )
        
        # Check duplicate
        is_duplicate = manager.detect_duplicate_oracle_signature(
            milestone_data, "addr_test1q..."
        )
        assert is_duplicate is True
        
        # Check new oracle
        is_duplicate = manager.detect_duplicate_oracle_signature(
            milestone_data, "addr_test1q...new"
        )
        assert is_duplicate is False

