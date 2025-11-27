# Implementation Plan: Python Off-Chain Backend MVP for Milestone Token Distribution

**Branch**: `003-python-offchain-backend` | **Date**: 2025-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-python-offchain-backend/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build an MVP Python off-chain backend for milestone-based token distribution on Cardano. The system provides CLI commands for initializing the environment, registering milestone schedules, committing milestone completion data, checking milestone status, calculating token distributions, and submitting release transactions. The backend uses direct node access via local cardano-node + Ogmios (WebSocket JSON-RPC) + Kupo (UTxO indexer), avoiding external APIs. Code is organized into separate modules for network clients (ogmios_client.py, kupo_client.py), wallet management (wallet.py), transaction building (tx_builder.py), milestone business logic (milestone_manager.py), and configuration (config.py). Infrastructure orchestration (docker-compose) lives in infra/, while compiled Aiken validators are loaded from existing artifacts. The system separates business logic from network interfaces and contract serialization for testability.

## Technical Context

**Language/Version**: Python 3.8+ (spec requirement: Python 3.8 or later)  
**Primary Dependencies**: pycardano 0.9.0+ (Cardano transaction building), typer 0.9.0+ (CLI framework), websockets 11.0+ (WebSocket client for Ogmios), httpx 0.25.0+ (HTTP client for Kupo), pydantic 2.0+ (data validation), pytest with pytest-asyncio (testing)  
**Storage**: Local file system (JSON files) for milestone completion data, configurable directory (default: `offchain/data/`), SQLite migration option available if needed  
**Testing**: pytest with pytest-asyncio plugin for async tests, unittest.mock for mocking WebSocket/HTTP clients  
**Target Platform**: Linux/macOS (local development), Docker containers for infrastructure services (cardano-node, Ogmios, Kupo)  
**Project Type**: Single project (CLI application with modular backend)  
**Performance Goals**: Transaction submission <2 minutes (SC-005), query response <10 seconds (SC-004), initialization <30 seconds (SC-001), memory <500MB typical usage  
**Constraints**: Must work with local cardano-node (no external APIs), must support both testnet and mainnet, must handle network disconnections gracefully, transaction size ~16KB limit, execution budget queried from protocol parameters, collateral 2-5 ADA typical  
**Scale/Scope**: MVP scope: up to 50 beneficiaries per milestone schedule (SC-002), CLI-only interface (no web UI), single network per instance, interactive CLI usage (not batch processing)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Note**: Constitution file appears to be a template. Proceeding with standard development practices:
- Code organization: Separate modules for different concerns (network, wallet, transactions, business logic)
- Testing: Unit tests for business logic, integration tests for blockchain interactions
- Error handling: Clear error messages for service unavailability and invalid inputs
- Documentation: CLI commands documented, code organized for maintainability

**Gates**:
- ✅ Code separation: Business logic separated from network/chain interface (FR-014, FR-015)
- ✅ Testability: Business logic testable without blockchain connectivity (SC-010)
- ✅ Error handling: Clear error messages for service issues (FR-024)
- ⚠️ NEEDS CLARIFICATION: Specific constitution rules if they exist beyond template

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
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
offchain/
├── offchain/
│   ├── ogmios_client.py      # WebSocket JSON-RPC client for Ogmios
│   ├── kupo_client.py        # HTTP client for Kupo UTxO indexer
│   ├── wallet.py             # Wallet management and signing
│   ├── tx_builder.py         # Transaction building with pycardano
│   ├── milestone_manager.py  # Business logic for milestone distribution
│   ├── config.py             # Configuration management
│   └── validator_loader.py   # Load compiled Aiken validators
├── cli.py                     # CLI entry point (typer/argparse)
├── data/                      # Local milestone completion data (configurable)
└── tests/
    ├── unit/
    │   ├── test_milestone_manager.py
    │   └── test_config.py
    ├── integration/
    │   ├── test_ogmios_client.py
    │   ├── test_kupo_client.py
    │   └── test_tx_builder.py
    └── contract/
        └── test_validator_loading.py

infra/
├── docker-compose.yml         # Orchestration for cardano-node, Ogmios, Kupo
└── config/                    # Service configuration files

contracts/
└── compiled/                  # Compiled Aiken validator artifacts (optional move from validators/)
```

**Structure Decision**: Single project structure with clear separation:
- `offchain/` contains all Python modules and CLI entry point
- `infra/` contains infrastructure orchestration (docker-compose)
- `contracts/compiled/` optionally houses compiled validator artifacts
- Existing `validators/` directory remains for Aiken source code
- Tests organized by type (unit, integration, contract) within `offchain/tests/`

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
