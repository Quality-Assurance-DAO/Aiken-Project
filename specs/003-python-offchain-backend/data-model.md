# Data Model: Python Off-Chain Backend

**Date**: 2025-01-27  
**Feature**: 003-python-offchain-backend

## Overview

This document defines the data structures used in the Python off-chain backend for milestone-based token distribution. These structures represent:
- Input data for CLI commands
- Local storage formats
- On-chain state representations
- Transaction building components
- Configuration data

## Core Entities

### 1. Milestone Schedule

Input data structure for registering a new milestone schedule. Used to create distribution contract datums.

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class BeneficiaryAllocationInput(BaseModel):
    """Input for a single beneficiary allocation"""
    beneficiary_address: str = Field(..., description="Cardano address (bech32 format)")
    token_amount: int = Field(..., gt=0, description="Token amount in smallest unit")
    milestone_identifier: str = Field(..., description="Unique milestone identifier")
    vesting_timestamp: int = Field(..., description="POSIXTime timestamp for vesting")

class MilestoneSchedule(BaseModel):
    """Complete milestone schedule for creating a distribution contract"""
    token_policy_id: str = Field(..., description="Policy ID of token to distribute (hex)")
    beneficiary_allocations: List[BeneficiaryAllocationInput] = Field(..., min_items=1, max_items=50)
    oracle_addresses: List[str] = Field(..., min_items=1, description="Authorized oracle addresses")
    quorum_threshold: int = Field(..., gt=0, description="Minimum oracle signatures required")
    contract_metadata: Optional[dict] = Field(None, description="Additional metadata")
    
    @property
    def total_token_amount(self) -> int:
        """Calculate total tokens across all allocations"""
        return sum(alloc.token_amount for alloc in self.beneficiary_allocations)
    
    def validate(self) -> List[str]:
        """Validate schedule and return list of errors"""
        errors = []
        if self.quorum_threshold > len(self.oracle_addresses):
            errors.append(f"Quorum threshold ({self.quorum_threshold}) exceeds oracle count ({len(self.oracle_addresses)})")
        # Additional validation logic...
        return errors
```

**Fields**:
- `token_policy_id`: Policy ID of the token being distributed (hex string)
- `beneficiary_allocations`: List of beneficiary allocations (1-50 items)
- `oracle_addresses`: List of authorized oracle addresses (bech32 format)
- `quorum_threshold`: Minimum oracle signatures required for milestone verification
- `contract_metadata`: Optional metadata dictionary

**Validation Rules**:
- `quorum_threshold` must be <= length of `oracle_addresses`
- `quorum_threshold` must be > 0
- All `beneficiary_address` values must be valid Cardano addresses (bech32)
- All `token_amount` values must be > 0
- `vesting_timestamp` must be in the future (at creation time)
- `milestone_identifier` must be non-empty strings

**State Transitions**:
- **Creation**: Created from CLI input or JSON file
- **Validation**: Validated before datum creation
- **Datum Generation**: Converted to on-chain `DistributionContract` datum format

---

### 2. Milestone Completion Data

Local storage format for milestone verification data. Stored as JSON files in `offchain/data/milestones/`.

```python
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class OracleSignatureData(BaseModel):
    """Oracle signature data (format validation only)"""
    oracle_address: str = Field(..., description="Oracle address (bech32)")
    signature: str = Field(..., description="Ed25519 signature (hex)")
    signed_data: str = Field(..., description="Data that was signed (hex)")
    signature_timestamp: int = Field(..., description="POSIXTime when signed")

class MilestoneCompletionData(BaseModel):
    """Milestone completion data stored locally"""
    milestone_identifier: str = Field(..., description="Unique milestone identifier")
    oracle_signatures: List[OracleSignatureData] = Field(default_factory=list)
    verification_timestamp: Optional[int] = Field(None, description="POSIXTime when verified")
    quorum_status: str = Field("pending", description="pending|met|exceeded")
    quorum_threshold: int = Field(..., description="Required signature count")
    total_oracles: int = Field(..., description="Total authorized oracles")
    
    @property
    def signature_count(self) -> int:
        """Count of unique oracle signatures"""
        unique_oracles = set(sig.oracle_address for sig in self.oracle_signatures)
        return len(unique_oracles)
    
    @property
    def quorum_met(self) -> bool:
        """Check if quorum threshold is met"""
        return self.signature_count >= self.quorum_threshold
    
    def add_signature(self, signature: OracleSignatureData) -> bool:
        """Add signature if oracle is authorized and not duplicate"""
        # Check if oracle is authorized (would need oracle_addresses list)
        # Check for duplicates
        existing = any(s.oracle_address == signature.oracle_address 
                     for s in self.oracle_signatures)
        if not existing:
            self.oracle_signatures.append(signature)
            self._update_quorum_status()
            return True
        return False
    
    def _update_quorum_status(self):
        """Update quorum status based on signature count"""
        count = self.signature_count
        if count >= self.quorum_threshold:
            self.quorum_status = "met" if count == self.quorum_threshold else "exceeded"
        else:
            self.quorum_status = "pending"
```

**Storage Format** (JSON file: `offchain/data/milestones/{milestone_id}.json`):
```json
{
  "milestone_identifier": "milestone-001",
  "oracle_signatures": [
    {
      "oracle_address": "addr1...",
      "signature": "abc123...",
      "signed_data": "def456...",
      "signature_timestamp": 1234567890
    }
  ],
  "verification_timestamp": 1234567890,
  "quorum_status": "met",
  "quorum_threshold": 3,
  "total_oracles": 5
}
```

**Fields**:
- `milestone_identifier`: Unique identifier matching allocation milestone
- `oracle_signatures`: List of oracle signatures (format validated)
- `verification_timestamp`: When milestone was verified (POSIXTime)
- `quorum_status`: Current quorum status (pending/met/exceeded)
- `quorum_threshold`: Required signature count
- `total_oracles`: Total authorized oracles

**Validation Rules**:
- Oracle signature format validation (structure, field presence, data types)
- No cryptographic verification (happens on-chain)
- Duplicate oracle signatures are ignored
- File corruption triggers auto-recovery from chain

**State Transitions**:
- **Initial**: Created when milestone completion is committed
- **Update**: Signatures added incrementally
- **Quorum Met**: Status changes to "met" when threshold reached
- **Recovery**: Rebuilt from chain if file corrupted

---

### 3. Distribution Contract State

On-chain state representation queried from Kupo indexer.

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class BeneficiaryAllocationState(BaseModel):
    """On-chain beneficiary allocation state"""
    beneficiary_address: str
    token_amount: int
    milestone_identifier: str
    vesting_timestamp: int
    claimed: bool

class DistributionContractState(BaseModel):
    """Current on-chain state of distribution contract"""
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
    remaining_token_amount: int = Field(..., description="Tokens not yet claimed")
    
    @property
    def claimed_count(self) -> int:
        """Count of claimed allocations"""
        return sum(1 for alloc in self.beneficiary_allocations if alloc.claimed)
    
    @property
    def unclaimed_count(self) -> int:
        """Count of unclaimed allocations"""
        return len(self.beneficiary_allocations) - self.claimed_count
    
    def get_allocation_by_index(self, index: int) -> Optional[BeneficiaryAllocationState]:
        """Get allocation by index"""
        if 0 <= index < len(self.beneficiary_allocations):
            return self.beneficiary_allocations[index]
        return None
    
    def get_claimable_allocations(self, current_time: int) -> List[BeneficiaryAllocationState]:
        """Get allocations that are claimable (not claimed, vesting passed)"""
        return [
            alloc for alloc in self.beneficiary_allocations
            if not alloc.claimed and alloc.vesting_timestamp <= current_time
        ]
```

**Fields**:
- `contract_address`: Contract address where UTxO is located
- `utxo_tx_hash`: Transaction hash of the UTxO
- `utxo_index`: Output index of the UTxO
- `datum`: Parsed contract datum (JSON representation)
- `beneficiary_allocations`: Current state of all allocations
- `remaining_token_amount`: Tokens not yet claimed

**Query Source**: Kupo indexer (`/matches/{contract_address}` endpoint)

**State Transitions**:
- **Query**: Fetched from Kupo when checking milestone status
- **Update**: Refreshed from chain when local cache is stale
- **Cache**: Stored locally for efficient repeated queries

---

### 4. Release Transaction

Transaction building components for submitting token release transactions.

```python
from pydantic import BaseModel, Field
from typing import Optional

class ReleaseTransactionInput(BaseModel):
    """Input for building a release transaction"""
    contract_address: str = Field(..., description="Distribution contract address")
    beneficiary_address: str = Field(..., description="Beneficiary claiming address")
    beneficiary_index: int = Field(..., ge=0, description="Index in allocations list")
    milestone_identifier: str = Field(..., description="Milestone being claimed")
    milestone_verification: dict = Field(..., description="Milestone verification data")
    signing_key_path: str = Field(..., description="Path to signing key file")
    collateral_amount: Optional[int] = Field(None, description="Collateral amount (auto-calculated if None)")

class ReleaseTransaction(BaseModel):
    """Built transaction ready for submission"""
    transaction_cbor: str = Field(..., description="CBOR-encoded transaction (hex)")
    transaction_hash: str = Field(..., description="Transaction hash")
    fee_estimate: int = Field(..., description="Estimated transaction fee (lovelace)")
    collateral_amount: int = Field(..., description="Collateral amount (lovelace)")
    inputs: List[dict] = Field(..., description="Transaction inputs")
    outputs: List[dict] = Field(..., description="Transaction outputs")
    redeemers: List[dict] = Field(..., description="Redeemer data")
    datums: List[dict] = Field(..., description="Datum data")
```

**Fields**:
- `contract_address`: Contract address to interact with
- `beneficiary_index`: Index of allocation being claimed
- `milestone_verification`: Verification data with oracle signatures
- `signing_key_path`: Path to wallet signing key
- `transaction_cbor`: Built transaction in CBOR format

**Validation Rules**:
- Beneficiary index must be valid
- Milestone identifier must match allocation
- Quorum threshold must be met (checked before building)
- Vesting timestamp must have passed (checked before building)
- Sufficient ADA for fees and collateral

**State Transitions**:
- **Input**: Created from CLI command parameters
- **Validation**: Validated against contract state
- **Building**: Transaction built using pycardano
- **Signing**: Signed with provided key
- **Submission**: Submitted via Ogmios
- **Confirmation**: Status checked after submission

---

### 5. Network Configuration

Settings for connecting to Cardano network and services.

```python
from pydantic import BaseModel, Field
from typing import Literal

class NetworkConfiguration(BaseModel):
    """Network and service configuration"""
    network: Literal["testnet", "mainnet", "preview", "preprod"] = Field(..., description="Network name")
    ogmios_url: str = Field(..., description="Ogmios WebSocket URL (e.g., ws://localhost:1337)")
    kupo_url: str = Field(..., description="Kupo HTTP URL (e.g., http://localhost:1442)")
    cardano_node_socket: Optional[str] = Field(None, description="Path to cardano-node socket (if needed)")
    protocol_magic: Optional[int] = Field(None, description="Protocol magic number (network-specific)")
    
    def validate_connectivity(self) -> dict:
        """Validate connectivity to all services"""
        results = {
            "ogmios": False,
            "kupo": False,
            "cardano_node": False
        }
        # Implementation: test connections
        return results
```

**Fields**:
- `network`: Network identifier (testnet/mainnet/preview/preprod)
- `ogmios_url`: WebSocket URL for Ogmios service
- `kupo_url`: HTTP URL for Kupo service
- `cardano_node_socket`: Optional path to node socket

**Storage**: Configuration file (YAML/TOML) or environment variables

**Default Configurations**:
- **Testnet**: Ogmios `ws://localhost:1337`, Kupo `http://localhost:1442`
- **Mainnet**: Ogmios `ws://localhost:1337`, Kupo `http://localhost:1442` (same ports, different node)

---

### 6. Data Storage Configuration

Settings for local file storage.

```python
from pydantic import BaseModel, Field
from pathlib import Path

class DataStorageConfiguration(BaseModel):
    """Configuration for local data storage"""
    data_directory: Path = Field(
        default=Path("offchain/data"),
        description="Base directory for data storage"
    )
    milestones_directory: Path = Field(
        default=Path("offchain/data/milestones"),
        description="Directory for milestone completion data"
    )
    cache_directory: Path = Field(
        default=Path("offchain/data/cache"),
        description="Directory for cached contract states"
    )
    
    def ensure_directories(self):
        """Create directories if they don't exist"""
        self.milestones_directory.mkdir(parents=True, exist_ok=True)
        self.cache_directory.mkdir(parents=True, exist_ok=True)
```

**Fields**:
- `data_directory`: Base directory for all data files
- `milestones_directory`: Directory for milestone completion JSON files
- `cache_directory`: Directory for cached contract states

**Default Paths**:
- Base: `offchain/data/`
- Milestones: `offchain/data/milestones/`
- Cache: `offchain/data/cache/`

**File Naming**:
- Milestone files: `{milestone_identifier}.json`
- Cache files: `contract_{address_hash}.json`

---

## Relationships

```
MilestoneSchedule (1)
  ├── generates (1) DistributionContract (on-chain)
  └── contains (1..N) BeneficiaryAllocationInput

MilestoneCompletionData (1)
  ├── stored in (1) JSON file
  ├── references (1) milestone_identifier
  └── contains (N) OracleSignatureData

DistributionContractState (1)
  ├── queried from (1) Kupo indexer
  ├── represents (1) on-chain DistributionContract
  └── contains (1..N) BeneficiaryAllocationState

ReleaseTransactionInput (1)
  ├── references (1) DistributionContractState
  ├── references (1) MilestoneCompletionData
  └── builds (1) ReleaseTransaction

NetworkConfiguration (1)
  └── used by (all) network operations

DataStorageConfiguration (1)
  └── manages (all) local file storage
```

## Data Flow

### Milestone Schedule Registration
1. CLI receives `MilestoneSchedule` input
2. Validates schedule (addresses, amounts, quorum)
3. Converts to on-chain `DistributionContract` datum format
4. Returns datum for transaction building

### Milestone Completion Commitment
1. CLI receives milestone completion data
2. Validates oracle signature formats
3. Loads or creates `MilestoneCompletionData` file
4. Adds signatures incrementally
5. Updates quorum status
6. Saves to JSON file

### Milestone Status Check
1. CLI receives contract address
2. Queries `DistributionContractState` from Kupo (or cache)
3. Loads `MilestoneCompletionData` from local storage
4. Validates local data against chain state
5. Returns combined status (on-chain + local verification)

### Token Release Transaction
1. CLI receives `ReleaseTransactionInput`
2. Queries `DistributionContractState` from chain
3. Loads `MilestoneCompletionData` for milestone
4. Validates claim eligibility (vesting, quorum, not claimed)
5. Builds `ReleaseTransaction` using pycardano
6. Signs transaction
7. Submits via Ogmios
8. Returns transaction hash

## Validation Summary

### Milestone Schedule Validation
- ✅ All addresses are valid Cardano addresses (bech32)
- ✅ Token amounts are positive integers
- ✅ Quorum threshold is valid (0 < threshold <= oracle count)
- ✅ Vesting timestamps are in the future
- ✅ Milestone identifiers are non-empty

### Milestone Completion Data Validation
- ✅ Oracle signature format validation (structure, types)
- ✅ No duplicate oracle signatures
- ✅ Quorum calculation (unique oracle count)
- ⚠️ No cryptographic verification (on-chain only)

### Release Transaction Validation
- ✅ Beneficiary index is valid
- ✅ Allocation not already claimed
- ✅ Vesting timestamp has passed
- ✅ Milestone identifier matches
- ✅ Quorum threshold met
- ✅ Sufficient ADA for fees and collateral

## Serialization Formats

- **JSON**: Used for milestone completion data files, configuration files
- **CBOR**: Used for on-chain datum/redeemer serialization (via pycardano)
- **Hex**: Used for transaction CBOR, policy IDs, addresses in some contexts
- **Bech32**: Used for Cardano addresses in user-facing interfaces

## Error Handling

- **File I/O Errors**: Auto-recovery from chain, warning messages
- **Network Errors**: Retry logic, clear error messages
- **Validation Errors**: Detailed error messages with field-level details
- **Transaction Errors**: Pre-validation before submission, clear failure reasons

