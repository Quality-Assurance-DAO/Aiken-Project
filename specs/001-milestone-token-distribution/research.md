# Research: Milestone-Based Token Distribution System

**Date**: 2025-01-27  
**Feature**: 001-milestone-token-distribution

## Purpose

This document consolidates research findings to resolve all "NEEDS CLARIFICATION" items identified in the Technical Context section of plan.md.

## Research Areas

### 1. Cardano Transaction Building Libraries

**Decision**: Use Cardano CLI tools for initial implementation, with option to migrate to libraries like `cardano-cli-js`, `lucid`, or `meson` for advanced features.

**Rationale**: 
- Cardano CLI provides stable, well-documented transaction building capabilities
- Standard toolchain that all Cardano developers have access to
- Supports all required operations: transaction construction, signing, submission
- Can be wrapped in shell scripts for CLI commands
- Libraries can be added later for programmatic access if needed

**Alternatives Considered**:
- **cardano-cli-js**: JavaScript library, good for Node.js integration but adds dependency
- **lucid**: TypeScript library, excellent for web integration but requires TypeScript setup
- **meson**: Python library, good for Python-based tooling but adds Python dependency
- **cardano-serialization-lib**: Low-level, more complex but maximum control

**Implementation Note**: Start with Cardano CLI wrapped in bash scripts. Evaluate library migration during Phase 2 if programmatic transaction building becomes critical.

---

### 2. Cardano Script Execution Budget and Constraints

**Decision**: Design validator to operate within standard Cardano limits:
- Transaction size: ~16KB maximum
- Execution units: Budget varies by network, design for <10M CPU units and <10M memory units
- UTXO model: Single UTXO per distribution contract, track claims via datum updates

**Rationale**:
- Cardano testnet and mainnet have different execution budgets, but validator logic should be efficient regardless
- UTXO model requires careful datum design to track state without exceeding size limits
- Multi-recipient allocations must be structured efficiently in datum
- Oracle signatures should be stored compactly (addresses + signature hashes rather than full signatures)

**Alternatives Considered**:
- **Multiple UTXOs per contract**: Rejected - increases complexity and transaction overhead
- **Off-chain state tracking**: Rejected - defeats purpose of on-chain verification
- **Compressed signature storage**: Accepted - store signature hashes/addresses, verify off-chain before submission

**Implementation Note**: 
- Use Aiken's built-in optimization features
- Test execution budget on testnet before mainnet deployment
- Consider datum compression techniques if contract size becomes an issue
- Monitor transaction fees as they scale with execution units

---

### 3. Oracle Signature Verification Pattern

**Decision**: Store oracle addresses and signature hashes in datum. Verify signatures off-chain before transaction submission. Validator checks quorum of valid oracle addresses.

**Rationale**:
- Full cryptographic signature verification on-chain is expensive
- Off-chain verification reduces execution budget usage
- Validator can verify that claimed oracle addresses match authorized set
- Signature hashes prevent replay attacks
- Quorum logic remains on-chain for security

**Alternatives Considered**:
- **Full on-chain signature verification**: Rejected - too expensive in execution budget
- **Pure off-chain verification**: Rejected - security risk, no on-chain enforcement
- **Hybrid approach**: Accepted - off-chain verify, on-chain validate quorum

**Implementation Note**:
- Oracle signatures should include milestone identifier and timestamp
- Signature format: Ed25519 signatures compatible with Cardano
- Testnet: Use test keys for simulation
- Mainnet: Integrate with real oracle infrastructure

---

### 4. Multi-Recipient Allocation Datum Structure

**Decision**: Store allocations as a list/array in datum with fields: beneficiary address, token amount, milestone identifier, vesting timestamp, claimed flag.

**Rationale**:
- Aiken supports list types efficiently
- Allows iteration for validation
- Enables partial contract consumption (one beneficiary claims, others remain)
- Claimed flags prevent double-claiming
- Structure supports 50+ beneficiaries within transaction size limits

**Alternatives Considered**:
- **Separate UTXO per beneficiary**: Rejected - too many UTXOs, complex management
- **Map/dictionary structure**: Considered - Aiken map support varies, list is more reliable
- **Compressed encoding**: Considered - may be needed if beneficiary count exceeds 100

**Implementation Note**:
- Test with 50 beneficiaries first
- Monitor datum size
- Consider compression if needed for larger distributions

---

### 5. Vesting Timestamp Validation

**Decision**: Use Cardano's POSIXTime (slot-based time) for vesting timestamps. Validator checks current transaction time against vesting timestamp.

**Rationale**:
- Cardano uses slot-based time (POSIXTime)
- Transaction validity interval provides time context
- Standard pattern in Cardano smart contracts
- Supports absolute timestamps as specified in requirements

**Alternatives Considered**:
- **Relative time durations**: Rejected - requirements specify absolute timestamps
- **Block height**: Rejected - less precise than POSIXTime
- **External time oracle**: Rejected - unnecessary complexity

**Implementation Note**:
- Convert human-readable timestamps to POSIXTime during contract creation
- Validate timestamps are in the future at contract creation
- Test timestamp enforcement on testnet

---

### 6. Testnet to Mainnet Migration Path

**Decision**: Design contract with configuration parameters (oracle addresses, token policy IDs) that can be swapped between testnet and mainnet without code changes.

**Rationale**:
- Reduces risk of bugs during migration
- Allows same validator code for both networks
- Configuration changes are simpler than code changes
- Supports iterative testing on testnet

**Alternatives Considered**:
- **Separate contracts for testnet/mainnet**: Rejected - code duplication, maintenance burden
- **Network detection in validator**: Considered - adds complexity, configuration is simpler

**Implementation Note**:
- Store network-specific values (oracle addresses, policy IDs) in datum or as contract parameters
- Document migration checklist
- Test migration process on testnet first

---

## Summary of Resolved Clarifications

1. ✅ **Transaction Building**: Cardano CLI tools (with library option for future)
2. ✅ **Execution Budget**: Design for <10M CPU/memory units, monitor on testnet
3. ✅ **Oracle Verification**: Hybrid approach (off-chain verify, on-chain quorum check)
4. ✅ **Datum Structure**: List of allocation records with claimed flags
5. ✅ **Vesting Timestamps**: POSIXTime-based validation
6. ✅ **Migration Path**: Configuration-based, same code for testnet/mainnet

## Remaining Implementation Decisions

These will be made during implementation:
- Specific Aiken version and standard library features to use
- Exact datum encoding format (CBOR details)
- Transaction fee estimation strategy
- Error message formats for failed validations
- CLI command interface design (flags, arguments, output format)

## References

- Aiken Language Documentation: https://aiken-lang.org
- Cardano Developer Portal: https://developers.cardano.org
- QA-DAO Token Distribution Framework: https://github.com/Quality-Assurance-DAO/Token-Distribution-Framework
- Cardano UTXO Model: https://docs.cardano.org/learn/cardano-architecture


