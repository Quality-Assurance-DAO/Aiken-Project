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

    def commit_milestone_completion_data(
        self,
        milestone_identifier: str,
        oracle_signatures: List[OracleSignatureData],
        quorum_threshold: Optional[int] = None,
        total_oracles: Optional[int] = None,
    ) -> MilestoneCompletionData:
        """Commit milestone completion data with incremental signature addition."""
        # Load existing milestone data if it exists
        existing_data = self.load_milestone_completion_data(milestone_identifier)
        
        if existing_data:
            milestone_data = existing_data
        else:
            # Create new milestone data
            if quorum_threshold is None or total_oracles is None:
                raise ValueError(
                    "quorum_threshold and total_oracles are required when creating new milestone data"
                )
            milestone_data = MilestoneCompletionData(
                milestone_identifier=milestone_identifier,
                quorum_threshold=quorum_threshold,
                total_oracles=total_oracles,
            )
        
        # Validate and add each signature
        added_count = 0
        skipped_count = 0
        validation_errors = []
        
        for sig in oracle_signatures:
            # Validate signature format
            sig_dict = sig.model_dump()
            format_errors = self.validate_oracle_signature_format(sig_dict)
            
            if format_errors:
                validation_errors.extend(
                    [f"Signature from {sig.oracle_address}: {err}" for err in format_errors]
                )
                continue
            
            # Check for duplicates
            if self.detect_duplicate_oracle_signature(milestone_data, sig.oracle_address):
                skipped_count += 1
                continue
            
            # Add signature
            milestone_data.oracle_signatures.append(sig)
            added_count += 1
        
        # Update quorum status
        signature_count = milestone_data.signature_count
        milestone_data.quorum_status = self.calculate_quorum_status(
            signature_count, milestone_data.quorum_threshold
        )
        
        # Update verification timestamp if quorum is met
        if milestone_data.quorum_met and milestone_data.verification_timestamp is None:
            import time
            milestone_data.verification_timestamp = int(time.time())
        
        # Save updated milestone data
        self.save_milestone_completion_data(milestone_data)
        
        # Raise error if there were validation errors
        if validation_errors:
            raise ValueError(
                f"Invalid signature formats: {'; '.join(validation_errors)}"
            )
        
        return milestone_data

    def save_contract_state_cache(
        self, contract_address: str, contract_state: DistributionContractState
    ) -> Path:
        """Save contract state to cache directory."""
        # Use contract address as filename (sanitized)
        safe_address = contract_address.replace("/", "_").replace(":", "_")
        cache_file = self.cache_directory / f"{safe_address}.json"
        
        cache_data = {
            "contract_address": contract_state.contract_address,
            "utxo_tx_hash": contract_state.utxo_tx_hash,
            "utxo_index": contract_state.utxo_index,
            "datum": contract_state.datum,
            "total_token_amount": contract_state.total_token_amount,
            "token_policy_id": contract_state.token_policy_id,
            "beneficiary_allocations": [
                {
                    "beneficiary_address": alloc.beneficiary_address,
                    "token_amount": alloc.token_amount,
                    "milestone_identifier": alloc.milestone_identifier,
                    "vesting_timestamp": alloc.vesting_timestamp,
                    "claimed": alloc.claimed,
                }
                for alloc in contract_state.beneficiary_allocations
            ],
            "oracle_addresses": contract_state.oracle_addresses,
            "quorum_threshold": contract_state.quorum_threshold,
            "total_oracles": contract_state.total_oracles,
            "remaining_token_amount": contract_state.remaining_token_amount,
            "cached_at": int(__import__("time").time()),
        }
        
        with open(cache_file, "w") as f:
            json.dump(cache_data, f, indent=2)
        
        return cache_file

    def load_contract_state_cache(
        self, contract_address: str
    ) -> Optional[DistributionContractState]:
        """Load contract state from cache directory."""
        safe_address = contract_address.replace("/", "_").replace(":", "_")
        cache_file = self.cache_directory / f"{safe_address}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, "r") as f:
                cache_data = json.load(f)
            
            # Reconstruct DistributionContractState
            from offchain.models import BeneficiaryAllocationState
            
            beneficiary_allocations = [
                BeneficiaryAllocationState(**alloc)
                for alloc in cache_data["beneficiary_allocations"]
            ]
            
            return DistributionContractState(
                contract_address=cache_data["contract_address"],
                utxo_tx_hash=cache_data["utxo_tx_hash"],
                utxo_index=cache_data["utxo_index"],
                datum=cache_data["datum"],
                total_token_amount=cache_data["total_token_amount"],
                token_policy_id=cache_data["token_policy_id"],
                beneficiary_allocations=beneficiary_allocations,
                oracle_addresses=cache_data["oracle_addresses"],
                quorum_threshold=cache_data["quorum_threshold"],
                total_oracles=cache_data["total_oracles"],
                remaining_token_amount=cache_data["remaining_token_amount"],
            )
        except (json.JSONDecodeError, KeyError, Exception):
            # Cache corrupted - return None to trigger refresh
            return None

    def is_cache_stale(
        self, contract_address: str, max_age_seconds: int = 300
    ) -> bool:
        """Check if cached contract state is stale."""
        safe_address = contract_address.replace("/", "_").replace(":", "_")
        cache_file = self.cache_directory / f"{safe_address}.json"
        
        if not cache_file.exists():
            return True
        
        # If max_age_seconds is 0, always consider cache stale (disables caching)
        if max_age_seconds == 0:
            return True
        
        try:
            with open(cache_file, "r") as f:
                cache_data = json.load(f)
            
            cached_at = cache_data.get("cached_at", 0)
            import time
            age = int(time.time()) - cached_at
            
            return age > max_age_seconds
        except Exception:
            return True

    def parse_contract_state_from_utxo(
        self, utxo: Dict[str, Any], contract_address: str
    ) -> Optional[DistributionContractState]:
        """Parse DistributionContractState from Kupo UTxO response."""
        try:
            # Extract datum
            datum = utxo.get("datum")
            if not datum:
                return None
            
            # Handle different datum formats
            if isinstance(datum, dict):
                parsed_datum = datum
            elif isinstance(datum, str):
                # If it's a hex string, we might need to decode it
                # For now, assume it's already parsed or wrap it
                parsed_datum = {"cbor": datum}
            else:
                return None
            
            # Extract UTxO information
            utxo_tx_hash = utxo.get("transaction_id") or utxo.get("tx_hash", "")
            utxo_index = utxo.get("output_index", 0)
            
            # Parse datum structure (assuming it matches our datum format)
            token_policy_id = parsed_datum.get("token_policy_id", "")
            beneficiary_allocations_data = parsed_datum.get("beneficiary_allocations", [])
            oracle_addresses = parsed_datum.get("oracle_addresses", [])
            quorum_threshold = parsed_datum.get("quorum_threshold", 0)
            total_oracles = parsed_datum.get("total_oracles", len(oracle_addresses))
            
            # Convert beneficiary allocations
            from offchain.models import BeneficiaryAllocationState
            
            beneficiary_allocations = []
            total_token_amount = 0
            
            for alloc_data in beneficiary_allocations_data:
                alloc = BeneficiaryAllocationState(
                    beneficiary_address=alloc_data.get("beneficiary_address", ""),
                    token_amount=alloc_data.get("token_amount", 0),
                    milestone_identifier=alloc_data.get("milestone_identifier", ""),
                    vesting_timestamp=alloc_data.get("vesting_timestamp", 0),
                    claimed=alloc_data.get("claimed", False),
                )
                beneficiary_allocations.append(alloc)
                total_token_amount += alloc.token_amount
            
            # Calculate remaining token amount (unclaimed tokens)
            remaining_token_amount = sum(
                alloc.token_amount
                for alloc in beneficiary_allocations
                if not alloc.claimed
            )
            
            return DistributionContractState(
                contract_address=contract_address,
                utxo_tx_hash=utxo_tx_hash,
                utxo_index=utxo_index,
                datum=parsed_datum,
                total_token_amount=total_token_amount,
                token_policy_id=token_policy_id,
                beneficiary_allocations=beneficiary_allocations,
                oracle_addresses=oracle_addresses,
                quorum_threshold=quorum_threshold,
                total_oracles=total_oracles,
                remaining_token_amount=remaining_token_amount,
            )
        except Exception as e:
            # Failed to parse - return None
            return None

    def aggregate_milestone_status(
        self,
        contract_state: DistributionContractState,
        milestone_identifier: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Aggregate milestone status combining contract state and local milestone data."""
        import time
        
        result = {
            "contract_address": contract_state.contract_address,
            "milestones": {},
        }
        
        # Get all unique milestone identifiers from contract
        milestone_ids = set(
            alloc.milestone_identifier
            for alloc in contract_state.beneficiary_allocations
        )
        
        # If specific milestone requested, filter to that one
        if milestone_identifier:
            if milestone_identifier not in milestone_ids:
                result["error"] = f"Milestone {milestone_identifier} not found in contract"
                return result
            milestone_ids = {milestone_identifier}
        
        current_time = int(time.time())
        
        # Aggregate status for each milestone
        for mid in milestone_ids:
            # Load local milestone completion data
            local_data = self.load_milestone_completion_data(mid)
            
            # Get allocations for this milestone
            milestone_allocations = [
                alloc
                for alloc in contract_state.beneficiary_allocations
                if alloc.milestone_identifier == mid
            ]
            
            # Calculate totals
            total_amount = sum(alloc.token_amount for alloc in milestone_allocations)
            claimed_amount = sum(
                alloc.token_amount
                for alloc in milestone_allocations
                if alloc.claimed
            )
            unclaimed_amount = total_amount - claimed_amount
            
            # Check vesting status
            vesting_passed = all(
                alloc.vesting_timestamp <= current_time
                for alloc in milestone_allocations
            )
            earliest_vesting = min(
                alloc.vesting_timestamp for alloc in milestone_allocations
            )
            
            milestone_status = {
                "milestone_identifier": mid,
                "total_token_amount": total_amount,
                "claimed_amount": claimed_amount,
                "unclaimed_amount": unclaimed_amount,
                "allocations_count": len(milestone_allocations),
                "claimed_count": sum(1 for alloc in milestone_allocations if alloc.claimed),
                "vesting_passed": vesting_passed,
                "earliest_vesting_timestamp": earliest_vesting,
            }
            
            # Add local milestone completion data if available
            if local_data:
                milestone_status["quorum_status"] = local_data.quorum_status
                milestone_status["quorum_met"] = local_data.quorum_met
                milestone_status["signature_count"] = local_data.signature_count
                milestone_status["quorum_threshold"] = local_data.quorum_threshold
                milestone_status["verification_timestamp"] = local_data.verification_timestamp
                milestone_status["claimable"] = (
                    local_data.quorum_met and vesting_passed and unclaimed_amount > 0
                )
            else:
                milestone_status["quorum_status"] = "unknown"
                milestone_status["quorum_met"] = False
                milestone_status["signature_count"] = 0
                milestone_status["quorum_threshold"] = contract_state.quorum_threshold
                milestone_status["verification_timestamp"] = None
                milestone_status["claimable"] = False
            
            result["milestones"][mid] = milestone_status
        
        return result

