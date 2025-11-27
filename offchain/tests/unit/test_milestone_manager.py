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


def test_milestone_data_storage_file_io():
    """Test milestone data storage with file I/O operations."""
    with TemporaryDirectory() as tmpdir:
        manager = MilestoneManager(Path(tmpdir))
        
        # Create milestone data with signatures
        milestone_data = MilestoneCompletionData(
            milestone_identifier="milestone-002",
            quorum_threshold=3,
            total_oracles=5,
        )
        
        # Add some signatures
        milestone_data.oracle_signatures.append(
            OracleSignatureData(
                oracle_address="addr_test1q...oracle1",
                signature="sig1",
                signed_data="data1",
                signature_timestamp=1735689600,
            )
        )
        milestone_data.oracle_signatures.append(
            OracleSignatureData(
                oracle_address="addr_test1q...oracle2",
                signature="sig2",
                signed_data="data2",
                signature_timestamp=1735689700,
            )
        )
        
        # Save milestone data
        file_path = manager.save_milestone_completion_data(milestone_data)
        assert file_path.exists()
        assert file_path.name == "milestone-002.json"
        
        # Verify file contents
        with open(file_path, "r") as f:
            loaded_json = json.load(f)
            assert loaded_json["milestone_identifier"] == "milestone-002"
            assert len(loaded_json["oracle_signatures"]) == 2
        
        # Load milestone data
        loaded_data = manager.load_milestone_completion_data("milestone-002")
        assert loaded_data is not None
        assert loaded_data.milestone_identifier == "milestone-002"
        assert len(loaded_data.oracle_signatures) == 2
        assert loaded_data.oracle_signatures[0].oracle_address == "addr_test1q...oracle1"
        
        # Test loading non-existent milestone
        non_existent = manager.load_milestone_completion_data("milestone-999")
        assert non_existent is None


def test_quorum_calculation_various_counts():
    """Test quorum calculation with various signature counts."""
    with TemporaryDirectory() as tmpdir:
        manager = MilestoneManager(Path(tmpdir))
        quorum_threshold = 3
        
        # Test pending (0 signatures)
        assert manager.calculate_quorum_status(0, quorum_threshold) == "pending"
        
        # Test pending (1 signature)
        assert manager.calculate_quorum_status(1, quorum_threshold) == "pending"
        
        # Test pending (2 signatures)
        assert manager.calculate_quorum_status(2, quorum_threshold) == "pending"
        
        # Test met (exactly threshold)
        assert manager.calculate_quorum_status(3, quorum_threshold) == "met"
        
        # Test exceeded (more than threshold)
        assert manager.calculate_quorum_status(4, quorum_threshold) == "exceeded"
        assert manager.calculate_quorum_status(5, quorum_threshold) == "exceeded"
        
        # Test with milestone data
        milestone_data = MilestoneCompletionData(
            milestone_identifier="milestone-003",
            quorum_threshold=quorum_threshold,
            total_oracles=5,
        )
        
        # Add signatures incrementally
        for i in range(1, 4):
            milestone_data.oracle_signatures.append(
                OracleSignatureData(
                    oracle_address=f"addr_test1q...oracle{i}",
                    signature=f"sig{i}",
                    signed_data=f"data{i}",
                    signature_timestamp=1735689600 + i,
                )
            )
            status = manager.calculate_quorum_status(
                milestone_data.signature_count, quorum_threshold
            )
            if i < 3:
                assert status == "pending"
            elif i == 3:
                assert status == "met"


def test_commit_milestone_completion_data_new():
    """Test committing milestone completion data for new milestone."""
    with TemporaryDirectory() as tmpdir:
        manager = MilestoneManager(Path(tmpdir))
        
        signatures = [
            OracleSignatureData(
                oracle_address="addr_test1q...oracle1",
                signature="sig1",
                signed_data="data1",
                signature_timestamp=1735689600,
            ),
            OracleSignatureData(
                oracle_address="addr_test1q...oracle2",
                signature="sig2",
                signed_data="data2",
                signature_timestamp=1735689700,
            ),
        ]
        
        milestone_data = manager.commit_milestone_completion_data(
            milestone_identifier="milestone-004",
            oracle_signatures=signatures,
            quorum_threshold=3,
            total_oracles=5,
        )
        
        assert milestone_data.milestone_identifier == "milestone-004"
        assert milestone_data.signature_count == 2
        assert milestone_data.quorum_status == "pending"
        assert milestone_data.quorum_met is False
        
        # Verify file was saved
        loaded = manager.load_milestone_completion_data("milestone-004")
        assert loaded is not None
        assert loaded.signature_count == 2


def test_commit_milestone_completion_data_incremental():
    """Test incremental signature addition to existing milestone data."""
    with TemporaryDirectory() as tmpdir:
        manager = MilestoneManager(Path(tmpdir))
        
        # Create initial milestone data
        initial_sigs = [
            OracleSignatureData(
                oracle_address="addr_test1q...oracle1",
                signature="sig1",
                signed_data="data1",
                signature_timestamp=1735689600,
            ),
        ]
        
        milestone_data = manager.commit_milestone_completion_data(
            milestone_identifier="milestone-005",
            oracle_signatures=initial_sigs,
            quorum_threshold=3,
            total_oracles=5,
        )
        
        assert milestone_data.signature_count == 1
        assert milestone_data.quorum_status == "pending"
        
        # Add more signatures incrementally
        additional_sigs = [
            OracleSignatureData(
                oracle_address="addr_test1q...oracle2",
                signature="sig2",
                signed_data="data2",
                signature_timestamp=1735689700,
            ),
            OracleSignatureData(
                oracle_address="addr_test1q...oracle3",
                signature="sig3",
                signed_data="data3",
                signature_timestamp=1735689800,
            ),
        ]
        
        updated_data = manager.commit_milestone_completion_data(
            milestone_identifier="milestone-005",
            oracle_signatures=additional_sigs,
            quorum_threshold=3,
            total_oracles=5,
        )
        
        assert updated_data.signature_count == 3
        assert updated_data.quorum_status == "met"
        assert updated_data.quorum_met is True
        assert updated_data.verification_timestamp is not None


def test_commit_milestone_completion_data_duplicate_prevention():
    """Test that duplicate oracle signatures are prevented."""
    with TemporaryDirectory() as tmpdir:
        manager = MilestoneManager(Path(tmpdir))
        
        signatures = [
            OracleSignatureData(
                oracle_address="addr_test1q...oracle1",
                signature="sig1",
                signed_data="data1",
                signature_timestamp=1735689600,
            ),
        ]
        
        milestone_data = manager.commit_milestone_completion_data(
            milestone_identifier="milestone-006",
            oracle_signatures=signatures,
            quorum_threshold=2,
            total_oracles=3,
        )
        
        assert milestone_data.signature_count == 1
        
        # Try to add the same signature again
        duplicate_sigs = [
            OracleSignatureData(
                oracle_address="addr_test1q...oracle1",
                signature="sig1-different",
                signed_data="data1-different",
                signature_timestamp=1735689900,
            ),
        ]
        
        updated_data = manager.commit_milestone_completion_data(
            milestone_identifier="milestone-006",
            oracle_signatures=duplicate_sigs,
            quorum_threshold=2,
            total_oracles=3,
        )
        
        # Should still have only 1 signature (duplicate ignored)
        assert updated_data.signature_count == 1


def test_commit_milestone_completion_data_invalid_signature_format():
    """Test that invalid signature formats are rejected."""
    with TemporaryDirectory() as tmpdir:
        manager = MilestoneManager(Path(tmpdir))
        
        # Create invalid signature (missing required field)
        invalid_sig = OracleSignatureData(
            oracle_address="addr_test1q...oracle1",
            signature="sig1",
            signed_data="data1",
            signature_timestamp=1735689600,
        )
        
        # Manually create invalid dict to test validation
        invalid_dict = {
            "oracle_address": "addr_test1q...oracle1",
            "signature": "",  # Empty signature should fail
            "signed_data": "data1",
            "signature_timestamp": 1735689600,
        }
        
        errors = manager.validate_oracle_signature_format(invalid_dict)
        assert len(errors) > 0
        assert any("signature" in err.lower() for err in errors)
        
        # Test with invalid address format
        invalid_addr_dict = {
            "oracle_address": "invalid-address",
            "signature": "sig1",
            "signed_data": "data1",
            "signature_timestamp": 1735689600,
        }
        
        errors = manager.validate_oracle_signature_format(invalid_addr_dict)
        assert len(errors) > 0
        assert any("address" in err.lower() for err in errors)


def test_contract_state_cache_save_and_load():
    """Test saving and loading contract state cache."""
    with TemporaryDirectory() as tmpdir:
        manager = MilestoneManager(Path(tmpdir))
        
        from offchain.models import DistributionContractState, BeneficiaryAllocationState
        
        contract_state = DistributionContractState(
            contract_address="addr_test1q...",
            utxo_tx_hash="abc123",
            utxo_index=0,
            datum={"token_policy_id": "abc"},
            total_token_amount=1000000,
            token_policy_id="abc",
            beneficiary_allocations=[
                BeneficiaryAllocationState(
                    beneficiary_address="addr_test1q...ben1",
                    token_amount=500000,
                    milestone_identifier="milestone-001",
                    vesting_timestamp=1735689600,
                    claimed=False,
                )
            ],
            oracle_addresses=["addr_test1q...oracle1"],
            quorum_threshold=1,
            total_oracles=1,
            remaining_token_amount=1000000,
        )
        
        # Save cache
        cache_path = manager.save_contract_state_cache("addr_test1q...", contract_state)
        assert cache_path.exists()
        
        # Load cache
        loaded_state = manager.load_contract_state_cache("addr_test1q...")
        assert loaded_state is not None
        assert loaded_state.contract_address == "addr_test1q..."
        assert loaded_state.utxo_tx_hash == "abc123"
        assert len(loaded_state.beneficiary_allocations) == 1


def test_contract_state_cache_stale_check():
    """Test cache staleness checking."""
    with TemporaryDirectory() as tmpdir:
        manager = MilestoneManager(Path(tmpdir))
        
        from offchain.models import DistributionContractState, BeneficiaryAllocationState
        
        contract_state = DistributionContractState(
            contract_address="addr_test1q...",
            utxo_tx_hash="abc123",
            utxo_index=0,
            datum={},
            total_token_amount=0,
            token_policy_id="abc",
            beneficiary_allocations=[],
            oracle_addresses=[],
            quorum_threshold=1,
            total_oracles=1,
            remaining_token_amount=0,
        )
        
        # Save cache
        manager.save_contract_state_cache("addr_test1q...", contract_state)
        
        # Should not be stale immediately
        assert manager.is_cache_stale("addr_test1q...", max_age_seconds=300) is False
        
        # Should be stale with very short max age
        assert manager.is_cache_stale("addr_test1q...", max_age_seconds=0) is True


def test_parse_contract_state_from_utxo():
    """Test parsing contract state from UTxO response."""
    with TemporaryDirectory() as tmpdir:
        manager = MilestoneManager(Path(tmpdir))
        
        utxo = {
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
        
        contract_state = manager.parse_contract_state_from_utxo(utxo, "addr_test1q...")
        
        assert contract_state is not None
        assert contract_state.contract_address == "addr_test1q..."
        assert contract_state.utxo_tx_hash == "tx123"
        assert contract_state.token_policy_id == "abc123"
        assert len(contract_state.beneficiary_allocations) == 1
        assert contract_state.beneficiary_allocations[0].milestone_identifier == "milestone-001"


def test_milestone_status_aggregation():
    """Test milestone status aggregation combining contract state and local data."""
    with TemporaryDirectory() as tmpdir:
        manager = MilestoneManager(Path(tmpdir))
        
        from offchain.models import DistributionContractState, BeneficiaryAllocationState
        
        # Create contract state
        contract_state = DistributionContractState(
            contract_address="addr_test1q...",
            utxo_tx_hash="tx123",
            utxo_index=0,
            datum={},
            total_token_amount=2000000,
            token_policy_id="abc",
            beneficiary_allocations=[
                BeneficiaryAllocationState(
                    beneficiary_address="addr_test1q...ben1",
                    token_amount=1000000,
                    milestone_identifier="milestone-001",
                    vesting_timestamp=1735689600,  # Past timestamp
                    claimed=False,
                ),
                BeneficiaryAllocationState(
                    beneficiary_address="addr_test1q...ben2",
                    token_amount=1000000,
                    milestone_identifier="milestone-001",
                    vesting_timestamp=1735689600,
                    claimed=True,
                ),
            ],
            oracle_addresses=["addr_test1q...oracle1"],
            quorum_threshold=1,
            total_oracles=1,
            remaining_token_amount=1000000,
        )
        
        # Create local milestone completion data
        milestone_data = MilestoneCompletionData(
            milestone_identifier="milestone-001",
            quorum_threshold=1,
            total_oracles=1,
        )
        milestone_data.oracle_signatures.append(
            OracleSignatureData(
                oracle_address="addr_test1q...oracle1",
                signature="sig1",
                signed_data="data1",
                signature_timestamp=1735689600,
            )
        )
        milestone_data.quorum_status = "met"
        manager.save_milestone_completion_data(milestone_data)
        
        # Aggregate status
        status = manager.aggregate_milestone_status(contract_state, "milestone-001")
        
        assert "milestones" in status
        assert "milestone-001" in status["milestones"]
        
        milestone_status = status["milestones"]["milestone-001"]
        assert milestone_status["total_token_amount"] == 2000000
        assert milestone_status["claimed_amount"] == 1000000
        assert milestone_status["unclaimed_amount"] == 1000000
        assert milestone_status["quorum_met"] is True
        assert milestone_status["signature_count"] == 1
        assert milestone_status["vesting_passed"] is True
        assert milestone_status["claimable"] is True


def test_milestone_status_aggregation_no_local_data():
    """Test milestone status aggregation without local milestone data."""
    with TemporaryDirectory() as tmpdir:
        manager = MilestoneManager(Path(tmpdir))
        
        from offchain.models import DistributionContractState, BeneficiaryAllocationState
        
        contract_state = DistributionContractState(
            contract_address="addr_test1q...",
            utxo_tx_hash="tx123",
            utxo_index=0,
            datum={},
            total_token_amount=1000000,
            token_policy_id="abc",
            beneficiary_allocations=[
                BeneficiaryAllocationState(
                    beneficiary_address="addr_test1q...ben1",
                    token_amount=1000000,
                    milestone_identifier="milestone-002",
                    vesting_timestamp=1735689600,
                    claimed=False,
                )
            ],
            oracle_addresses=["addr_test1q...oracle1"],
            quorum_threshold=1,
            total_oracles=1,
            remaining_token_amount=1000000,
        )
        
        # Aggregate without local data
        status = manager.aggregate_milestone_status(contract_state, "milestone-002")
        
        assert "milestones" in status
        milestone_status = status["milestones"]["milestone-002"]
        assert milestone_status["quorum_status"] == "unknown"
        assert milestone_status["quorum_met"] is False
        assert milestone_status["signature_count"] == 0
        assert milestone_status["claimable"] is False


def test_milestone_status_aggregation_multiple_milestones():
    """Test milestone status aggregation with multiple milestones."""
    with TemporaryDirectory() as tmpdir:
        manager = MilestoneManager(Path(tmpdir))
        
        from offchain.models import DistributionContractState, BeneficiaryAllocationState
        
        contract_state = DistributionContractState(
            contract_address="addr_test1q...",
            utxo_tx_hash="tx123",
            utxo_index=0,
            datum={},
            total_token_amount=2000000,
            token_policy_id="abc",
            beneficiary_allocations=[
                BeneficiaryAllocationState(
                    beneficiary_address="addr_test1q...ben1",
                    token_amount=1000000,
                    milestone_identifier="milestone-001",
                    vesting_timestamp=1735689600,
                    claimed=False,
                ),
                BeneficiaryAllocationState(
                    beneficiary_address="addr_test1q...ben2",
                    token_amount=1000000,
                    milestone_identifier="milestone-002",
                    vesting_timestamp=1735689600,
                    claimed=False,
                ),
            ],
            oracle_addresses=["addr_test1q...oracle1"],
            quorum_threshold=1,
            total_oracles=1,
            remaining_token_amount=2000000,
        )
        
        # Aggregate for all milestones
        status = manager.aggregate_milestone_status(contract_state)
        
        assert "milestones" in status
        assert "milestone-001" in status["milestones"]
        assert "milestone-002" in status["milestones"]
        assert len(status["milestones"]) == 2

