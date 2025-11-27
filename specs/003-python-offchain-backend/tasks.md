# Implementation Tasks: Python Off-Chain Backend MVP

**Feature**: 003-python-offchain-backend  
**Branch**: `003-python-offchain-backend`  
**Date**: 2025-01-27  
**Based on**: [plan.md](./plan.md), [spec.md](./spec.md), [data-model.md](./data-model.md), [contracts/](./contracts/), [research.md](./research.md)

## Overview

This document provides an actionable, dependency-ordered task list for implementing the Python off-chain backend for milestone-based token distribution on Cardano. Tasks are organized by phase, with each user story implemented independently to enable incremental delivery and testing.

**Total Tasks**: 97  
**MVP Scope**: Phase 1-4 (Setup + Foundational + US1 + US2) = 40 tasks

## Implementation Strategy

**MVP First**: Implement User Stories 1 and 2 (both P1) first to deliver core value - enabling environment initialization and milestone schedule registration. This provides immediate administrative capability and validates the core architecture.

**Incremental Delivery**: Each user story phase is independently testable and can be deployed separately. Stories build upon foundational infrastructure but remain modular.

**Parallel Opportunities**: Tasks marked with `[P]` can be executed in parallel as they work on different files with no dependencies on incomplete tasks.

## Dependencies

### User Story Completion Order

1. **Phase 1-2**: Setup and Foundational (must complete before any user stories)
2. **Phase 3**: User Story 1 - Administrator Initializes Off-Chain Environment (P1) - **MVP Core**
3. **Phase 4**: User Story 2 - Administrator Registers New Milestone Schedule (P1) - **MVP Core**
4. **Phase 5**: User Story 3 - Administrator Commits Milestone Completion Data (P2)
5. **Phase 6**: User Story 4 - User Checks Milestone Completion State (P2)
6. **Phase 7**: User Story 5 - System Calculates Token Distribution Amounts (P2)
7. **Phase 8**: User Story 6 - Beneficiary Submits Token Release Transaction (P1) - **MVP Core**
8. **Phase 9**: Polish & Cross-Cutting Concerns

**Note**: User Stories 3-5 (P2) can be implemented in parallel after User Stories 1-2 are complete, as they extend different aspects of the system. User Story 6 depends on User Stories 3-5 for complete functionality.

## Phase 1: Setup

**Goal**: Initialize project structure and development environment for Python off-chain backend.

**Independent Test**: Project structure exists, dependencies install successfully, and basic Python modules can be imported.

### Setup Tasks

- [X] T001 Create project structure per implementation plan: offchain/offchain/, offchain/tests/, infra/, contracts/compiled/
- [X] T002 Create Python package structure with __init__.py files in offchain/offchain/ and offchain/tests/
- [X] T003 Create requirements.txt in offchain/ with pycardano>=0.9.0, typer>=0.9.0, websockets>=11.0, httpx>=0.25.0, pydantic>=2.0, pytest, pytest-asyncio
- [X] T004 Create setup.py or pyproject.toml in offchain/ for package installation
- [X] T005 [P] Create .gitignore in offchain/ to exclude __pycache__/, *.pyc, .venv/, data/, *.log
- [X] T006 [P] Create README.md in offchain/ with installation and usage instructions
- [X] T007 Create cli.py entry point in offchain/ with typer app initialization

## Phase 2: Foundational

**Goal**: Implement core data models, configuration management, and infrastructure setup that all user stories depend on.

**Independent Test**: All data models can be instantiated with test data, configuration loads correctly, and docker-compose services can be started.

**Dependencies**: Phase 1 must be complete.

### Foundational Tasks

- [X] T008 Implement NetworkConfiguration model in offchain/offchain/config.py with network, ogmios_url, kupo_url, cardano_node_socket fields
- [X] T009 Implement DataStorageConfiguration model in offchain/offchain/config.py with data_directory, milestones_directory, cache_directory fields
- [X] T010 Implement configuration loading logic in offchain/offchain/config.py to load from YAML file or environment variables
- [X] T011 Implement MilestoneSchedule model in offchain/offchain/models.py with token_policy_id, beneficiary_allocations, oracle_addresses, quorum_threshold, contract_metadata fields per data-model.md
- [X] T012 Implement BeneficiaryAllocationInput model in offchain/offchain/models.py with beneficiary_address, token_amount, milestone_identifier, vesting_timestamp fields
- [X] T013 Implement MilestoneCompletionData model in offchain/offchain/models.py with milestone_identifier, oracle_signatures, verification_timestamp, quorum_status, quorum_threshold, total_oracles fields
- [X] T014 Implement OracleSignatureData model in offchain/offchain/models.py with oracle_address, signature, signed_data, signature_timestamp fields
- [X] T015 Implement DistributionContractState model in offchain/offchain/models.py with contract_address, utxo_tx_hash, utxo_index, datum, beneficiary_allocations fields
- [X] T016 Implement ReleaseTransactionInput model in offchain/offchain/models.py with contract_address, beneficiary_address, beneficiary_index, milestone_identifier, signing_key_path fields
- [X] T017 Create docker-compose.yml in infra/ with cardano-node, ogmios, and kupo services
- [X] T018 Create config/ directory in infra/ with service configuration files for cardano-node, ogmios, kupo
- [X] T019 [P] Create validator_loader.py skeleton in offchain/offchain/validator_loader.py with function to load plutus.json

## Phase 3: User Story 1 - Administrator Initializes Off-Chain Environment (P1)

**Goal**: Enable administrators to set up the off-chain backend infrastructure to connect to local Cardano node and supporting services.

**Independent Test**: Run initialization command and verify that all required services (cardano-node, Ogmios, Kupo) are accessible and properly configured. This delivers the capability to establish a working connection to the blockchain.

**Dependencies**: Phase 1-2 must be complete.

**Acceptance Criteria**:
- System verifies connectivity to cardano-node, Ogmios, and Kupo services
- System reports which services are missing if unavailable
- System confirms successful connection when all services are available
- System supports both testnet and mainnet network configurations

### User Story 1 Tasks

- [X] T020 [US1] Implement OgmiosClient class skeleton in offchain/offchain/ogmios_client.py with async WebSocket connection handling
- [X] T021 [US1] Implement connectivity check method in offchain/offchain/ogmios_client.py to verify Ogmios service availability
- [X] T022 [US1] Implement KupoClient class skeleton in offchain/offchain/kupo_client.py with HTTP client initialization
- [X] T023 [US1] Implement connectivity check method in offchain/offchain/kupo_client.py to verify Kupo service availability
- [X] T024 [US1] Implement cardano-node connectivity check in offchain/offchain/config.py to verify node socket accessibility
- [X] T025 [US1] Implement init command in offchain/cli.py to call connectivity checks for all services
- [X] T026 [US1] Implement service status reporting in offchain/cli.py init command with JSON output format
- [X] T027 [US1] Implement error handling in offchain/cli.py init command to report missing services with guidance
- [X] T028 [US1] Create unit test for OgmiosClient connectivity in offchain/tests/unit/test_ogmios_client.py with mocked WebSocket
- [X] T029 [US1] Create unit test for KupoClient connectivity in offchain/tests/unit/test_kupo_client.py with mocked HTTP client
- [X] T030 [US1] Create integration test for init command in offchain/tests/integration/test_init.py with real services (if available)

## Phase 4: User Story 2 - Administrator Registers New Milestone Schedule (P1)

**Goal**: Enable administrators to create a new milestone-based token distribution schedule by defining beneficiary allocations, vesting timestamps, and milestone requirements.

**Independent Test**: Run milestone registration command with valid beneficiary data and verify that a properly structured datum is created. This delivers the capability to define token distribution schedules.

**Dependencies**: Phase 1-3 must be complete.

**Acceptance Criteria**:
- System creates valid distribution contract datum with all allocations recorded
- System validates beneficiary addresses and token amounts
- System rejects invalid inputs and reports specific validation errors
- System generates datum in correct format for transaction submission

### User Story 2 Tasks

- [X] T031 [US2] Implement MilestoneSchedule validation logic in offchain/offchain/milestone_manager.py to validate addresses, amounts, quorum threshold
- [X] T032 [US2] Implement datum generation logic in offchain/offchain/milestone_manager.py to convert MilestoneSchedule to on-chain datum format
- [X] T033 [US2] Implement contract address calculation in offchain/offchain/milestone_manager.py using validator hash from plutus.json
- [X] T034 [US2] Implement register-milestone command in offchain/cli.py to accept milestone schedule input from JSON file or CLI arguments
- [X] T035 [US2] Implement input validation in offchain/cli.py register-milestone command for beneficiary addresses, token amounts, milestone identifiers
- [X] T036 [US2] Implement datum output formatting in offchain/cli.py register-milestone command with JSON output
- [X] T037 [US2] Implement error handling in offchain/cli.py register-milestone command for validation failures
- [X] T038 [US2] Create unit test for MilestoneSchedule validation in offchain/tests/unit/test_milestone_manager.py with valid and invalid inputs
- [X] T039 [US2] Create unit test for datum generation in offchain/tests/unit/test_milestone_manager.py with sample milestone schedule
- [X] T040 [US2] Create integration test for register-milestone command in offchain/tests/integration/test_register_milestone.py with end-to-end flow

## Phase 5: User Story 3 - Administrator Commits Milestone Completion Data (P2)

**Goal**: Enable administrators to record milestone completion information including oracle verifications, enabling the system to track which milestones have been verified.

**Independent Test**: Commit milestone data for a specific milestone identifier and verify that the system stores and can retrieve this information. This delivers milestone state management capability.

**Dependencies**: Phase 1-4 must be complete.

**Acceptance Criteria**:
- System stores milestone completion data to local file system
- System marks milestone as verified when quorum threshold is met
- System updates existing milestone data with additional oracle signatures
- System validates oracle signature format (structure, types) but not cryptographic validity

### User Story 3 Tasks

- [ ] T041 [US3] Implement milestone data file storage logic in offchain/offchain/milestone_manager.py to save MilestoneCompletionData as JSON files
- [ ] T042 [US3] Implement milestone data file loading logic in offchain/offchain/milestone_manager.py to load existing milestone data from JSON files
- [ ] T043 [US3] Implement oracle signature format validation in offchain/offchain/milestone_manager.py to validate structure without cryptographic verification
- [ ] T044 [US3] Implement quorum status calculation in offchain/offchain/milestone_manager.py to update quorum_status based on signature count
- [ ] T045 [US3] Implement duplicate oracle signature detection in offchain/offchain/milestone_manager.py to prevent counting same oracle twice
- [ ] T046 [US3] Implement commit-milestone command in offchain/cli.py to accept milestone identifier and oracle signatures
- [ ] T047 [US3] Implement incremental signature addition in offchain/cli.py commit-milestone command to update existing milestone data
- [ ] T048 [US3] Implement error handling in offchain/cli.py commit-milestone command for invalid signature formats
- [ ] T049 [US3] Create unit test for milestone data storage in offchain/tests/unit/test_milestone_manager.py with file I/O operations
- [ ] T050 [US3] Create unit test for quorum calculation in offchain/tests/unit/test_milestone_manager.py with various signature counts
- [ ] T051 [US3] Create integration test for commit-milestone command in offchain/tests/integration/test_commit_milestone.py with end-to-end flow

## Phase 6: User Story 4 - User Checks Milestone Completion State (P2)

**Goal**: Enable users to query the system to determine whether a specific milestone has been verified and whether tokens are available for claim, by scanning on-chain UTxOs and datum states.

**Independent Test**: Query milestone state for a distribution contract and verify that the system correctly reports completion status based on on-chain data. This delivers status visibility capability.

**Dependencies**: Phase 1-5 must be complete (needs KupoClient and milestone data loading).

**Acceptance Criteria**:
- System checks local cache first and verifies/updates from on-chain UTxOs
- System returns current status of each milestone (verified/unverified)
- System reports quorum status and signature counts
- System handles missing contracts and corrupted local data gracefully

### User Story 4 Tasks

- [ ] T052 [US4] Implement UTxO query method in offchain/offchain/kupo_client.py to query contract UTxOs by address using /matches endpoint
- [ ] T053 [US4] Implement datum parsing logic in offchain/offchain/kupo_client.py to extract and parse contract datum from UTxO response
- [ ] T054 [US4] Implement contract state caching logic in offchain/offchain/milestone_manager.py to cache DistributionContractState locally
- [ ] T055 [US4] Implement cache validation logic in offchain/offchain/milestone_manager.py to check if cached data is stale and refresh from chain
- [ ] T056 [US4] Implement milestone status aggregation logic in offchain/offchain/milestone_manager.py to combine local milestone data with on-chain contract state
- [ ] T057 [US4] Implement check-status command in offchain/cli.py to accept contract address and optional milestone identifier
- [ ] T058 [US4] Implement hybrid query logic in offchain/cli.py check-status command to check local cache first, then verify from chain
- [ ] T059 [US4] Implement auto-recovery logic in offchain/cli.py check-status command to rebuild local cache from chain if corrupted
- [ ] T060 [US4] Create unit test for KupoClient UTxO query in offchain/tests/unit/test_kupo_client.py with mocked HTTP responses
- [ ] T061 [US4] Create unit test for milestone status aggregation in offchain/tests/unit/test_milestone_manager.py with sample data
- [ ] T062 [US4] Create integration test for check-status command in offchain/tests/integration/test_check_status.py with real Kupo queries (if available)

## Phase 7: User Story 5 - System Calculates Token Distribution Amounts (P2)

**Goal**: Enable the system to calculate how many tokens should be distributed to a beneficiary based on milestone completion status, vesting timestamps, and allocation rules.

**Independent Test**: Provide milestone and beneficiary data and verify that the system calculates the correct distribution amount based on business rules. This delivers calculation accuracy.

**Dependencies**: Phase 1-6 must be complete (needs milestone status checking and contract state).

**Acceptance Criteria**:
- System calculates claimable amount based on verified milestones and vesting timestamps
- System returns zero tokens if vesting timestamp has not passed
- System sums all claimable allocations correctly for multiple milestones
- System excludes already-claimed allocations from calculation

### User Story 5 Tasks

- [ ] T063 [US5] Implement distribution calculation logic in offchain/offchain/milestone_manager.py to calculate claimable tokens for a beneficiary
- [ ] T064 [US5] Implement vesting timestamp check in offchain/offchain/milestone_manager.py to verify vesting_timestamp <= current_time
- [ ] T065 [US5] Implement claimed allocation filtering in offchain/offchain/milestone_manager.py to exclude already-claimed allocations
- [ ] T066 [US5] Implement multi-milestone aggregation logic in offchain/offchain/milestone_manager.py to sum claimable amounts across all eligible milestones
- [ ] T067 [US5] Implement calculate-distribution command in offchain/cli.py to accept contract address and beneficiary address
- [ ] T068 [US5] Implement allocation breakdown output in offchain/cli.py calculate-distribution command showing per-milestone details
- [ ] T069 [US5] Implement error handling in offchain/cli.py calculate-distribution command for invalid addresses or missing contracts
- [ ] T070 [US5] Create unit test for distribution calculation in offchain/tests/unit/test_milestone_manager.py with various scenarios (vesting passed/not passed, verified/unverified)
- [ ] T071 [US5] Create unit test for multi-milestone aggregation in offchain/tests/unit/test_milestone_manager.py with multiple allocations
- [ ] T072 [US5] Create integration test for calculate-distribution command in offchain/tests/integration/test_calculate_distribution.py with end-to-end flow

## Phase 8: User Story 6 - Beneficiary Submits Token Release Transaction (P1)

**Goal**: Enable beneficiaries to initiate a transaction to claim their allocated tokens from a distribution contract, providing necessary milestone verification data and signing the transaction.

**Independent Test**: Submit a release transaction with valid beneficiary data and milestone verification, and verify that the transaction is successfully built, signed, and submitted to the blockchain. This delivers token claiming capability.

**Dependencies**: Phase 1-7 must be complete (needs all previous functionality for validation and transaction building).

**Acceptance Criteria**:
- System builds valid transaction with correct datum/redeemer, signs it, and submits to blockchain
- System validates beneficiary address and milestone identifier before submission
- System detects and prevents transaction submission when quorum requirements are not met
- System detects and prevents transaction submission when vesting timestamp has not passed
- System handles insufficient ADA for fees and collateral gracefully

### User Story 6 Tasks

- [ ] T073 [US6] Implement validator loading logic in offchain/offchain/validator_loader.py to parse plutus.json and extract compiled code and validator hash
- [ ] T074 [US6] Implement protocol parameters query in offchain/offchain/ogmios_client.py to query current protocol parameters via Ogmios
- [ ] T075 [US6] Implement transaction builder class in offchain/offchain/tx_builder.py using pycardano to construct release transactions
- [ ] T076 [US6] Implement script UTxO reference handling in offchain/offchain/tx_builder.py to reference contract UTxO from Kupo query
- [ ] T077 [US6] Implement datum/redeemer serialization in offchain/offchain/tx_builder.py to serialize milestone verification data as redeemer
- [ ] T078 [US6] Implement collateral calculation in offchain/offchain/tx_builder.py based on protocol parameters (typically 2-5 ADA)
- [ ] T079 [US6] Implement fee estimation in offchain/offchain/tx_builder.py using pycardano transaction building
- [ ] T080 [US6] Implement transaction signing logic in offchain/offchain/wallet.py to load signing key and sign transaction
- [ ] T081 [US6] Implement transaction submission logic in offchain/offchain/ogmios_client.py to submit transaction via Ogmios submitTransaction method
- [ ] T082 [US6] Implement pre-submission validation in offchain/offchain/milestone_manager.py to verify quorum, vesting, and claim eligibility before building transaction
- [ ] T083 [US6] Implement submit-release command in offchain/cli.py to accept contract address, beneficiary address, beneficiary index, milestone identifier, and signing key path
- [ ] T084 [US6] Implement transaction status reporting in offchain/cli.py submit-release command with transaction hash and fee estimate
- [ ] T085 [US6] Implement error handling in offchain/cli.py submit-release command for validation failures, insufficient funds, and submission errors
- [ ] T086 [US6] Create unit test for transaction building in offchain/tests/unit/test_tx_builder.py with mocked pycardano components
- [ ] T087 [US6] Create unit test for transaction signing in offchain/tests/unit/test_wallet.py with test signing keys
- [ ] T088 [US6] Create integration test for submit-release command in offchain/tests/integration/test_submit_release.py with end-to-end transaction flow (testnet)

## Phase 9: Polish & Cross-Cutting Concerns

**Goal**: Finalize error handling, documentation, testing coverage, and deployment preparation.

**Independent Test**: All CLI commands execute successfully, error messages are clear, documentation is complete, and testnet deployment completes without errors.

**Dependencies**: All previous phases should be complete.

### Polish Tasks

- [ ] T089 Add comprehensive error handling to all CLI commands with clear error messages for service unavailability and invalid inputs
- [ ] T090 Add input validation to all CLI commands for address format, amount ranges, timestamp validity
- [ ] T091 Add logging support throughout offchain/offchain/ modules for debugging and monitoring
- [ ] T092 Create comprehensive CLI help documentation with examples for each command
- [ ] T093 Add performance monitoring for transaction submission (<2 minutes) and query response (<10 seconds)
- [ ] T094 Create testnet deployment guide in docs/ with step-by-step instructions for infrastructure setup
- [ ] T095 Add auto-recovery tests for corrupted milestone data files in offchain/tests/integration/test_recovery.py
- [ ] T096 Add network disconnection handling tests in offchain/tests/integration/test_network_errors.py
- [ ] T097 Create mainnet migration checklist in docs/ with network configuration changes

## Parallel Execution Examples

### User Story 1 (Phase 3)
Tasks T028-T030 can be written in parallel as they test different components:
- T028: OgmiosClient connectivity test
- T029: KupoClient connectivity test
- T030: Init command integration test

### User Story 2 (Phase 4)
Tasks T038-T040 can be written in parallel:
- T038: MilestoneSchedule validation test
- T039: Datum generation test
- T040: Register-milestone integration test

### User Story 3 (Phase 5)
Tasks T041-T045 can be organized:
- T041-T042: File storage/loading (sequential)
- T043-T045: Validation and quorum logic (can be parallelized)
- T049-T051: Tests (can be written in parallel)

### User Story 4 (Phase 6)
Tasks T052-T062 can be parallelized:
- T052-T053: KupoClient methods (sequential)
- T054-T056: Caching and aggregation logic (sequential)
- T060-T062: Tests (can be written in parallel)

### User Story 6 (Phase 8)
Tasks T073-T088 can be organized:
- T073-T081: Core transaction building components (sequential dependencies)
- T082-T085: CLI command and validation (sequential)
- T086-T088: Tests (can be written in parallel)

## Testing Strategy

**Unit Tests**: Test individual modules (ogmios_client, kupo_client, milestone_manager, tx_builder, wallet) in isolation with mocked dependencies.

**Integration Tests**: Test full CLI command flows end-to-end, including real service connections when available.

**Contract Tests**: Test validator loading and datum/redeemer serialization against compiled Aiken validators.

**Performance Tests**: Verify transaction submission <2 minutes (SC-005), query response <10 seconds (SC-004), initialization <30 seconds (SC-001).

## Success Metrics

- ✅ All unit tests pass
- ✅ All integration tests pass
- ✅ CLI commands provide clear error messages for service issues (SC-009)
- ✅ System validates 100% of transaction inputs before building (SC-006)
- ✅ System detects quorum requirement failures before submission (SC-007)
- ✅ System detects vesting timestamp violations before submission (SC-008)
- ✅ Code organization separates business logic from network interface (SC-010)
- ✅ System reuses existing on-chain validator code without modification (SC-011)
- ✅ All success criteria from spec.md are met

## Notes

- Tasks marked with `[P]` can be executed in parallel
- Tasks marked with `[US1]`, `[US2]`, etc. belong to specific user story phases
- File paths are relative to project root
- Each task should be independently completable by an LLM with the provided context
- MVP scope focuses on delivering User Stories 1, 2, and 6 first for immediate administrative and claiming capability
- User Stories 3-5 provide enhanced functionality but can be implemented incrementally after MVP

