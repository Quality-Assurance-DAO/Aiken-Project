# Cardano Ecosystem Overview

**Navigation**: [Home](../README.md) > [Documentation](./README.md) > Cardano Ecosystem Overview

This document provides context about the Cardano ecosystem and explains how this project integrates with Cardano components. It is designed to help new contributors understand Cardano terminology and the project's role in the Cardano ecosystem.

## Cardano Overview

Cardano is a blockchain platform that uses a proof-of-stake consensus mechanism and an extended UTXO (eUTXO) model for transaction processing. Cardano supports smart contracts through the Plutus platform, enabling developers to build decentralized applications (dApps) on Cardano.

### Protocol Eras

Cardano has evolved through multiple protocol eras, each introducing new capabilities:

- **Byron**: Initial Cardano launch with basic transaction capabilities
- **Shelley**: Introduction of staking and decentralization
- **Goguen**: Smart contract capabilities via Plutus
- **Babbage**: Performance improvements and new features
- **Conway**: Current era with governance features (this project targets Conway)

**This project targets the Conway era** to leverage the latest Cardano capabilities and ensure future compatibility.

### Networks

Cardano operates multiple networks:

- **Mainnet**: Production network with real ADA and assets
- **Testnet**: Test network using test tokens (tADA) for development and testing

This project provides deployment guides for both testnet (for development) and mainnet (for production).

## Cardano Components Used by This Project

### Cardano Node

**Component Type**: Network Infrastructure  
**Protocol Era**: Conway  
**Project Usage**: The project vendors the Cardano Node repository (`cardano-node/`) for local development and testing. The node provides blockchain synchronization and state management.

**Dependencies**: 
- Requires network connectivity to Cardano peers
- Uses configuration files for testnet/mainnet

**Standards References**: 
- Cardano Node follows Cardano protocol specifications
- Configuration follows Cardano network standards

**Configuration Requirements**:
- Network configuration files (config.json, topology.json)
- Genesis files for testnet/mainnet
- Socket path for CLI communication

**Project Integration**: The node is used locally for development and testing. Production deployments may use remote nodes or infrastructure providers.

### Cardano CLI

**Component Type**: Development Tool  
**Protocol Era**: Conway  
**Project Usage**: The project uses Cardano CLI (`cardano-cli`) for:
- Building transactions for contract deployment
- Querying blockchain state (UTXOs, transaction status)
- Managing keys and addresses
- Submitting transactions to the network

**Dependencies**:
- Requires connection to Cardano Node (local or remote)
- Uses network configuration (testnet/mainnet)

**Standards References**:
- Cardano CLI follows Cardano transaction format standards
- Transaction building follows Cardano protocol specifications

**Configuration Requirements**:
- Socket path to Cardano Node
- Network flag (`--testnet-magic` or `--mainnet`)
- Key files for signing transactions

**Project Integration**: 
- Deployment scripts (`scripts/deploy.sh`) use Cardano CLI
- Test data validation uses CLI address validation
- See [Cardano CLI Setup](./cardano-cli-setup.md) for installation and configuration

### Aiken Compiler

**Component Type**: Development Tool  
**Protocol Era**: Conway (Plutus V2)  
**Project Usage**: The project uses Aiken to:
- Write smart contract code in Aiken language (`src/contract/`, `src/validator/`)
- Compile contracts to Plutus V2 scripts
- Run tests using Aiken test framework (`tests/`)
- Generate CLI commands (`src/cli/`)

**Dependencies**:
- Compiles to Plutus V2 scripts
- Uses Aiken standard library

**Standards References**:
- Aiken follows Plutus V2 standards
- Compiles to Cardano-native script format

**Configuration Requirements**:
- `aiken.toml` for project configuration
- `aiken.lock` for dependency locking
- Aiken compiler installed locally

**Project Integration**:
- All smart contract source code is in Aiken (`src/`)
- Build process compiles to Plutus scripts
- Test suites use Aiken test framework
- See [Glossary](./glossary.md#aiken) for more details

### Plutus V2

**Component Type**: Smart Contract Platform  
**Protocol Era**: Conway  
**Project Usage**: The project compiles Aiken code to Plutus V2 scripts that run on Cardano. Plutus V2 provides:
- On-chain validation logic (validators)
- Improved performance compared to Plutus V1
- Enhanced features for complex smart contracts

**Dependencies**:
- Runs on Cardano blockchain
- Uses Cardano's eUTXO model

**Standards References**:
- Plutus V2 follows Cardano script standards
- Validators must comply with execution budget limits

**Configuration Requirements**:
- `plutus.json` for script configuration
- Execution budget considerations (CPU/memory limits)

**Project Integration**:
- Validators compile to Plutus V2 scripts
- Contracts use Plutus V2 features (datums, redeemers)
- See [Glossary](./glossary.md#plutus-v2) for more details

## Project Architecture in Cardano Context

### Smart Contracts

This project implements a milestone-based token distribution system as Cardano smart contracts:

1. **Contract Validator** (`src/validator/`): On-chain logic that validates token claims based on milestone completion
2. **Contract Logic** (`src/contract/`): Core business logic for distribution rules
3. **CLI Commands** (`src/cli/`): Off-chain code for building transactions and interacting with contracts

### Transaction Flow

1. **Deployment**: Contract is deployed to Cardano using Cardano CLI, creating a UTXO with contract validator
2. **State Management**: Contract state (allocations, claims) is stored in UTXO datums
3. **Claim Processing**: Beneficiaries submit transactions with redeemers to claim tokens when milestones are validated
4. **Oracle Validation**: Oracle quorum validates milestone completion before tokens are released

### Data Model

- **UTXOs**: Each contract instance is a UTXO with validator script
- **Datums**: Store allocation data, claim records, and milestone state
- **Redeemers**: Specify claim actions and milestone identifiers
- **Transactions**: Built using Cardano CLI, signed, and submitted to network

## Standards and Specifications

### CIP Standards

This project may reference Cardano Improvement Proposals (CIPs) for standards compliance:

- **CIP-68**: NFT metadata standard (if applicable)
- Other CIPs as relevant to token distribution

**External Reference**: [CIP Repository](https://github.com/cardano-foundation/CIPs)

### Plutus Standards

- **Plutus V2**: All contracts compile to Plutus V2 scripts
- **Execution Budget**: Contracts designed to operate within Cardano execution limits
- **Transaction Size**: Contracts optimized for Cardano transaction size limits (~16KB)

## Network Configuration

### Testnet

- **Purpose**: Development and testing
- **Magic Number**: 1097911063 (Preprod testnet)
- **Configuration**: See [Cardano CLI Setup](./cardano-cli-setup.md)
- **Usage**: All development and initial testing

### Mainnet

- **Purpose**: Production deployment
- **Network**: Cardano mainnet
- **Configuration**: See [Mainnet Migration](./mainnet-migration.md)
- **Usage**: Production token distribution

## Integration Points

### Deployment Scripts

- `scripts/deploy.sh`: Uses Cardano CLI to deploy contracts
- `scripts/mint_test_tokens.sh`: Mints test tokens using Cardano CLI
- `scripts/simulate_oracles.sh`: Simulates oracle interactions

### Test Data

- `test-data/allocations.json`: Allocation data for contract deployment
- `test-data/oracles.json`: Oracle addresses for milestone validation

### Build Process

1. Aiken compiles source code to Plutus V2 scripts
2. Build artifacts stored in `build/` directory
3. Compiled scripts ready for deployment via Cardano CLI

## Getting Started

For new contributors:

1. **Understand Cardano Basics**: Review [Glossary](./glossary.md) for Cardano terminology
2. **Set Up Development Environment**: Follow [Cardano CLI Setup](./cardano-cli-setup.md)
3. **Deploy to Testnet**: Follow [Testnet Deployment](./testnet-deployment.md)
4. **Understand Project Structure**: See [Solution Architecture](./solution-architecture.md)

## External Resources

- [Cardano Documentation](https://docs.cardano.org/)
- [Aiken Documentation](https://aiken-lang.org/)
- [Plutus Documentation](https://plutus.readthedocs.io/)
- [Cardano Node Repository](https://github.com/intersectmbo/cardano-node)
- [CIP Repository](https://github.com/cardano-foundation/CIPs)

## Related Documentation

- [Glossary](./glossary.md) - Definitions of Cardano and project-specific terms
- [Solution Architecture](./solution-architecture.md) - Project structure and module boundaries
- [Repository Inventory](./repository-inventory.md) - Complete catalog of project components
- [Cardano CLI Setup](./cardano-cli-setup.md) - Installation and configuration guide

