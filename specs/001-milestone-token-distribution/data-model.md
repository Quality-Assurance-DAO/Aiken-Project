# Data Model: Milestone-Based Token Distribution System

**Date**: 2025-01-27  
**Feature**: 001-milestone-token-distribution

## Overview

This document defines the data structures used in the milestone-based token distribution system. All structures are designed for on-chain storage via Cardano's UTXO model using Aiken smart contracts.

## Core Entities

### 1. Distribution Contract (Datum)

The main on-chain data structure stored in the validator's UTXO datum.

```aiken
type DistributionContract {
  total_token_amount: Int
  token_policy_id: ByteArray
  beneficiary_allocations: List<BeneficiaryAllocation>
  oracle_addresses: List<Address>
  quorum_threshold: Int  // Minimum number of oracle signatures required
  total_oracles: Int     // Total number of authorized oracles
  contract_metadata: ContractMetadata
}
```

**Fields**:
- `total_token_amount`: Total tokens allocated across all beneficiaries (in smallest token unit)
- `token_policy_id`: Policy ID of the token being distributed (ByteArray for Cardano native tokens)
- `beneficiary_allocations`: List of all beneficiary allocations (see below)
- `oracle_addresses`: List of authorized oracle addresses that can verify milestones
- `quorum_threshold`: Minimum number of oracle signatures required (e.g., 3 of 5)
- `total_oracles`: Total count of authorized oracles (for quorum calculation)
- `contract_metadata`: Additional metadata (creation timestamp, creator address, etc.)

**Validation Rules**:
- `quorum_threshold` must be <= `total_oracles`
- `quorum_threshold` must be > 0
- `total_token_amount` must equal sum of all `beneficiary_allocations[].token_amount`
- All `beneficiary_allocations` must have unique `beneficiary_address` + `milestone_identifier` combinations
- All `oracle_addresses` must be valid Cardano addresses

**State Transitions**:
- **Creation**: Contract created with all allocations unclaimed (`claimed: false`)
- **Claim**: When beneficiary claims, their allocation's `claimed` flag set to `true`
- **Completion**: When all allocations are claimed, contract can be closed (optional)

---

### 2. Beneficiary Allocation

Represents a single beneficiary's entitlement to tokens for a specific milestone.

```aiken
type BeneficiaryAllocation {
  beneficiary_address: Address
  token_amount: Int
  milestone_identifier: ByteArray  // Unique identifier for the milestone
  vesting_timestamp: Int          // POSIXTime (slot-based timestamp)
  claimed: Bool                   // Whether this allocation has been claimed
}
```

**Fields**:
- `beneficiary_address`: Cardano address where tokens will be sent
- `token_amount`: Amount of tokens allocated (in smallest token unit)
- `milestone_identifier`: Unique identifier linking to milestone verification
- `vesting_timestamp`: Absolute timestamp when tokens become claimable (POSIXTime)
- `claimed`: Boolean flag preventing double-claiming

**Validation Rules**:
- `beneficiary_address` must be a valid, spendable Cardano address
- `token_amount` must be > 0
- `milestone_identifier` must be non-empty
- `vesting_timestamp` must be in the future at contract creation time
- `claimed` starts as `false`, can only transition to `true` once

**State Transitions**:
- **Initial**: `claimed: false` at contract creation
- **Claim**: `claimed: true` after successful claim transaction
- **No reversal**: Once `claimed: true`, cannot revert to `false`

---

### 3. Milestone Verification (Redeemer Data)

Evidence that a milestone has been completed, provided during claim transactions.

```aiken
type MilestoneVerification {
  milestone_identifier: ByteArray
  oracle_signatures: List<OracleSignature>
  verification_timestamp: Int  // POSIXTime when verification occurred
}
```

**Fields**:
- `milestone_identifier`: Must match the `milestone_identifier` in the beneficiary's allocation
- `oracle_signatures`: List of oracle signatures attesting to milestone completion
- `verification_timestamp`: When the milestone was verified (for audit purposes)

**Validation Rules**:
- `milestone_identifier` must match the allocation being claimed
- `oracle_signatures` must contain at least `quorum_threshold` valid signatures
- Each signature must be from an authorized oracle (address in `oracle_addresses`)
- Duplicate signatures from the same oracle count only once toward quorum
- Unauthorized signatures are ignored (don't count toward quorum, don't cause rejection)

---

### 4. Oracle Signature

Cryptographic proof from an authorized oracle that a milestone is complete.

```aiken
type OracleSignature {
  oracle_address: Address
  signature_hash: ByteArray  // Hash of the signature (verified off-chain)
  signed_data: ByteArray    // Data that was signed (milestone_id + timestamp)
  signature_timestamp: Int  // POSIXTime when signature was created
}
```

**Fields**:
- `oracle_address`: Address of the oracle that created the signature
- `signature_hash`: Hash of the Ed25519 signature (for on-chain verification)
- `signed_data`: The data that was signed (typically milestone_id concatenated with timestamp)
- `signature_timestamp`: When the signature was created

**Validation Rules**:
- `oracle_address` must be in the contract's `oracle_addresses` list
- `signature_hash` must be valid (format validation, not full crypto verification)
- `signed_data` must include the `milestone_identifier` being claimed
- Full cryptographic verification happens off-chain before transaction submission

**Note**: Full signature verification is expensive on-chain. The validator checks:
1. Oracle address is authorized
2. Signature hash format is valid
3. Signed data includes correct milestone identifier
Full Ed25519 verification happens off-chain before transaction construction.

---

### 5. Claim Transaction (Redeemer)

The action taken by a beneficiary to claim their allocation.

```aiken
type ClaimRedeemer {
  beneficiary_index: Int  // Index in beneficiary_allocations list
  milestone_verification: MilestoneVerification
}
```

**Fields**:
- `beneficiary_index`: Index of the beneficiary's allocation in the `beneficiary_allocations` list
- `milestone_verification`: Proof that the milestone has been completed

**Validation Rules**:
- `beneficiary_index` must be valid (0 <= index < length of allocations)
- Allocation at `beneficiary_index` must have `claimed: false`
- Current transaction time must be >= allocation's `vesting_timestamp`
- `milestone_verification.milestone_identifier` must match allocation's `milestone_identifier`
- Quorum check must pass (sufficient valid oracle signatures)
- Transaction output must send correct `token_amount` to `beneficiary_address`
- Transaction must include sufficient ADA for fees (from beneficiary's wallet)

**State Changes**:
- Sets `beneficiary_allocations[beneficiary_index].claimed = true`
- Transfers tokens from contract UTXO to beneficiary address
- Updates datum with modified allocation list

---

### 6. Contract Metadata

Additional metadata stored with the distribution contract.

```aiken
type ContractMetadata {
  creation_timestamp: Int      // POSIXTime when contract was created
  creator_address: Address      // Address that created the contract
  contract_version: ByteArray   // Version identifier for contract schema
  description: Option<ByteArray> // Optional human-readable description
}
```

**Fields**:
- `creation_timestamp`: When the contract was created (for audit trail)
- `creator_address`: Address that funded/created the contract
- `contract_version`: Version identifier for schema compatibility
- `description`: Optional description (can be None)

---

## Relationships

```
DistributionContract (1)
  ├── contains (1..N) BeneficiaryAllocation
  ├── references (1..N) OracleAddress (via oracle_addresses list)
  └── has (1) ContractMetadata

ClaimTransaction (1)
  ├── references (1) BeneficiaryAllocation (via beneficiary_index)
  ├── includes (1) MilestoneVerification
  └── MilestoneVerification contains (N) OracleSignature (where N >= quorum_threshold)
```

## Data Flow

### Contract Creation
1. Treasury administrator creates `DistributionContract` datum
2. Validates all allocations (addresses, amounts, timestamps)
3. Locks tokens in contract UTXO
4. Stores datum on-chain

### Milestone Verification (Off-Chain)
1. Oracles observe project progress
2. Authorized oracles sign milestone completion
3. Signatures collected until quorum reached
4. `MilestoneVerification` constructed with signatures

### Claim Transaction
1. Beneficiary constructs `ClaimRedeemer` with `beneficiary_index` and `MilestoneVerification`
2. Validator checks:
   - Allocation not already claimed
   - Vesting timestamp passed
   - Milestone identifier matches
   - Quorum threshold met
   - Token amount correct
3. If valid:
   - Marks allocation as claimed
   - Transfers tokens to beneficiary
   - Updates datum

## Constraints and Limits

- **Maximum beneficiaries per contract**: 50+ (tested), potentially 100+ with optimization
- **Datum size**: Must stay within Cardano transaction size limits (~16KB)
- **Oracle signatures**: Store signature hashes, not full signatures (saves space)
- **Token amounts**: Stored in smallest unit (e.g., lovelace for ADA)
- **Timestamps**: All use POSIXTime (Cardano slot-based time)

## Validation Summary

### Contract Creation Validation
- ✅ All beneficiary addresses are valid and spendable
- ✅ Total token amount matches sum of allocations
- ✅ Quorum threshold is valid (0 < threshold <= total_oracles)
- ✅ Vesting timestamps are in the future
- ✅ Contract holds sufficient tokens for all allocations

### Claim Transaction Validation
- ✅ Beneficiary index is valid
- ✅ Allocation not already claimed
- ✅ Vesting timestamp has passed
- ✅ Milestone identifier matches allocation
- ✅ Quorum threshold met (sufficient valid oracle signatures)
- ✅ Token amount matches allocation
- ✅ Beneficiary address matches allocation
- ✅ Transaction has sufficient ADA for fees

## Future Considerations

- **Partial claims**: Currently not supported (all-or-nothing per allocation)
- **Accelerated vesting**: Not supported (absolute timestamps only)
- **Dynamic quorum**: Not supported (set at contract creation)
- **Multiple milestones per beneficiary**: Supported via multiple allocations with different milestone_identifiers

