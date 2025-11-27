"""Milestone management and business logic."""

import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from offchain.models import (
    MilestoneSchedule,
    BeneficiaryAllocationInput,
    MilestoneCompletionData,
    OracleSignatureData,
    DistributionContractState,
)
from offchain.validator_loader import ValidatorLoader
from pycardano import Address, PlutusV3Script, ScriptHash
import hashlib


class MilestoneManager:
    """Manages milestone schedules and completion data."""

    def __init__(self, data_directory: Path):
        """Initialize milestone manager."""
        self.data_directory = Path(data_directory)
        self.milestones_directory = self.data_directory / "milestones"
        self.cache_directory = self.data_directory / "cache"
        self.milestones_directory.mkdir(parents=True, exist_ok=True)
        self.cache_directory.mkdir(parents=True, exist_ok=True)

    def validate_milestone_schedule(self, schedule: MilestoneSchedule) -> List[str]:
        """Validate milestone schedule and return list of errors."""
        errors = []
        
        # Validate quorum threshold
        if schedule.quorum_threshold > len(schedule.oracle_addresses):
            errors.append(
                f"Quorum threshold ({schedule.quorum_threshold}) exceeds oracle count ({len(schedule.oracle_addresses)})"
            )
        
        if schedule.quorum_threshold <= 0:
            errors.append("Quorum threshold must be greater than 0")
        
        # Validate beneficiary addresses (basic bech32 format check)
        for i, allocation in enumerate(schedule.beneficiary_allocations):
            if not allocation.beneficiary_address.startswith(("addr", "addr_test", "addr1")):
                errors.append(
                    f"Invalid beneficiary address format at index {i}: {allocation.beneficiary_address}"
                )
            
            if allocation.token_amount <= 0:
                errors.append(
                    f"Token amount must be positive at index {i}: {allocation.token_amount}"
                )
            
            if not allocation.milestone_identifier:
                errors.append(
                    f"Milestone identifier cannot be empty at index {i}"
                )
        
        # Validate oracle addresses
        for i, oracle_addr in enumerate(schedule.oracle_addresses):
            if not oracle_addr.startswith(("addr", "addr_test", "addr1")):
                errors.append(
                    f"Invalid oracle address format at index {i}: {oracle_addr}"
                )
        
        return errors

    def generate_datum(self, schedule: MilestoneSchedule) -> Dict[str, Any]:
        """Convert MilestoneSchedule to on-chain datum format."""
        # Convert to datum structure expected by validator
        datum = {
            "token_policy_id": schedule.token_policy_id,
            "beneficiary_allocations": [
                {
                    "beneficiary_address": alloc.beneficiary_address,
                    "token_amount": alloc.token_amount,
                    "milestone_identifier": alloc.milestone_identifier,
                    "vesting_timestamp": alloc.vesting_timestamp,
                    "claimed": False,
                }
                for alloc in schedule.beneficiary_allocations
            ],
            "oracle_addresses": schedule.oracle_addresses,
            "quorum_threshold": schedule.quorum_threshold,
            "total_oracles": len(schedule.oracle_addresses),
        }
        
        if schedule.contract_metadata:
            datum["metadata"] = schedule.contract_metadata
        
        return datum

    def calculate_contract_address(self, validator_hash: str, network: str = "testnet") -> str:
        """Calculate contract address from validator hash."""
        # This is a simplified version - actual implementation would use pycardano
        # to properly construct the address from the script hash
        try:
            # Convert hex hash to bytes
            script_hash_bytes = bytes.fromhex(validator_hash)
            
            # For now, return a placeholder - actual implementation needs pycardano
            # to construct proper bech32 address
            # This would require network-specific address construction
            return f"addr_test1{validator_hash[:56]}"  # Placeholder
        except Exception as e:
            raise ValueError(f"Failed to calculate contract address: {e}")

    def save_milestone_completion_data(
        self, milestone_data: MilestoneCompletionData
    ) -> Path:
        """Save milestone completion data to JSON file."""
        file_path = self.milestones_directory / f"{milestone_data.milestone_identifier}.json"
        
        with open(file_path, "w") as f:
            json.dump(milestone_data.model_dump(), f, indent=2)
        
        return file_path

    def load_milestone_completion_data(
        self, milestone_identifier: str
    ) -> Optional[MilestoneCompletionData]:
        """Load milestone completion data from JSON file."""
        file_path = self.milestones_directory / f"{milestone_identifier}.json"
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                return MilestoneCompletionData(**data)
        except (json.JSONDecodeError, Exception):
            # File corrupted - return None to trigger recovery
            return None

    def validate_oracle_signature_format(self, signature: Dict[str, Any]) -> List[str]:
        """Validate oracle signature format (structure only, not cryptographic)."""
        errors = []
        
        required_fields = ["oracle_address", "signature", "signed_data", "signature_timestamp"]
        for field in required_fields:
            if field not in signature:
                errors.append(f"Missing required field: {field}")
        
        if "oracle_address" in signature:
            addr = signature["oracle_address"]
            if not isinstance(addr, str) or not addr.startswith(("addr", "addr_test", "addr1")):
                errors.append(f"Invalid oracle_address format: {addr}")
        
        if "signature" in signature:
            sig = signature["signature"]
            if not isinstance(sig, str) or len(sig) == 0:
                errors.append("Signature must be a non-empty string")
        
        if "signature_timestamp" in signature:
            ts = signature["signature_timestamp"]
            if not isinstance(ts, int) or ts <= 0:
                errors.append("signature_timestamp must be a positive integer")
        
        return errors

    def calculate_quorum_status(
        self, signature_count: int, quorum_threshold: int
    ) -> str:
        """Calculate quorum status based on signature count."""
        if signature_count >= quorum_threshold:
            return "met" if signature_count == quorum_threshold else "exceeded"
        return "pending"

    def detect_duplicate_oracle_signature(
        self, milestone_data: MilestoneCompletionData, oracle_address: str
    ) -> bool:
        """Check if oracle has already signed."""
        return any(
            sig.oracle_address == oracle_address
            for sig in milestone_data.oracle_signatures
        )

