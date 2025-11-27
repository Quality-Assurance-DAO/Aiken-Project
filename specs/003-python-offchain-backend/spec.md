# Feature Specification: Python Off-Chain Backend MVP for Milestone Token Distribution

**Feature Branch**: `003-python-offchain-backend`  
**Created**: 2025-01-27  
**Status**: Draft  
**Input**: User description: "Using the existing Aiken-Project repository (on-chain validators in validators/, plus cardano-node/, scripts/, share/, specs/ infrastructure components), scaffold an MVP of the milestone-based token distribution system on Cardano with a full off-chain backend in Python — no external API like Blockfrost, but direct node access via a local cardano-node + Ogmios (WebSocket JSON-RPC) + Kupo (UTxO indexer). Organise the project so that new code lives in clearly separated folders: offchain/ for Python modules (e.g. ogmios_client.py, kupo_client.py, wallet.py, tx_builder.py, milestone_manager.py, config.py), infra/ for docker-compose or orchestration definitions for cardano-node, Ogmios, and Kupo, and leave contracts/ or keep validators/ for the existing Aiken smart contracts (optionally move compiled outputs to a contracts/compiled/ sub-folder). Add a CLI entry point (e.g. cli.py) using a Python CLI framework (e.g. typer or argparse) exposing commands for: initializing the environment, registering a new milestone-schedule (datum creation), committing/updating milestone data, checking milestone completion state (by scanning UTxOs via indexer), calculating token distribution amounts, and submitting a release transaction with appropriate datum/redeemer to release tokens to a beneficiary. In off-chain code, implement modules that (a) load compiled Aiken validator (from plutus.json or compiled artifact), (b) query UTxOs & datum states via Kupo, (c) query chain & protocol parameters via Ogmios, (d) build transactions via a library like pycardano, including script-UTxO, datum/redeemer, collateral, fees, signing, and (e) submit transactions back to the chain via Ogmios. Structure the milestone-distribution logic in a dedicated module — separate from "network / chain interface" and "contract loading / serialization" — so that business logic (milestones, token release rules, schedule, recipients) remains modular and testable. This MVP should reuse existing on-chain code and infrastructure configs to minimize duplication, while layering a clean, maintainable off-chain backend, suitable as a base for future web-app UI."

## Clarifications

### Session 2025-01-27

- Q: How should milestone completion data be persisted (in-memory, local file system, on-chain only, or hybrid)? → A: Local file system (JSON files or SQLite database)
- Q: Should the Python backend cryptographically validate oracle signatures or only validate format? → A: Format validation only (on-chain validator performs cryptographic verification)
- Q: Where should local milestone completion data files be stored? → A: Configurable directory (default: project data subdirectory)
- Q: Should milestone completion state queries use local storage, on-chain data, or both? → A: Hybrid (check local cache first, verify/update from chain if needed)
- Q: How should the system handle corrupted or unreadable local milestone data files? → A: Auto-recover from chain (with warning message)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Administrator Initializes Off-Chain Environment (Priority: P1)

An administrator sets up the off-chain backend infrastructure to connect to a local Cardano node and supporting services, enabling the system to interact with the blockchain without external API dependencies.

**Why this priority**: Without proper initialization, no other operations can function. This establishes the foundation for all subsequent interactions with the blockchain.

**Independent Test**: Can be fully tested by running the initialization command and verifying that all required services (cardano-node, Ogmios, Kupo) are accessible and properly configured. This delivers the capability to establish a working connection to the blockchain.

**Acceptance Scenarios**:

1. **Given** an administrator wants to set up the off-chain backend, **When** they run the initialization command, **Then** the system verifies connectivity to cardano-node, Ogmios, and Kupo services and confirms successful connection
2. **Given** the initialization command is run, **When** one or more required services are unavailable, **Then** the system reports which services are missing and provides guidance on how to start them
3. **Given** the initialization command completes successfully, **When** the administrator attempts to use other CLI commands, **Then** those commands can successfully connect to the blockchain services
4. **Given** the system is initialized for a specific network (testnet/mainnet), **When** the administrator queries chain information, **Then** the system returns data for the correct network

---

### User Story 2 - Administrator Registers New Milestone Schedule (Priority: P1)

An administrator creates a new milestone-based token distribution schedule by defining beneficiary allocations, vesting timestamps, and milestone requirements, which results in a distribution contract datum ready for on-chain deployment.

**Why this priority**: This is the core administrative function that enables token distributions. Without the ability to create milestone schedules, the system cannot distribute tokens.

**Independent Test**: Can be fully tested by running the milestone registration command with valid beneficiary data and verifying that a properly structured datum is created. This delivers the capability to define token distribution schedules.

**Acceptance Scenarios**:

1. **Given** an administrator wants to create a milestone schedule for 5 beneficiaries, **When** they provide beneficiary addresses, token amounts, milestone identifiers, and vesting timestamps, **Then** the system creates a valid distribution contract datum with all allocations recorded
2. **Given** an administrator attempts to create a milestone schedule, **When** they provide invalid beneficiary addresses or negative token amounts, **Then** the system rejects the input and reports specific validation errors
3. **Given** a milestone schedule is created, **When** the administrator views the generated datum, **Then** they can see all beneficiary allocations, total token amounts, and contract metadata
4. **Given** a milestone schedule is created, **When** the administrator wants to deploy it on-chain, **Then** the datum is in the correct format for transaction submission

---

### User Story 3 - Administrator Commits Milestone Completion Data (Priority: P2)

An administrator records milestone completion information including oracle verifications, enabling the system to track which milestones have been verified and are ready for token release.

**Why this priority**: Milestone completion tracking is essential for determining when beneficiaries can claim tokens. This enables the system to enforce milestone verification requirements.

**Independent Test**: Can be fully tested by committing milestone data for a specific milestone identifier and verifying that the system stores and can retrieve this information. This delivers milestone state management capability.

**Acceptance Scenarios**:

1. **Given** an administrator wants to record that milestone "milestone-001" is complete, **When** they provide milestone identifier and oracle verification signatures, **Then** the system stores the milestone completion data to local file system and marks it as verified
2. **Given** milestone completion data exists for a milestone, **When** the administrator updates it with additional oracle signatures, **Then** the system updates the locally stored data file with the new information
3. **Given** milestone completion data is stored locally, **When** the administrator queries the milestone state, **Then** the system returns the current verification status and oracle signature count from local storage
4. **Given** an administrator attempts to commit milestone data, **When** they provide an invalid milestone identifier or malformed oracle signatures (invalid format/structure), **Then** the system rejects the input and reports validation errors (format validation only; cryptographic verification happens on-chain)

---

### User Story 4 - User Checks Milestone Completion State (Priority: P2)

A user (administrator or beneficiary) queries the system to determine whether a specific milestone has been verified and whether tokens are available for claim, by scanning on-chain UTxOs and datum states.

**Why this priority**: Users need visibility into milestone status to know when they can claim tokens. This provides transparency and enables informed decision-making.

**Independent Test**: Can be fully tested by querying milestone state for a distribution contract and verifying that the system correctly reports completion status based on on-chain data. This delivers status visibility capability.

**Acceptance Scenarios**:

1. **Given** a distribution contract exists on-chain with milestone allocations, **When** a user queries milestone completion state, **Then** the system checks local cache first and verifies/updates from on-chain UTxOs, returning the current status of each milestone (verified/unverified)
2. **Given** a milestone has been verified by sufficient oracles, **When** a user checks the milestone state, **Then** the system reports that the milestone is complete and tokens are claimable (using local cache if available, verifying against chain)
3. **Given** a milestone has not yet met quorum requirements, **When** a user checks the milestone state, **Then** the system reports how many oracle signatures are present and how many are required (from local cache or chain query)
4. **Given** a user queries milestone state, **When** the distribution contract UTxO cannot be found on-chain, **Then** the system reports that the contract address is invalid or the contract has not been deployed
5. **Given** local milestone data exists but may be stale, **When** a user queries milestone state, **Then** the system verifies local data against on-chain state and updates local cache if discrepancies are found

---

### User Story 5 - System Calculates Token Distribution Amounts (Priority: P2)

The system calculates how many tokens should be distributed to a beneficiary based on milestone completion status, vesting timestamps, and allocation rules, ensuring accurate distribution calculations.

**Why this priority**: Accurate calculation is essential for ensuring beneficiaries receive correct token amounts. This prevents over-distribution and ensures compliance with allocation rules.

**Independent Test**: Can be fully tested by providing milestone and beneficiary data and verifying that the system calculates the correct distribution amount based on business rules. This delivers calculation accuracy.

**Acceptance Scenarios**:

1. **Given** a beneficiary has an allocation of 1000 tokens for a verified milestone, **When** the system calculates distribution amount, **Then** it returns 1000 tokens as the claimable amount
2. **Given** a beneficiary's milestone is verified but vesting timestamp has not passed, **When** the system calculates distribution amount, **Then** it returns zero tokens (not yet claimable)
3. **Given** a beneficiary has multiple milestone allocations, **When** the system calculates total distribution amount, **Then** it sums all claimable allocations correctly
4. **Given** a beneficiary has already claimed some allocations, **When** the system calculates remaining distribution amount, **Then** it excludes already-claimed allocations from the calculation

---

### User Story 6 - Beneficiary Submits Token Release Transaction (Priority: P1)

A beneficiary initiates a transaction to claim their allocated tokens from a distribution contract, providing necessary milestone verification data and signing the transaction.

**Why this priority**: This is the end-user value proposition - enabling beneficiaries to receive their tokens. Without this capability, the entire system has no practical value.

**Independent Test**: Can be fully tested by submitting a release transaction with valid beneficiary data and milestone verification, and verifying that the transaction is successfully built, signed, and submitted to the blockchain. This delivers token claiming capability.

**Acceptance Scenarios**:

1. **Given** a beneficiary wants to claim tokens for a verified milestone, **When** they submit a release transaction with their address and milestone verification data, **Then** the system builds a valid transaction with correct datum/redeemer, signs it, and submits it to the blockchain
2. **Given** a beneficiary submits a release transaction, **When** the transaction includes incorrect beneficiary address or milestone identifier, **Then** the system validates the input and rejects the transaction before submission
3. **Given** a beneficiary submits a release transaction, **When** the milestone verification does not meet quorum requirements, **Then** the system detects this and prevents transaction submission
4. **Given** a release transaction is submitted, **When** the transaction is successfully included in a block, **Then** the system can verify the transaction status and confirm token transfer
5. **Given** a beneficiary submits a release transaction, **When** their wallet has insufficient ADA for transaction fees, **Then** the system detects this and reports the fee requirement before attempting submission

---

### Edge Cases

- What happens when the local cardano-node is not running or unreachable? → System reports connection error and provides guidance on starting the node
- How does the system handle network disconnections during transaction submission? → System detects disconnection, reports error, and allows retry without duplicating transactions
- What happens when Kupo indexer is out of sync with the blockchain? → System reports sync status and warns if data may be stale
- How does the system handle invalid or corrupted compiled validator files? → System validates validator file format and reports errors if validator cannot be loaded
- What happens when a transaction submission fails due to insufficient collateral? → System calculates required collateral, detects insufficiency, and reports error before submission
- How does the system handle concurrent milestone state queries? → System processes queries independently without blocking
- What happens when milestone data is queried for a non-existent contract address? → System reports that no contract UTxO was found at the address
- How does the system handle protocol parameter queries when Ogmios is unavailable? → System reports service unavailability and cannot proceed with transaction building
- What happens when transaction building fails due to execution budget limits? → System reports budget calculation and identifies which operations exceed limits
- How does the system handle wallet signing when the signing key is missing or invalid? → System validates key file existence and format before attempting to sign
- What happens when local milestone data files are corrupted or unreadable? → System automatically recovers by querying on-chain state, rebuilding local cache, and displays warning message to user

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a CLI command to initialize the off-chain environment and verify connectivity to cardano-node, Ogmios, and Kupo services
- **FR-002**: System MUST provide a CLI command to register a new milestone schedule that creates a distribution contract datum with beneficiary allocations
- **FR-003**: System MUST validate milestone schedule inputs including beneficiary addresses, token amounts, milestone identifiers, and vesting timestamps before creating datum
- **FR-004**: System MUST provide a CLI command to commit or update milestone completion data including oracle verification signatures
- **FR-025**: System MUST persist milestone completion data to local file system (JSON files or SQLite database) to enable efficient querying and incremental updates
- **FR-027**: System MUST store milestone completion data in a configurable directory, with default location in a project data subdirectory (e.g., `offchain/data/` or `data/`)
- **FR-028**: System MUST automatically recover from corrupted or unreadable local milestone data files by querying on-chain state and rebuilding local cache, with warning message to user
- **FR-005**: System MUST provide a CLI command to check milestone completion state using hybrid approach (check local cache first, verify/update from on-chain UTxOs and datum states if needed)
- **FR-006**: System MUST query UTxOs from Kupo indexer to determine current contract state
- **FR-007**: System MUST query chain and protocol parameters from Ogmios to support transaction building
- **FR-008**: System MUST provide a CLI command to calculate token distribution amounts based on milestone status, vesting timestamps, and allocation rules
- **FR-009**: System MUST provide a CLI command to submit release transactions that builds, signs, and submits transactions to the blockchain
- **FR-010**: System MUST load compiled Aiken validator from plutus.json or compiled artifact files
- **FR-011**: System MUST build transactions including script UTxO references, datum, redeemer, collateral, and fee calculations
- **FR-012**: System MUST sign transactions using provided wallet signing keys
- **FR-013**: System MUST submit transactions to the blockchain via Ogmios
- **FR-014**: System MUST separate milestone distribution business logic from network/chain interface code
- **FR-015**: System MUST separate contract loading and serialization logic from business logic
- **FR-016**: System MUST validate transaction inputs (beneficiary address, milestone identifier, token amounts) before building transactions
- **FR-017**: System MUST detect and report when milestone verification does not meet quorum requirements
- **FR-026**: System MUST validate oracle signature format (structure, field presence, data types) but MUST NOT perform cryptographic signature verification (on-chain validator handles cryptographic validation)
- **FR-018**: System MUST detect and report when vesting timestamps have not been met
- **FR-019**: System MUST handle transaction fee calculations and detect insufficient wallet balances
- **FR-020**: System MUST verify transaction submission status and report success or failure
- **FR-021**: System MUST organize code into separate modules for different concerns (network clients, wallet management, transaction building, milestone logic, configuration)
- **FR-022**: System MUST reuse existing on-chain validator code and infrastructure configurations
- **FR-023**: System MUST support both testnet and mainnet network configurations
- **FR-024**: System MUST provide clear error messages when services are unavailable or inputs are invalid

### Key Entities *(include if feature involves data)*

- **Milestone Schedule**: A data structure defining token distribution parameters including beneficiary allocations, vesting timestamps, milestone identifiers, and contract metadata. Used to create distribution contract datums.

- **Milestone Completion Data**: Information recording that a milestone has been verified, including milestone identifier, oracle signatures, verification timestamp, and quorum status. Stored locally in configurable directory (default: project data subdirectory) as JSON files or SQLite database to enable efficient querying and incremental updates. Oracle signatures are validated for format/structure off-chain; cryptographic verification occurs on-chain via the validator. Used to determine when tokens become claimable.

- **Distribution Contract State**: Current on-chain state of a distribution contract including UTxO information, datum content, claimed allocations, and remaining token balances. Retrieved by querying the blockchain via Kupo.

- **Release Transaction**: A blockchain transaction that claims tokens from a distribution contract, including script UTxO reference, beneficiary address, milestone verification data, datum, redeemer, and transaction metadata.

- **Network Configuration**: Settings that define which Cardano network to connect to (testnet/mainnet), service endpoints (Ogmios, Kupo, cardano-node), and network-specific parameters.

- **Data Storage Configuration**: Settings that define where milestone completion data and other local files are stored, including configurable data directory path (defaults to project data subdirectory).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Administrators can successfully initialize the off-chain environment and establish connectivity to all required services (cardano-node, Ogmios, Kupo) within 30 seconds when services are running
- **SC-002**: Administrators can create milestone schedules for up to 50 beneficiaries in a single operation, with datum generation completing within 5 seconds
- **SC-003**: System correctly calculates token distribution amounts with 100% accuracy based on milestone verification status and vesting timestamps
- **SC-004**: System successfully queries milestone completion status using hybrid approach (local cache + on-chain verification) and returns current status within 10 seconds of the query request
- **SC-005**: Beneficiaries can submit release transactions that are successfully built, signed, and submitted to the blockchain within 2 minutes of initiating the command when all conditions are met
- **SC-006**: System validates 100% of transaction inputs (addresses, amounts, milestone identifiers) before building transactions, preventing invalid submissions
- **SC-007**: System detects and reports quorum requirement failures before transaction submission in 100% of cases where quorum is not met
- **SC-008**: System detects and reports vesting timestamp violations before transaction submission in 100% of cases where vesting has not passed
- **SC-009**: System provides clear error messages for service connectivity issues, enabling administrators to diagnose and resolve problems within 5 minutes
- **SC-010**: Code organization separates business logic from network interface code, enabling independent testing of milestone distribution rules without requiring blockchain connectivity
- **SC-011**: System reuses existing on-chain validator code without modification, maintaining compatibility with existing smart contracts
- **SC-012**: CLI commands provide consistent interface and error handling, enabling users to complete operations without manual transaction building or low-level blockchain interaction

## Assumptions

- Local cardano-node, Ogmios, and Kupo services are available and can be started/configured by administrators
- Administrators have access to wallet signing keys for transaction signing
- Compiled Aiken validator artifacts (plutus.json or equivalent) are available in the project
- Existing on-chain validator code follows standard Cardano datum/redeemer patterns
- Network infrastructure (cardano-node, Ogmios, Kupo) can be orchestrated via docker-compose or similar tools
- Python environment supports required libraries for Cardano transaction building and WebSocket communication
- Administrators understand basic Cardano concepts (UTxOs, datums, redeemers, transaction fees)
- Beneficiaries have Cardano-compatible wallets and can provide signing keys for claim transactions
- Milestone verification data (oracle signatures) is available from external sources when committing milestone completion
- The system operates in a development/testnet environment initially, with mainnet support as a future consideration

## Dependencies

- Existing Aiken-Project repository with on-chain validators in validators/ directory
- Existing cardano-node infrastructure and configuration files
- Local cardano-node instance (running or configurable)
- Ogmios service (WebSocket JSON-RPC interface to cardano-node)
- Kupo service (UTxO indexer for querying on-chain state)
- Python runtime environment (3.8 or later)
- Python libraries for Cardano transaction building (e.g., pycardano)
- Python libraries for WebSocket communication
- Python CLI framework (typer or argparse)
- Docker or similar orchestration tool for infrastructure services (if using docker-compose)
- Compiled Aiken validator artifacts (plutus.json or equivalent format)

## Out of Scope

- Web application user interface (this MVP provides CLI foundation for future UI)
- External API integrations (Blockfrost, etc.) - system uses direct node access only
- Real-time monitoring dashboards or web interfaces
- Automated milestone detection or project progress tracking
- Oracle signature generation (assumed to come from external oracle services)
- Wallet management beyond transaction signing (key generation, key storage security)
- Multi-signature wallet support
- Transaction fee optimization or advanced fee strategies
- Support for multiple Cardano networks simultaneously (one network per instance)
- Advanced transaction building features beyond basic script interactions (complex DeFi integrations)
- Performance optimization for high-volume transaction processing
- Integration with external notification systems or alerting

