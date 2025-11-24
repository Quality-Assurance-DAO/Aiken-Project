# Feature Specification: Milestone-Based Token Distribution System

**Feature Branch**: `001-milestone-token-distribution`  
**Created**: 2025-01-27  
**Status**: Draft  
**Input**: User description: "Develop a milestone-based token distribution system on Cardano testnet using Aiken, building on the QA‑DAO Token Distribution Framework (https://github.com/Quality-Assurance-DAO/Token-Distribution-Framework ) which structures treasury funding and token allocations across multiple stakeholder groups based on governance-approved milestones and quality-assurance metrics. First, implement the validator, datum, and redeemer in Aiken to handle multi-recipient allocations, oracle-based milestone verification, and quorum enforcement. Simulate oracle signatures locally using test keys and include them in the datum to test quorum logic. Mint test tokens on the testnet and create off-chain scripts or CLI commands to submit claim transactions for each beneficiary, enforcing timestamp/vesting constraints and correct token amounts. Iteratively test multi-recipient claims, double claims, invalid signatures, quorum failures, and timestamp enforcement. Monitor testnet transactions to verify outputs and refine contract logic. Once testing is complete, prepare for mainnet deployment by replacing simulated oracle signatures with real oracle nodes and test tokens with production token policy IDs, ensuring the off-chain scripts handle real ADA fees and token transfers."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Beneficiary Claims Tokens After Milestone Verification (Priority: P1)

A beneficiary receives notification that a milestone has been verified and their allocated tokens are available for claim. They submit a claim transaction to receive their tokens from the distribution contract.

**Why this priority**: This is the core value proposition - enabling beneficiaries to receive their allocated tokens. Without this, the entire system has no purpose. This story delivers immediate value to end users.

**Independent Test**: Can be fully tested by creating a distribution contract with a single beneficiary allocation, verifying a milestone with oracle signatures, and successfully claiming tokens. This delivers the fundamental capability of token distribution.

**Acceptance Scenarios**:

1. **Given** a distribution contract contains tokens allocated to a beneficiary for a verified milestone, **When** the beneficiary submits a valid claim transaction with correct beneficiary address and milestone identifier, **Then** the beneficiary receives their allocated token amount minus transaction fees
2. **Given** a distribution contract contains tokens for multiple beneficiaries, **When** beneficiary A claims their allocation, **Then** beneficiary A receives their tokens and the contract still contains tokens for other beneficiaries
3. **Given** a beneficiary attempts to claim tokens before the vesting timestamp, **When** they submit a claim transaction, **Then** the transaction is rejected and no tokens are transferred
4. **Given** a beneficiary has already claimed their allocation for a milestone, **When** they attempt to claim again for the same milestone, **Then** the transaction is rejected to prevent double-claiming

---

### User Story 2 - Oracle Quorum Verifies Milestone Completion (Priority: P2)

A set of authorized oracles observe project progress and independently verify milestone completion. When a sufficient quorum of oracles signs off on a milestone, the milestone becomes claimable by beneficiaries.

**Why this priority**: Oracle verification ensures that tokens are only distributed when milestones are genuinely completed, protecting the treasury from fraudulent claims. This is essential for system security and trust.

**Independent Test**: Can be fully tested by simulating multiple oracle signatures, verifying quorum logic accepts valid quorums and rejects insufficient signatures, and confirming milestone state transitions. This delivers the security mechanism that prevents unauthorized token distribution.

**Acceptance Scenarios**:

1. **Given** a milestone requires verification from at least 3 of 5 authorized oracles, **When** exactly 3 valid oracle signatures are provided, **Then** the milestone is marked as verified and tokens become claimable
2. **Given** a milestone requires verification from at least 3 of 5 authorized oracles, **When** only 2 valid oracle signatures are provided, **Then** the milestone remains unverified and tokens are not claimable
3. **Given** a milestone verification includes signatures from unauthorized addresses, **When** the quorum check is performed, **Then** unauthorized signatures are ignored and only valid oracle signatures count toward quorum
4. **Given** a milestone verification includes duplicate signatures from the same oracle, **When** the quorum check is performed, **Then** duplicate signatures are counted only once toward quorum

---

### User Story 3 - Treasury Administrator Sets Up Multi-Recipient Distribution (Priority: P3)

A treasury administrator creates a new distribution contract that allocates tokens to multiple beneficiaries across different stakeholder categories (projects, participants, auditors) with different vesting schedules and milestone requirements.

**Why this priority**: This enables the system to handle complex real-world scenarios where multiple parties need allocations. While single-recipient distributions work, multi-recipient support is essential for practical treasury management.

**Independent Test**: Can be fully tested by creating a distribution contract with allocations for multiple beneficiaries, each with different token amounts, vesting timestamps, and milestone identifiers. This delivers the capability to manage complex distribution scenarios.

**Acceptance Scenarios**:

1. **Given** a treasury administrator wants to distribute tokens to 10 beneficiaries, **When** they create a distribution contract with all 10 allocations, **Then** the contract is created with the correct total token amount and all beneficiary addresses are recorded
2. **Given** a distribution contract contains allocations for beneficiaries A, B, and C, **When** beneficiary A claims their allocation, **Then** the contract updates to reflect A's claim while preserving allocations for B and C
3. **Given** a distribution contract has allocations with different vesting timestamps, **When** beneficiary A's vesting time arrives but beneficiary B's has not, **Then** only beneficiary A can claim while beneficiary B's claim is rejected

---

### User Story 4 - System Enforces Vesting and Timestamp Constraints (Priority: P4)

The system prevents beneficiaries from claiming tokens before their vesting period begins and ensures claims occur within valid time windows based on milestone completion dates.

**Why this priority**: Vesting enforcement protects the treasury by ensuring tokens are only released according to schedule. This prevents premature claims and ensures alignment with project timelines.

**Independent Test**: Can be fully tested by creating allocations with specific vesting timestamps and verifying that claims before the timestamp are rejected while claims after are accepted. This delivers time-based access control.

**Acceptance Scenarios**:

1. **Given** a beneficiary's allocation has a vesting timestamp of January 1st, **When** they attempt to claim on December 31st, **Then** the transaction is rejected
2. **Given** a beneficiary's allocation has a vesting timestamp of January 1st, **When** they attempt to claim on January 1st or later, **Then** the transaction is accepted and tokens are transferred
3. **Given** a milestone has an expiration timestamp after which claims are no longer valid, **When** a beneficiary attempts to claim after expiration, **Then** the transaction is rejected

---

### Edge Cases

- What happens when a beneficiary's address is invalid or unspendable?
- How does the system handle claims when the contract has insufficient tokens (due to previous claims or errors)?
- What happens if oracle signatures are provided but the milestone identifier doesn't match any allocation?
- How does the system handle simultaneous claims from multiple beneficiaries for the same milestone?
- What happens when a claim transaction includes incorrect token amounts (more or less than allocated)?
- How does the system handle claims when the required quorum threshold changes after contract creation?
- What happens if a beneficiary's allocation amount is zero or negative?
- How does the system handle vesting timestamps that are in the past at contract creation time?
- What happens when transaction fees exceed the allocated token amount?
- How does the system handle partial claims if supported, or enforce all-or-nothing claims?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow beneficiaries to claim their allocated tokens after milestone verification and vesting timestamp requirements are met
- **FR-002**: System MUST verify that milestone completion is attested by a sufficient quorum of authorized oracle signatures before allowing claims
- **FR-003**: System MUST support multiple beneficiary allocations within a single distribution contract
- **FR-004**: System MUST enforce vesting timestamps to prevent claims before the specified time
- **FR-005**: System MUST prevent double-claiming by tracking which beneficiaries have already claimed for each milestone
- **FR-006**: System MUST validate that claim transactions include the correct beneficiary address matching the allocation
- **FR-007**: System MUST validate that claim transactions include the correct token amount matching the allocation
- **FR-008**: System MUST validate that claim transactions include the correct milestone identifier
- **FR-009**: System MUST ignore unauthorized oracle signatures when calculating quorum
- **FR-010**: System MUST count duplicate signatures from the same oracle only once toward quorum
- **FR-011**: System MUST reject claims when the required quorum threshold is not met
- **FR-012**: System MUST handle testnet deployment with simulated oracle signatures for testing purposes
- **FR-013**: System MUST support off-chain scripts or CLI commands to construct and submit claim transactions
- **FR-014**: System MUST validate that transactions include sufficient ADA for fees
- **FR-015**: System MUST support monitoring and verification of testnet transactions for testing purposes
- **FR-016**: System MUST be designed to transition from testnet simulated oracles to mainnet real oracle nodes
- **FR-017**: System MUST support replacing test token policy IDs with production token policy IDs for mainnet deployment
- **FR-018**: System MUST handle token transfers including both native tokens and ADA
- **FR-019**: System MUST preserve allocations for unclaimed beneficiaries when one beneficiary claims their portion
- **FR-020**: System MUST validate that milestone verification data matches the milestone identifier in the allocation

### Key Entities *(include if feature involves data)*

- **Distribution Contract**: A smart contract that holds tokens allocated to multiple beneficiaries, enforces milestone verification, and manages vesting schedules. Contains total token amount, beneficiary allocations, oracle addresses, quorum threshold, and contract metadata.

- **Beneficiary Allocation**: Represents a single beneficiary's entitlement to tokens. Contains beneficiary address, token amount, milestone identifier, vesting timestamp, and claim status.

- **Milestone Verification**: Evidence that a milestone has been completed, consisting of milestone identifier, oracle signatures, and verification timestamp. Must meet quorum threshold to be considered valid.

- **Oracle Signature**: Cryptographic proof from an authorized oracle that a milestone has been completed. Contains oracle address, signature data, and timestamp. Used collectively to meet quorum requirements.

- **Claim Transaction**: A transaction submitted by a beneficiary to receive their allocated tokens. Contains beneficiary address, milestone identifier, token amount, and references the distribution contract.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Beneficiaries can successfully claim their allocated tokens within 5 minutes of submitting a valid claim transaction when all conditions are met (milestone verified, vesting passed, quorum satisfied)
- **SC-002**: System rejects 100% of claim attempts that do not meet quorum requirements (insufficient or invalid oracle signatures)
- **SC-003**: System rejects 100% of claim attempts made before vesting timestamps
- **SC-004**: System prevents 100% of double-claim attempts (same beneficiary, same milestone)
- **SC-005**: System successfully processes multi-recipient distributions supporting at least 50 simultaneous beneficiary allocations in a single contract
- **SC-006**: System validates claim transactions with 100% accuracy for beneficiary address, token amount, and milestone identifier matching
- **SC-007**: Testnet deployment enables complete testing of all claim scenarios (valid claims, double claims, invalid signatures, quorum failures, timestamp enforcement) with simulated oracles
- **SC-008**: System can transition from testnet to mainnet deployment by replacing oracle infrastructure and token policy IDs without requiring contract logic changes
- **SC-009**: Off-chain scripts or CLI commands enable users to construct and submit claim transactions without manual transaction building
- **SC-010**: System handles transaction fee calculations correctly, ensuring beneficiaries receive their full allocated amount minus fees in 100% of successful claims

## Assumptions

- Oracle addresses and quorum thresholds are set at contract creation time and remain constant for the contract lifetime
- Vesting timestamps are absolute timestamps (not relative durations) set at contract creation
- Each beneficiary allocation is associated with exactly one milestone identifier
- Token amounts are specified in the smallest unit of the token (e.g., lovelace for ADA)
- Testnet testing uses simulated oracle signatures generated from test keys for development purposes
- Mainnet deployment will use real oracle nodes that provide cryptographic signatures through established oracle infrastructure
- Transaction fees are paid in ADA (native currency) and deducted from the transaction, not from allocated token amounts
- The system assumes beneficiaries have Cardano-compatible wallets capable of submitting transactions
- Milestone identifiers are unique strings or numbers that unambiguously identify specific project milestones
- The quorum threshold is expressed as "at least N of M oracles" where N and M are integers set at contract creation

## Dependencies

- Cardano testnet access for initial deployment and testing
- Aiken development environment and toolchain for smart contract development
- Test token minting capability on Cardano testnet
- Oracle signature generation tools for testnet simulation (test keys)
- Off-chain transaction building libraries or CLI tools compatible with Cardano
- Cardano node access for monitoring and verifying testnet transactions
- Mainnet oracle infrastructure (for post-testnet deployment phase)
- Production token policy IDs (for mainnet deployment phase)

## Out of Scope

- Automatic milestone detection or project progress tracking (oracles handle this externally)
- Token price discovery or market mechanisms
- Governance voting mechanisms for approving distributions (assumed to happen before contract creation)
- Multi-currency support beyond Cardano native tokens and ADA
- Dynamic quorum threshold changes after contract creation
- Partial token claims (system enforces all-or-nothing per allocation)
- Accelerated vesting or early release mechanisms
- Penalty mechanisms or clawbacks for missed milestones
- Integration with external DeFi protocols or AMM pools
- Real-time monitoring dashboards or user interfaces (focus is on smart contract and CLI tools)
