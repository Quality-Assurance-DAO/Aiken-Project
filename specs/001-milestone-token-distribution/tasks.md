# Implementation Tasks: Milestone-Based Token Distribution System

**Feature**: 001-milestone-token-distribution  
**Branch**: `001-milestone-token-distribution`  
**Date**: 2025-01-27  
**Based on**: [plan.md](./plan.md), [spec.md](./spec.md), [data-model.md](./data-model.md), [contracts/](./contracts/)

## Overview

This document provides an actionable, dependency-ordered task list for implementing the milestone-based token distribution system on Cardano testnet using Aiken smart contracts. Tasks are organized by phase, with each user story implemented independently to enable incremental delivery and testing.

**Total Tasks**: 54  
**MVP Scope**: Phase 1-3 (Setup + Foundational + User Story 1) = 23 tasks

## Implementation Strategy

**MVP First**: Implement User Story 1 (P1) first to deliver core value - enabling beneficiaries to claim tokens. This provides immediate value and validates the core architecture.

**Incremental Delivery**: Each user story phase is independently testable and can be deployed separately. Stories build upon foundational infrastructure but remain modular.

**Parallel Opportunities**: Tasks marked with `[P]` can be executed in parallel as they work on different files with no dependencies on incomplete tasks.

## Dependencies

### User Story Completion Order

1. **Phase 1-2**: Setup and Foundational (must complete before any user stories)
2. **Phase 3**: User Story 1 - Beneficiary Claims Tokens (P1) - **MVP**
3. **Phase 4**: User Story 2 - Oracle Quorum Verification (P2) - depends on US1 validator structure
4. **Phase 5**: User Story 3 - Multi-Recipient Distribution (P3) - depends on US1 single-recipient implementation
5. **Phase 6**: User Story 4 - Vesting Enforcement (P4) - depends on US1 timestamp validation
6. **Phase 7**: Polish & Cross-Cutting Concerns

**Note**: User Stories 2-4 can be implemented in parallel after User Story 1 is complete, as they extend different aspects of the system.

## Phase 1: Setup

**Goal**: Initialize project structure and development environment.

**Independent Test**: Project builds successfully with `aiken build` and test framework runs.

### Setup Tasks

- [X] T001 Create project structure per implementation plan in src/validator/, src/cli/, src/lib/, tests/validator/, tests/integration/, tests/unit/, scripts/
- [X] T002 Initialize Aiken project configuration with aiken.toml in project root
- [X] T003 Create shared type definitions in src/lib/types.aiken for Address, ByteArray, Int, Bool, List, Option
- [X] T004 Create validation helper functions in src/lib/validation.aiken for address validation, timestamp validation, amount validation
- [X] T005 [P] Create test data fixtures directory test-data/ with sample allocations.json and oracles.json
- [X] T006 [P] Create deployment scripts directory scripts/ with placeholder deploy.sh, mint_test_tokens.sh, simulate_oracles.sh

## Phase 2: Foundational

**Goal**: Implement core data structures and types that all user stories depend on.

**Independent Test**: All data types compile and can be instantiated with test data. Datum and redeemer types serialize/deserialize correctly.

**Dependencies**: Phase 1 must be complete.

### Foundational Tasks

- [X] T007 Implement ContractMetadata type in src/lib/types.aiken with creation_timestamp, creator_address, contract_version, description fields
- [X] T008 Implement BeneficiaryAllocation type in src/validator/datum.aiken with beneficiary_address, token_amount, milestone_identifier, vesting_timestamp, claimed fields
- [X] T009 Implement DistributionContract datum type in src/validator/datum.aiken with total_token_amount, token_policy_id, beneficiary_allocations, oracle_addresses, quorum_threshold, total_oracles, contract_metadata fields
- [X] T010 Implement OracleSignature type in src/validator/oracle.aiken with oracle_address, signature_hash, signed_data, signature_timestamp fields
- [X] T011 Implement MilestoneVerification type in src/validator/redeemer.aiken with milestone_identifier, oracle_signatures, verification_timestamp fields
- [X] T012 Implement ClaimRedeemer type in src/validator/redeemer.aiken with beneficiary_index, milestone_verification fields
- [X] T013 Create validator skeleton in src/validator/lib.aiken with validate function signature accepting DistributionContract datum, ClaimRedeemer redeemer, ScriptContext context

## Phase 3: User Story 1 - Beneficiary Claims Tokens (P1)

**Goal**: Enable beneficiaries to claim their allocated tokens after milestone verification and vesting requirements are met.

**Independent Test**: Create a distribution contract with a single beneficiary allocation, verify a milestone with oracle signatures, and successfully claim tokens. Verify tokens transfer to beneficiary address and allocation is marked as claimed.

**Dependencies**: Phase 1-2 must be complete.

**Acceptance Criteria**:
- Beneficiary receives allocated token amount when valid claim submitted
- Multiple beneficiaries can claim independently from same contract
- Claims before vesting timestamp are rejected
- Double-claiming is prevented

### User Story 1 Tasks

- [X] T014 [US1] Implement beneficiary index validation in src/validator/lib.aiken validate function to check index is within bounds
- [X] T015 [US1] Implement double-claim prevention check in src/validator/lib.aiken validate function to verify allocation.claimed == false
- [X] T016 [US1] Implement vesting timestamp validation in src/validator/lib.aiken validate function to check current_time >= allocation.vesting_timestamp
- [X] T017 [US1] Implement milestone identifier matching in src/validator/lib.aiken validate function to verify redeemer.milestone_verification.milestone_identifier == allocation.milestone_identifier
- [X] T018 [US1] Implement token transfer validation in src/validator/lib.aiken validate function to verify transaction output sends correct token_amount to beneficiary_address
- [X] T019 [US1] Implement datum update logic in src/validator/lib.aiken validate function to mark allocation.claimed = true in updated datum
- [X] T020 [US1] Create unit test for valid claim scenario in tests/validator/validator_test.aiken
- [X] T021 [US1] Create unit test for double-claim prevention in tests/validator/validator_test.aiken
- [X] T022 [US1] Create unit test for vesting timestamp enforcement in tests/validator/validator_test.aiken
- [X] T023 [US1] Create integration test for single beneficiary claim flow in tests/integration/multi_recipient_test.aiken

## Phase 4: User Story 2 - Oracle Quorum Verification (P2)

**Goal**: Verify that milestone completion is attested by a sufficient quorum of authorized oracle signatures before allowing claims.

**Independent Test**: Simulate multiple oracle signatures, verify quorum logic accepts valid quorums and rejects insufficient signatures, and confirm milestone state transitions.

**Dependencies**: Phase 1-3 must be complete (needs validator structure from US1).

**Acceptance Criteria**:
- Quorum threshold is enforced (e.g., 3 of 5 oracles)
- Unauthorized oracle signatures are ignored
- Duplicate signatures from same oracle count only once
- Insufficient signatures reject the claim

### User Story 2 Tasks

- [X] T024 [US2] Implement oracle address filtering logic in src/validator/oracle.aiken to filter signatures to only those from authorized oracle_addresses
- [X] T025 [US2] Implement duplicate oracle removal logic in src/validator/oracle.aiken to count each oracle address only once toward quorum
- [X] T026 [US2] Implement quorum threshold check in src/validator/lib.aiken validate function to verify valid_count >= quorum_threshold
- [X] T027 [US2] Implement unauthorized signature handling in src/validator/oracle.aiken to ignore signatures from non-authorized addresses without causing rejection
- [X] T028 [US2] Create unit test for valid quorum acceptance in tests/validator/oracle_test.aiken
- [X] T029 [US2] Create unit test for quorum failure rejection in tests/validator/oracle_test.aiken
- [X] T030 [US2] Create unit test for duplicate signature handling in tests/validator/oracle_test.aiken
- [X] T031 [US2] Create integration test for quorum verification flow in tests/integration/quorum_test.aiken

## Phase 5: User Story 3 - Multi-Recipient Distribution (P3)

**Goal**: Support multiple beneficiary allocations within a single distribution contract with different vesting schedules and milestone requirements.

**Independent Test**: Create a distribution contract with allocations for multiple beneficiaries, each with different token amounts, vesting timestamps, and milestone identifiers. Verify beneficiaries can claim independently.

**Dependencies**: Phase 1-3 must be complete (needs single-recipient implementation from US1).

**Acceptance Criteria**:
- Contract supports 50+ simultaneous beneficiary allocations
- Each beneficiary can claim independently
- Contract preserves unclaimed allocations when one beneficiary claims
- Different vesting timestamps are enforced per allocation

### User Story 3 Tasks

- [X] T032 [US3] Implement multi-allocation datum validation in src/validator/lib.aiken validate function to handle list of beneficiary_allocations
- [X] T033 [US3] Implement allocation preservation logic in src/validator/lib.aiken validate function to update only claimed allocation while preserving others
- [X] T034 [US3] Implement total token amount validation in src/lib/validation.aiken to verify total_token_amount equals sum of all allocations
- [X] T035 [US3] Create unit test for multi-recipient contract creation in tests/validator/datum_test.aiken
- [X] T036 [US3] Create integration test for sequential multi-recipient claims in tests/integration/multi_recipient_test.aiken
- [X] T037 [US3] Create performance test for 50+ beneficiary allocations in tests/integration/multi_recipient_test.aiken

## Phase 6: User Story 4 - Vesting and Timestamp Constraints (P4)

**Goal**: Enforce vesting timestamps and prevent claims before vesting periods begin, ensuring claims occur within valid time windows.

**Independent Test**: Create allocations with specific vesting timestamps and verify that claims before the timestamp are rejected while claims after are accepted.

**Dependencies**: Phase 1-3 must be complete (needs timestamp validation from US1).

**Acceptance Criteria**:
- Claims before vesting timestamp are rejected
- Claims at or after vesting timestamp are accepted
- Different allocations can have different vesting timestamps
- Timestamp validation uses POSIXTime correctly

### User Story 4 Tasks

- [X] T038 [US4] Enhance vesting timestamp validation in src/validator/lib.aiken validate function to handle POSIXTime comparison with transaction validity range
- [X] T039 [US4] Implement per-allocation vesting enforcement in src/validator/lib.aiken validate function to check each allocation's vesting_timestamp independently
- [X] T040 [US4] Create unit test for vesting timestamp enforcement in tests/validator/validator_test.aiken
- [X] T041 [US4] Create integration test for multi-allocation vesting scenarios in tests/integration/vesting_test.aiken
- [X] T042 [US4] Create test for future vesting timestamp validation at contract creation in tests/validator/datum_test.aiken

## Phase 7: CLI Tools and Off-Chain Scripts

**Goal**: Provide CLI commands and scripts for contract creation, claim transactions, and utility operations.

**Independent Test**: CLI commands can create contracts, build claim transactions, verify milestones, and query contract state. Scripts can deploy contracts and simulate oracle signatures.

**Dependencies**: Phase 1-6 should be complete (needs validator implementation).

### CLI Tasks

- [X] T043 [P] Implement create command in src/cli/create.aiken to generate distribution contract datum from allocations and oracle files
- [X] T044 [P] Implement claim command in src/cli/claim.aiken to build and submit claim transactions using Cardano CLI
- [X] T045 [P] Implement verify-milestone command in src/cli/utils.aiken to verify oracle signatures off-chain before claim
- [X] T046 [P] Implement query command in src/cli/utils.aiken to query contract state from blockchain
- [X] T047 [P] Implement simulate-oracles command in scripts/simulate_oracles.sh to generate test oracle signatures for testnet

## Phase 8: Polish & Cross-Cutting Concerns

**Goal**: Finalize deployment scripts, error handling, documentation, and testnet deployment preparation.

**Independent Test**: All scripts execute successfully, error messages are clear, and testnet deployment completes without errors.

**Dependencies**: All previous phases should be complete.

### Polish Tasks

- [X] T048 Implement deploy.sh script in scripts/deploy.sh to automate testnet contract deployment
- [X] T049 Implement mint_test_tokens.sh script in scripts/mint_test_tokens.sh to mint test tokens on testnet
- [X] T050 Add comprehensive error handling to all CLI commands in src/cli/ with clear error messages
- [X] T051 Add input validation to all CLI commands in src/cli/ for address format, amount ranges, timestamp validity
- [X] T052 Create testnet deployment guide in docs/testnet-deployment.md with step-by-step instructions
- [X] T053 Add execution budget monitoring to validator tests in tests/validator/validator_test.aiken
- [X] T054 Create mainnet migration checklist in docs/mainnet-migration.md with oracle and token policy ID replacement steps

## Parallel Execution Examples

### User Story 1 (Phase 3)
Tasks T020-T023 can be written in parallel as they test different aspects:
- T020: Valid claim test
- T021: Double-claim test  
- T022: Vesting test
- T023: Integration test

### User Story 2 (Phase 4)
Tasks T024-T031 can be organized in parallel:
- T024-T025: Oracle filtering logic (can be done together)
- T026-T027: Quorum validation (depends on T024-T025)
- T028-T031: Tests (can be written in parallel after logic complete)

### User Story 3 (Phase 5)
Tasks T032-T037 can be parallelized:
- T032-T034: Multi-allocation logic (sequential within group)
- T035-T037: Tests (can be written in parallel)

### CLI Tools (Phase 7)
All CLI tasks T043-T047 are marked [P] and can be implemented in parallel as they work on different commands.

## Testing Strategy

**Unit Tests**: Test individual validator functions, data types, and validation logic in isolation.

**Integration Tests**: Test full claim flows, multi-recipient scenarios, quorum verification, and vesting enforcement end-to-end.

**Performance Tests**: Verify system handles 50+ beneficiary allocations within transaction size and execution budget limits.

**Testnet Tests**: Deploy to testnet and verify real transactions succeed, monitoring execution budget and transaction fees.

## Success Metrics

- ✅ All unit tests pass
- ✅ All integration tests pass  
- ✅ Validator executes within Cardano execution budget (<10M CPU, <10M memory)
- ✅ Supports 50+ beneficiary allocations per contract
- ✅ Testnet deployment successful
- ✅ All user story acceptance criteria met
- ✅ CLI commands functional and user-friendly

## Notes

- Tasks marked with `[P]` can be executed in parallel
- Tasks marked with `[US1]`, `[US2]`, etc. belong to specific user story phases
- File paths are relative to project root
- Each task should be independently completable by an LLM with the provided context
- MVP scope focuses on delivering User Story 1 first for immediate value

