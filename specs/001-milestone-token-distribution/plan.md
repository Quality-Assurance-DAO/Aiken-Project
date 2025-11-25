# Implementation Plan: Milestone-Based Token Distribution System

**Branch**: `001-milestone-token-distribution` | **Date**: 2025-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-milestone-token-distribution/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Develop a milestone-based token distribution system on Cardano testnet using Aiken smart contracts. The system enables multi-recipient token allocations with oracle-based milestone verification, quorum enforcement, and vesting timestamp constraints. Implementation includes on-chain validator logic (datum/redeemer patterns), off-chain CLI tools for transaction construction, and testnet deployment with simulated oracle signatures for testing.

**Technical Approach**: 
- On-chain validator enforces quorum-based milestone verification, vesting timestamps, and prevents double-claiming
- Hybrid oracle verification: off-chain signature verification, on-chain quorum validation
- Datum structure supports 50+ beneficiary allocations per contract
- CLI tools wrap Cardano CLI for contract creation and claim transactions
- Configuration-based design enables testnet-to-mainnet migration without code changes

## Technical Context

**Language/Version**: Aiken (latest stable)  
**Primary Dependencies**: Aiken standard library, Cardano CLI tools (with option for cardano-cli-js/lucid libraries for advanced features)  
**Storage**: On-chain (Cardano UTXO model via datum), Off-chain transaction metadata  
**Testing**: Aiken test framework, Cardano testnet for integration testing  
**Target Platform**: Cardano blockchain (testnet → mainnet)  
**Project Type**: single  
**Performance Goals**: Transaction validation completes within Cardano block time limits (<5 seconds), support 50+ simultaneous beneficiary allocations per contract  
**Constraints**: Cardano UTXO model limitations, transaction size limits (~16KB), script execution budget (<10M CPU units, <10M memory units), must handle concurrent claim attempts  
**Scale/Scope**: Single distribution contract supporting 50+ beneficiaries, multiple milestone verifications, testnet → mainnet deployment path

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Status**: PASSED (Pre-Phase 0) ✅  
**Status**: PASSED (Post-Phase 1) ✅

**Pre-Phase 0 Notes**: Constitution file is currently a template without specific principles defined. No explicit violations detected. Project follows standard Aiken/Cardano development patterns.

**Post-Phase 1 Re-evaluation**: 
- ✅ Single project structure confirmed (smart contract + CLI tools)
- ✅ Test-first approach maintained via Aiken test framework
- ✅ Standard Cardano transaction patterns used
- ✅ No unnecessary complexity introduced in design phase
- ✅ Data model is efficient and follows Cardano best practices
- ✅ CLI interface is straightforward and follows standard patterns
- ✅ Research resolved all technical unknowns without adding complexity
- ✅ Design supports requirements without over-engineering

**Conclusion**: Design phase maintains simplicity and follows established patterns. Ready to proceed to implementation.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── validator/
│   ├── lib.aiken          # Main validator logic
│   ├── datum.aiken        # Datum type definitions
│   ├── redeemer.aiken     # Redeemer type definitions
│   └── oracle.aiken       # Oracle signature verification logic
├── cli/
│   ├── claim.aiken        # Claim transaction builder
│   ├── create.aiken       # Contract creation helper
│   └── utils.aiken        # Shared CLI utilities
└── lib/
    ├── types.aiken        # Shared type definitions
    └── validation.aiken  # Validation helpers

tests/
├── validator/
│   ├── validator_test.aiken
│   ├── datum_test.aiken
│   └── oracle_test.aiken
├── integration/
│   ├── multi_recipient_test.aiken
│   ├── quorum_test.aiken
│   └── vesting_test.aiken
└── unit/
    └── validation_test.aiken

scripts/
├── deploy.sh              # Testnet deployment script
├── mint_test_tokens.sh    # Test token minting
└── simulate_oracles.sh    # Oracle signature simulation
```

**Structure Decision**: Single project structure following Aiken conventions. Validator code separated from CLI tools. Tests organized by type (validator, integration, unit). Scripts directory for deployment and testing automation.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
