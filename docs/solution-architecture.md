# Solution Architecture

**Navigation**: [Home](../README.md) > [Documentation](./README.md) > Solution Architecture

This document describes the project's architecture, module boundaries, and dependencies. It explains how components interact and how data flows through the system.

## Overview

This project implements a milestone-based token distribution system on Cardano. The system allows tokens to be distributed to beneficiaries based on milestone completion, validated by an oracle quorum.

## Architecture Layers

### 1. Smart Contract Layer (On-Chain)

**Location**: `src/contract/`, `src/validator/`

**Components**:
- **Validators**: On-chain validation logic that checks milestone completion and claim eligibility
- **Contract Logic**: Core business rules for token distribution, vesting, and claim validation
- **State Management**: Datum structures for storing allocations, claims, and milestone state

**Responsibilities**:
- Validate token claim transactions
- Enforce vesting schedules
- Verify oracle quorum signatures
- Maintain contract state in UTXOs

**Dependencies**: 
- Plutus V2 runtime
- Cardano blockchain

### 2. CLI Layer (Off-Chain)

**Location**: `src/cli/`

**Components**:
- **Create Command**: Initialize new distribution contracts
- **Claim Command**: Submit token claim transactions
- **Query Command**: Query contract state and allocations
- **Utils**: Shared utilities for transaction building and data handling

**Responsibilities**:
- Build Cardano transactions
- Interact with Cardano CLI
- Format contract data (datums, redeemers)
- Provide user-friendly CLI interface

**Dependencies**:
- Cardano CLI tools
- Aiken runtime (for CLI commands)
- Contract layer (for business logic)

### 3. Deployment Layer

**Location**: `scripts/`

**Components**:
- **deploy.sh**: Contract deployment script
- **mint_test_tokens.sh**: Test token minting
- **simulate_oracles.sh**: Oracle simulation for testing

**Responsibilities**:
- Deploy contracts to Cardano networks
- Set up test environments
- Manage deployment configurations

**Dependencies**:
- Cardano CLI
- Cardano Node (for local development)
- Contract compilation outputs

### 4. Test Layer

**Location**: `tests/`

**Components**:
- **Unit Tests**: Test individual contract functions and validators
- **Integration Tests**: Test end-to-end contract interactions
- **Validator Tests**: Test validator logic with various scenarios

**Responsibilities**:
- Verify contract correctness
- Test edge cases and error conditions
- Validate business logic
- Ensure execution budget compliance

**Dependencies**:
- Aiken test framework
- Contract layer
- Test data (`test-data/`)

## Module Boundaries

### Contract Module (`src/contract/`)

**Purpose**: Core business logic for token distribution

**Exports**:
- Distribution contract logic
- Allocation management
- Claim validation rules
- Vesting calculations

**Dependencies**: None (pure business logic)

**Used By**: Validator layer, CLI layer, tests

### Validator Module (`src/validator/`)

**Purpose**: On-chain validation scripts

**Exports**:
- Validator scripts
- Validation logic
- State transition rules

**Dependencies**: Contract module

**Used By**: Cardano blockchain (on-chain execution)

### CLI Module (`src/cli/`)

**Purpose**: Command-line interface for contract interactions

**Exports**:
- CLI commands (create, claim, query)
- Transaction building utilities
- Data formatting functions

**Dependencies**: Contract module, Cardano CLI

**Used By**: End users, deployment scripts

### Library Module (`src/lib/`)

**Purpose**: Shared utilities and helpers

**Exports**:
- Common data types
- Utility functions
- Shared constants

**Dependencies**: None

**Used By**: All other modules

## Data Flow

### Contract Deployment Flow

```
1. User prepares allocation data (test-data/allocations.json)
2. CLI create command builds contract datum
3. Deployment script (scripts/deploy.sh) uses Cardano CLI to:
   - Build deployment transaction
   - Sign transaction
   - Submit to network
4. Contract UTXO created on blockchain with validator script
```

### Token Claim Flow

```
1. Beneficiary initiates claim via CLI claim command
2. CLI builds transaction with:
   - Contract UTXO as input
   - Redeemer specifying claim action
   - Oracle signatures (if milestone validation required)
3. Validator executes on-chain:
   - Validates milestone completion (via oracle quorum)
   - Checks vesting timestamp
   - Verifies claim eligibility
   - Updates contract state (datum)
4. Transaction submitted to network
5. If valid, tokens transferred to beneficiary
```

### Query Flow

```
1. User runs CLI query command
2. CLI uses Cardano CLI to query contract UTXO
3. Datum extracted from UTXO
4. Contract state parsed and displayed
5. Allocation and claim status shown to user
```

## Configuration Flow

### Development Configuration

1. **Aiken Configuration** (`aiken.toml`):
   - Project metadata
   - Compiler settings
   - Dependency management

2. **Test Data** (`test-data/`):
   - Allocation configurations
   - Oracle addresses
   - Test scenarios

3. **Cardano Network Configuration**:
   - Testnet/mainnet settings
   - Node connection details
   - Network parameters

### Deployment Configuration

1. **Network Selection**: Testnet (development) or Mainnet (production)
2. **Contract Parameters**: Oracle addresses, quorum threshold, vesting schedules
3. **Key Management**: Signing keys for contract deployment
4. **Node Configuration**: Cardano Node settings for transaction submission

## Dependencies

### External Dependencies

- **Cardano Node**: Blockchain infrastructure (vendored in `cardano-node/`)
- **Cardano CLI**: Transaction building tools
- **Aiken Compiler**: Smart contract compilation
- **Plutus V2**: Smart contract runtime
- **BLS Library**: Cryptographic operations (vendored in `src/blst/`)

### Internal Dependencies

```
CLI Layer
  └── Contract Layer
        └── Library Layer

Validator Layer
  └── Contract Layer
        └── Library Layer

Deployment Scripts
  └── CLI Layer
        └── Contract Layer

Tests
  └── All Layers
```

## Module Interaction Patterns

### Contract → Validator

- Validator imports contract logic
- Validator uses contract functions for validation
- Contract provides pure business logic functions

### CLI → Contract

- CLI imports contract types and functions
- CLI uses contract logic to build transactions
- CLI formats contract data for Cardano transactions

### Tests → All Modules

- Tests import and exercise all modules
- Unit tests focus on individual modules
- Integration tests test module interactions

## State Management

### On-Chain State

- **Contract UTXO**: Contains validator script and current state datum
- **Datum Structure**: Stores allocations, claims, milestone state
- **State Updates**: New UTXO created with updated datum on each transaction

### Off-Chain State

- **Test Data**: Allocation and oracle configurations
- **Build Artifacts**: Compiled contracts and scripts
- **Deployment Records**: Contract addresses and deployment metadata

## Security Considerations

### On-Chain Security

- Validator enforces all business rules
- Oracle quorum prevents single point of failure
- Vesting timestamps prevent premature claims
- Execution budget limits prevent resource exhaustion

### Off-Chain Security

- Key management for transaction signing
- Oracle key security (quorum threshold)
- Network configuration validation
- Transaction validation before submission

## Performance Considerations

### Execution Budget

- Validators designed to operate within Cardano limits
- Efficient datum structures to minimize transaction size
- Optimized validation logic for CPU/memory usage

### Transaction Size

- Datums structured to fit within transaction limits (~16KB)
- Efficient encoding of allocation and claim data
- Minimal redeemer data requirements

## Extension Points

### Adding New Features

1. **New Validator Logic**: Extend `src/validator/` with new validation rules
2. **New CLI Commands**: Add commands to `src/cli/`
3. **New Contract Functions**: Extend `src/contract/` with new business logic
4. **New Test Scenarios**: Add tests to `tests/`

### Integration Points

- **Oracle Integration**: Oracle quorum system can be extended
- **Token Standards**: Can integrate with CIP token standards
- **Governance**: Can integrate with Cardano governance features

## Related Documentation

- [Cardano Ecosystem Overview](./cardano-ecosystem-overview.md) - Cardano components and integration
- [Repository Inventory](./repository-inventory.md) - Complete component catalog
- [Glossary](./glossary.md) - Technical term definitions
- [Testing Guide](./testing-guide.md) - Test execution and validation

