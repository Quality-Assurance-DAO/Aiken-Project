# Research: Python Off-Chain Backend MVP

**Date**: 2025-01-27  
**Feature**: 003-python-offchain-backend

## Purpose

This document consolidates research findings to resolve all "NEEDS CLARIFICATION" items identified in the Technical Context section of plan.md.

## Research Areas

### 1. Python Cardano Transaction Building Library

**Decision**: Use `pycardano` (Python Cardano library) version 0.9.0 or later for transaction building, signing, and serialization.

**Rationale**: 
- pycardano is the most mature Python library for Cardano transaction building
- Supports Plutus V3 scripts (required for Aiken validators)
- Provides high-level APIs for UTxO handling, transaction building, datum/redeemer serialization
- Active development and community support
- Compatible with Python 3.8+
- Supports both testnet and mainnet

**Alternatives Considered**:
- **cardano-cli wrapped in subprocess**: Rejected - less programmatic control, harder to test, requires CLI installation
- **meson**: Considered but less mature than pycardano, fewer examples
- **cardano-serialization-lib bindings**: Rejected - too low-level, requires more boilerplate

**Implementation Note**: 
- Install via pip: `pip install pycardano`
- Use pycardano's `TransactionBuilder` for constructing transactions
- Use `PlutusV3Script` for loading compiled Aiken validators
- Handle CBOR serialization for datums/redeemers using pycardano's built-in support

---

### 2. Python CLI Framework

**Decision**: Use `typer` (version 0.9.0+) for CLI interface implementation.

**Rationale**:
- Modern Python CLI framework built on Click
- Type hints support for better IDE integration and validation
- Automatic help generation
- Subcommand support (perfect for multiple CLI commands)
- Async support if needed for WebSocket operations
- Clean, readable code structure

**Alternatives Considered**:
- **argparse**: Rejected - more verbose, less modern, no type hints
- **click**: Considered - typer is built on click but provides better developer experience
- **fire**: Rejected - less structured, harder to organize multiple commands

**Implementation Note**:
- Structure: `cli.py` as entry point with typer app
- Commands: `init`, `register-milestone`, `commit-milestone`, `check-status`, `calculate-distribution`, `submit-release`
- Use typer's `Option` and `Argument` for parameters
- Output: JSON for machine-readable, formatted text for human-readable

---

### 3. WebSocket Client for Ogmios

**Decision**: Use `websockets` library (version 11.0+) for async WebSocket communication with Ogmios.

**Rationale**:
- Standard Python WebSocket library with async support
- Well-documented and stable
- Compatible with asyncio for concurrent operations
- Supports JSON-RPC protocol used by Ogmios
- Handles reconnection logic

**Alternatives Considered**:
- **aiohttp**: Considered - includes WebSocket support but heavier dependency
- **websocket-client**: Rejected - synchronous, less suitable for async operations
- **socketio**: Rejected - overkill for JSON-RPC, adds unnecessary complexity

**Implementation Note**:
- Implement `ogmios_client.py` with async WebSocket connection
- Handle JSON-RPC request/response pattern
- Implement reconnection logic for network failures
- Query methods: `queryLedgerState`, `queryProtocolParameters`, `submitTransaction`
- Use asyncio for concurrent queries if needed

---

### 4. HTTP Client for Kupo

**Decision**: Use `httpx` (version 0.25.0+) for HTTP requests to Kupo API.

**Rationale**:
- Modern async HTTP client (can use sync API too)
- Better than `requests` for async operations
- Supports both sync and async patterns
- Good error handling and timeout support
- Type hints support

**Alternatives Considered**:
- **requests**: Considered - simpler but synchronous only, less modern
- **aiohttp**: Considered - good async support but httpx is more modern and easier to use
- **urllib**: Rejected - too low-level, more boilerplate

**Implementation Note**:
- Implement `kupo_client.py` with HTTP client
- Endpoints: `/matches/*` for UTxO queries, `/checkpoints` for sync status
- Handle pagination for large result sets
- Parse JSON responses into Python dataclasses
- Implement caching for frequently accessed UTxOs

---

### 5. Data Validation Library

**Decision**: Use `pydantic` (version 2.0+) for data validation and serialization.

**Rationale**:
- Industry standard for Python data validation
- Type hints integration
- JSON schema generation (useful for API contracts)
- Validation error messages
- Serialization/deserialization support

**Alternatives Considered**:
- **dataclasses**: Rejected - no validation, requires manual validation code
- **marshmallow**: Considered - good but pydantic is more modern and type-hint friendly
- **attrs**: Considered - good but pydantic has better JSON support

**Implementation Note**:
- Define Pydantic models for: MilestoneSchedule, MilestoneCompletionData, DistributionContractState
- Use for CLI input validation
- Generate JSON schemas for API contracts
- Validate data before transaction building

---

### 6. Compiled Aiken Validator Format

**Decision**: Load validators from `plutus.json` format (Aiken's standard output format).

**Rationale**:
- `plutus.json` is Aiken's standard compilation output
- Contains compiled code, datum/redeemer schemas, validator hash
- JSON format is easy to parse in Python
- Already exists in project root (`plutus.json`)
- Contains all necessary information for transaction building

**Alternatives Considered**:
- **.plutus files**: Considered - binary format, harder to parse, less metadata
- **CBOR files**: Rejected - binary format, requires additional parsing
- **Manual compilation**: Rejected - error-prone, not maintainable

**Implementation Note**:
- Implement `validator_loader.py` to parse `plutus.json`
- Extract `compiledCode` (hex string) for script bytes
- Extract datum/redeemer schemas for validation
- Extract validator hash for address calculation
- Support loading from `contracts/compiled/` if validators are moved there

---

### 7. Local Storage for Milestone Completion Data

**Decision**: Use JSON files stored in configurable directory (default: `offchain/data/`) with option to migrate to SQLite if needed.

**Rationale**:
- JSON files are simple, human-readable, easy to debug
- No database setup required for MVP
- Easy to backup and version control
- Can migrate to SQLite later if query performance becomes an issue
- Meets requirement for "JSON files or SQLite database"

**Alternatives Considered**:
- **SQLite from start**: Considered - better for complex queries but adds complexity for MVP
- **In-memory only**: Rejected - doesn't meet persistence requirement
- **PostgreSQL**: Rejected - overkill for MVP, requires external service

**Implementation Note**:
- File structure: `offchain/data/milestones/{milestone_id}.json`
- Schema: `{milestone_id, oracle_signatures, verification_timestamp, quorum_status}`
- Implement file locking for concurrent access
- Auto-recovery: if file corrupted, query chain and rebuild
- Consider SQLite migration if file count exceeds 1000 or query performance degrades

---

### 8. Testing Strategy for WebSocket/Async Code

**Decision**: Use `pytest` with `pytest-asyncio` plugin for async tests, `unittest.mock` for mocking WebSocket/HTTP clients.

**Rationale**:
- pytest is Python standard for testing
- pytest-asyncio enables async test functions
- unittest.mock provides mocking capabilities
- Can mock WebSocket/HTTP responses without real services
- Supports fixtures for test setup/teardown

**Alternatives Considered**:
- **unittest**: Considered - standard library but less feature-rich than pytest
- **nose2**: Rejected - less maintained than pytest
- **hypothesis**: Considered - good for property-based testing but not primary framework

**Implementation Note**:
- Unit tests: Mock Ogmios/Kupo clients, test business logic in isolation
- Integration tests: Use test fixtures for real Ogmios/Kupo connections (if available)
- Contract tests: Test validator loading and serialization
- Use pytest fixtures for common test data (validator artifacts, test addresses)

---

### 9. Performance Goals and Constraints

**Decision**: 
- Transaction submission: <2 minutes end-to-end (matches SC-005)
- Query response: <10 seconds for milestone status (matches SC-004)
- Initialization: <30 seconds (matches SC-001)
- Memory: <500MB for typical operations
- CPU: Efficient enough for CLI usage (not a server)

**Rationale**:
- Performance goals align with success criteria from spec
- MVP scope doesn't require high-throughput server performance
- CLI usage patterns are interactive, not batch processing
- Memory constraint prevents excessive caching

**Alternatives Considered**:
- **Higher performance targets**: Rejected - premature optimization for MVP
- **Lower targets**: Considered - but spec already defines acceptable limits

**Implementation Note**:
- Use async operations for concurrent queries
- Implement caching for protocol parameters (change infrequently)
- Batch UTxO queries when possible
- Monitor performance during integration testing

---

### 10. Transaction Size and Execution Budget Constraints

**Decision**: 
- Transaction size limit: ~16KB (Cardano standard)
- Execution budget: Query from Ogmios, validate before submission
- Collateral: Calculate based on protocol parameters (typically 2-5 ADA)

**Rationale**:
- Cardano network enforces these limits
- Must query current protocol parameters (they change over time)
- Collateral requirements vary by network and transaction complexity
- Validator already designed for efficiency (from previous research)

**Alternatives Considered**:
- **Fixed limits**: Rejected - protocol parameters change, must query dynamically
- **Ignore limits**: Rejected - transactions will fail if limits exceeded

**Implementation Note**:
- Query protocol parameters from Ogmios before transaction building
- Calculate transaction size during building
- Estimate execution units (if possible) or rely on validator efficiency
- Calculate required collateral based on protocol parameters
- Validate all constraints before transaction submission

---

### 11. Docker Compose Infrastructure Setup

**Decision**: Use docker-compose.yml in `infra/` directory to orchestrate cardano-node, Ogmios, and Kupo services.

**Rationale**:
- Standard tool for multi-container orchestration
- Easy to start/stop all services together
- Can use existing cardano-node configurations
- Supports network configuration (testnet/mainnet)
- Matches requirement for "docker-compose or orchestration definitions"

**Alternatives Considered**:
- **Kubernetes**: Rejected - overkill for local development
- **Manual service management**: Rejected - error-prone, harder to reproduce
- **docker-compose**: Accepted - standard, simple, meets requirements

**Implementation Note**:
- Services: cardano-node, ogmios, kupo
- Network: bridge network for service communication
- Volumes: cardano-node database, Kupo database
- Environment: Network selection (testnet/mainnet)
- Health checks: Verify services are ready before CLI operations

---

## Summary of Resolved Clarifications

1. ✅ **Python Libraries**: pycardano 0.9.0+, typer 0.9.0+, websockets 11.0+, httpx 0.25.0+, pydantic 2.0+
2. ✅ **CLI Framework**: typer for modern, type-safe CLI interface
3. ✅ **WebSocket Client**: websockets library for async Ogmios communication
4. ✅ **HTTP Client**: httpx for Kupo API requests
5. ✅ **Data Validation**: pydantic for models and validation
6. ✅ **Validator Loading**: Parse plutus.json format (already exists in project)
7. ✅ **Local Storage**: JSON files in configurable directory (default: offchain/data/)
8. ✅ **Testing**: pytest with pytest-asyncio for async tests, unittest.mock for mocking
9. ✅ **Performance**: Align with success criteria (<2min transactions, <10s queries, <30s init)
10. ✅ **Constraints**: Query protocol parameters dynamically, validate transaction limits
11. ✅ **Infrastructure**: docker-compose.yml for service orchestration

## Remaining Implementation Decisions

These will be made during implementation:
- Specific version pinning in requirements.txt (use latest stable versions)
- Error message formats and user-facing messages
- Logging strategy (structured logging vs simple print statements)
- Configuration file format (YAML, TOML, or environment variables)
- CLI output formatting (table, JSON, plain text options)

## References

- pycardano Documentation: https://pycardano.readthedocs.io
- typer Documentation: https://typer.tiangolo.com
- Ogmios Documentation: https://ogmios.dev
- Kupo Documentation: https://cardanosolutions.github.io/kupo
- Aiken Language: https://aiken-lang.org
- Cardano Developer Portal: https://developers.cardano.org


