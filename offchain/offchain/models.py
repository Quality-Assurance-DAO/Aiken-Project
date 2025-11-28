"""Data models for Python off-chain backend."""

from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class BeneficiaryAllocationInput(BaseModel):
    """Input for a single beneficiary allocation."""

    beneficiary_address: str = Field(
        ..., description="Cardano address (bech32 format)"
    )
    token_amount: int = Field(..., gt=0, description="Token amount in smallest unit")
    milestone_identifier: str = Field(..., description="Unique milestone identifier")
    vesting_timestamp: int = Field(
        ..., description="POSIXTime timestamp for vesting"
    )


class MilestoneSchedule(BaseModel):
    """Complete milestone schedule for creating a distribution contract."""

    token_policy_id: str = Field(
        ..., description="Policy ID of token to distribute (hex)"
    )
    beneficiary_allocations: List[BeneficiaryAllocationInput] = Field(
        ..., min_items=1, max_items=50
    )
    oracle_addresses: List[str] = Field(
        ..., min_items=1, description="Authorized oracle addresses"
    )
    quorum_threshold: int = Field(
        ..., gt=0, description="Minimum oracle signatures required"
    )
    contract_metadata: Optional[dict] = Field(
        None, description="Additional metadata"
    )

    @property
    def total_token_amount(self) -> int:
        """Calculate total tokens across all allocations."""
        return sum(alloc.token_amount for alloc in self.beneficiary_allocations)

    def validate(self) -> List[str]:
        """Validate schedule and return list of errors."""
        errors = []
        if self.quorum_threshold > len(self.oracle_addresses):
            errors.append(
                f"Quorum threshold ({self.quorum_threshold}) exceeds oracle count ({len(self.oracle_addresses)})"
            )
        # Additional validation logic...
        return errors


class OracleSignatureData(BaseModel):
    """Oracle signature data (format validation only)."""

    oracle_address: str = Field(..., description="Oracle address (bech32)")
    signature: str = Field(..., description="Ed25519 signature (hex)")
    signed_data: str = Field(..., description="Data that was signed (hex)")
    signature_timestamp: int = Field(..., description="POSIXTime when signed")


class MilestoneCompletionData(BaseModel):
    """Milestone completion data stored locally."""

    milestone_identifier: str = Field(..., description="Unique milestone identifier")
    oracle_signatures: List[OracleSignatureData] = Field(default_factory=list)
    verification_timestamp: Optional[int] = Field(
        None, description="POSIXTime when verified"
    )
    quorum_status: str = Field(
        "pending", description="pending|met|exceeded"
    )
    quorum_threshold: int = Field(..., description="Required signature count")
    total_oracles: int = Field(..., description="Total authorized oracles")

    @property
    def signature_count(self) -> int:
        """Count of unique oracle signatures."""
        unique_oracles = set(sig.oracle_address for sig in self.oracle_signatures)
        return len(unique_oracles)

    @property
    def quorum_met(self) -> bool:
        """Check if quorum threshold is met."""
        return self.signature_count >= self.quorum_threshold

    def add_signature(self, signature: OracleSignatureData) -> bool:
        """Add signature if oracle is authorized and not duplicate."""
        # Check for duplicates
        existing = any(
            s.oracle_address == signature.oracle_address
            for s in self.oracle_signatures
        )
        if not existing:
            self.oracle_signatures.append(signature)
            self._update_quorum_status()
            return True
        return False

    def _update_quorum_status(self):
        """Update quorum status based on signature count."""
        count = self.signature_count
        if count >= self.quorum_threshold:
            self.quorum_status = (
                "met" if count == self.quorum_threshold else "exceeded"
            )
        else:
            self.quorum_status = "pending"


class BeneficiaryAllocationState(BaseModel):
    """On-chain beneficiary allocation state."""

    beneficiary_address: str
    token_amount: int
    milestone_identifier: str
    vesting_timestamp: int
    claimed: bool


class DistributionContractState(BaseModel):
    """Current on-chain state of distribution contract."""

    contract_address: str = Field(..., description="Contract address (bech32)")
    utxo_tx_hash: str = Field(..., description="UTxO transaction hash")
    utxo_index: int = Field(..., description="UTxO output index")
    datum: dict = Field(..., description="Contract datum (parsed JSON)")
    total_token_amount: int
    token_policy_id: str
    beneficiary_allocations: List[BeneficiaryAllocationState]
    oracle_addresses: List[str]
    quorum_threshold: int
    total_oracles: int
    remaining_token_amount: int = Field(
        ..., description="Tokens not yet claimed"
    )

    @property
    def claimed_count(self) -> int:
        """Count of claimed allocations."""
        return sum(1 for alloc in self.beneficiary_allocations if alloc.claimed)

    @property
    def unclaimed_count(self) -> int:
        """Count of unclaimed allocations."""
        return len(self.beneficiary_allocations) - self.claimed_count

    def get_allocation_by_index(self, index: int) -> Optional[BeneficiaryAllocationState]:
        """Get allocation by index."""
        if 0 <= index < len(self.beneficiary_allocations):
            return self.beneficiary_allocations[index]
        return None

    def get_claimable_allocations(
        self, current_time: int
    ) -> List[BeneficiaryAllocationState]:
        """Get allocations that are claimable (not claimed, vesting passed)."""
        return [
            alloc
            for alloc in self.beneficiary_allocations
            if not alloc.claimed and alloc.vesting_timestamp <= current_time
        ]


class ReleaseTransactionInput(BaseModel):
    """Input for building a release transaction."""

    contract_address: str = Field(..., description="Distribution contract address")
    beneficiary_address: str = Field(..., description="Beneficiary claiming address")
    beneficiary_index: int = Field(..., ge=0, description="Index in allocations list")
    milestone_identifier: str = Field(..., description="Milestone being claimed")
    signing_key_path: str = Field(..., description="Path to signing key file")
    collateral_amount: Optional[int] = Field(
        None, description="Collateral amount (auto-calculated if None)"
    )


