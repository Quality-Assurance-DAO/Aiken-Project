# Validator Contract Specification

**Date**: 2025-01-27  
**Feature**: 001-milestone-token-distribution

## Overview

This document specifies the on-chain validator contract interface for the milestone-based token distribution system. The validator enforces milestone verification, quorum requirements, vesting timestamps, and prevents double-claiming.

## Validator Interface

### Validator Script

**Type**: Spending Validator  
**Language**: Aiken  
**Location**: `src/validator/lib.aiken`

### Datum Type

See `data-model.md` for complete `DistributionContract` structure.

**Key Fields**:
- `beneficiary_allocations: List<BeneficiaryAllocation>`
- `oracle_addresses: List<Address>`
- `quorum_threshold: Int`
- `total_oracles: Int`

### Redeemer Type

```aiken
type ClaimRedeemer {
  beneficiary_index: Int
  milestone_verification: MilestoneVerification
}
```

## Validation Logic

### Entry Point: `validate`

**Signature**: `validate(datum: DistributionContract, redeemer: ClaimRedeemer, context: ScriptContext) -> Bool`

**Validation Steps**:

1. **Beneficiary Index Validation**
   - Check `redeemer.beneficiary_index` is within bounds: `0 <= index < length(datum.beneficiary_allocations)`
   - Extract allocation: `allocation = datum.beneficiary_allocations[redeemer.beneficiary_index]`

2. **Double-Claim Prevention**
   - Check `allocation.claimed == false`
   - Reject if already claimed

3. **Vesting Timestamp Check**
   - Get current transaction time from `context.tx_info.valid_range`
   - Check `current_time >= allocation.vesting_timestamp`
   - Reject if vesting period has not started

4. **Milestone Identifier Match**
   - Check `redeemer.milestone_verification.milestone_identifier == allocation.milestone_identifier`
   - Reject if identifiers don't match

5. **Quorum Verification**
   - Extract `oracle_signatures = redeemer.milestone_verification.oracle_signatures`
   - Filter signatures to only those from `datum.oracle_addresses`
   - Remove duplicate oracle addresses (count each oracle only once)
   - Count valid signatures: `valid_count = length(filtered_signatures)`
   - Check `valid_count >= datum.quorum_threshold`
   - Reject if quorum not met

6. **Token Transfer Validation**
   - Check transaction outputs for one output sending tokens to `allocation.beneficiary_address`
   - Verify output contains exactly `allocation.token_amount` of token with `datum.token_policy_id`
   - Verify output includes sufficient ADA for fees (min ADA requirement)
   - Reject if token amount or address incorrect

7. **Datum Update Validation**
   - Check that new datum (if contract continues) has `allocation.claimed = true`
   - Verify other allocations remain unchanged
   - If all allocations claimed, contract can be closed (no datum required)

**Return**: `true` if all validations pass, `false` otherwise

## Error Conditions

The validator rejects transactions (returns `false`) in these cases:

1. **Invalid Beneficiary Index**: Index out of bounds
2. **Already Claimed**: Allocation already has `claimed: true`
3. **Vesting Not Met**: Current time < `vesting_timestamp`
4. **Milestone Mismatch**: Milestone identifier doesn't match allocation
5. **Quorum Not Met**: Insufficient valid oracle signatures
6. **Invalid Token Amount**: Output doesn't match allocation amount
7. **Invalid Beneficiary Address**: Output address doesn't match allocation
8. **Unauthorized Oracle**: Signature from address not in `oracle_addresses` (ignored, doesn't cause rejection)

## Success Conditions

Transaction succeeds when:
- ✅ All validation steps pass
- ✅ Tokens transferred to correct beneficiary address
- ✅ Datum updated to mark allocation as claimed
- ✅ Transaction fees paid from beneficiary's wallet balance

## Gas/Execution Budget Considerations

- Quorum verification: O(N) where N = number of signatures
- Allocation lookup: O(1) via index
- Oracle address filtering: O(M*N) where M = oracle addresses, N = signatures
- Design target: <10M CPU units, <10M memory units

## Security Properties

1. **Double-Claim Prevention**: Enforced by `claimed` flag in datum
2. **Quorum Enforcement**: On-chain validation of oracle signatures
3. **Vesting Enforcement**: Time-based access control via POSIXTime
4. **Token Amount Integrity**: Validated against allocation in datum
5. **Oracle Authorization**: Only signatures from `oracle_addresses` count toward quorum

## Testing Requirements

- Unit tests for each validation step
- Integration tests for full claim flow
- Edge cases: concurrent claims, invalid signatures, quorum failures
- Performance tests: 50+ beneficiary allocations

