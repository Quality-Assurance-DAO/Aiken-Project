# Repository Inventory

**Navigation**: [Home](../README.md) > [Documentation](./README.md) > Repository Inventory

This document provides a comprehensive inventory of all top-level directories and files in the repository, their purpose, lifecycle status, and relationships to Cardano components.

## Inventory Table

| Name | Type | Purpose | Status | Cardano Dependency | Docs |
|------|------|---------|--------|-------------------|------|
| `.cursor` | directory | Cursor IDE configuration | active | None | - |
| `.git` | directory | Git repository metadata | active | None | - |
| `.specify` | directory | Specification tooling configuration | active | None | - |
| `build/` | directory | Aiken build artifacts and compiled packages | active | Aiken compiler | - |
| `cardano-node/` | directory | Vendored Cardano Node repository (external dependency) | external | Cardano Node | [cardano-node/README.rst](../cardano-node/README.rst) |
| `docs/` | directory | Project documentation | active | None | [docs/README.md](./README.md) |
| `scripts/` | directory | Deployment and utility scripts | active | Cardano CLI | - |
| `specs/` | directory | Feature specifications and design documents | active | None | - |
| `src/` | directory | Aiken smart contract source code | active | Aiken compiler | - |
| `test-data/` | directory | Test data files (allocations, oracles) | active | Cardano CLI | - |
| `tests/` | directory | Test suites (unit, integration, validator) | active | Aiken test framework | - |
| `validators/` | directory | Validator examples | active | Aiken compiler | - |
| `aiken.lock` | file | Aiken dependency lock file | active | Aiken compiler | - |
| `aiken.toml` | file | Aiken project configuration | active | Aiken compiler | - |
| `plutus.json` | file | Plutus script configuration | active | Plutus | - |
| `README.md` | file | Project root documentation | active | None | [README.md](../README.md) |

## Detailed Descriptions

### Directories

#### `.cursor/`
- **Purpose**: Cursor IDE workspace configuration and settings
- **Lifecycle**: Active - maintained for development environment
- **Cardano Dependency**: None
- **Modification Policy**: Developer-specific, not versioned

#### `.git/`
- **Purpose**: Git repository metadata and configuration
- **Lifecycle**: Active - standard Git directory
- **Cardano Dependency**: None
- **Modification Policy**: Managed by Git

#### `.specify/`
- **Purpose**: Specification tooling configuration for feature planning
- **Lifecycle**: Active - used for feature specification workflow
- **Cardano Dependency**: None
- **Modification Policy**: Updated as specification workflow evolves

#### `build/`
- **Purpose**: Aiken build artifacts, compiled packages, and lock files
- **Lifecycle**: Active - regenerated on each build
- **Cardano Dependency**: Aiken compiler
- **Modification Policy**: Auto-generated, should be git-ignored
- **Notes**: Contains `aiken-compile.lock` and compiled package artifacts

#### `cardano-node/`
- **Purpose**: Vendored Cardano Node repository (external dependency)
- **Lifecycle**: External - externally maintained, not modified by this project
- **Cardano Dependency**: Cardano Node (full dependency)
- **Modification Policy**: DO NOT MODIFY - external dependency
- **Source**: https://github.com/intersectmbo/cardano-node
- **Notes**: Contains full Cardano node implementation, CLI tools, and related components. This is a vendored dependency for local development and testing.

#### `docs/`
- **Purpose**: Project documentation organized by category
- **Lifecycle**: Active - actively maintained and expanded
- **Cardano Dependency**: None (documentation only)
- **Modification Policy**: Updated as documentation evolves
- **Contents**:
  - `cardano-cli-setup.md` - Cardano CLI installation guide
  - `testnet-deployment.md` - Testnet deployment guide
  - `mainnet-migration.md` - Mainnet migration checklist
  - `test-evidence/` - Test output documentation

#### `scripts/`
- **Purpose**: Deployment scripts and utility scripts for contract operations
- **Lifecycle**: Active - used for deployment and testing
- **Cardano Dependency**: Cardano CLI
- **Modification Policy**: Updated as deployment processes evolve
- **Contents**:
  - `deploy.sh` - Contract deployment script
  - `mint_test_tokens.sh` - Test token minting script
  - `simulate_oracles.sh` - Oracle simulation script

#### `specs/`
- **Purpose**: Feature specifications, design documents, and implementation plans
- **Lifecycle**: Active - used for feature planning and tracking
- **Cardano Dependency**: None (specification only)
- **Modification Policy**: Updated as features are planned and implemented
- **Contents**:
  - `001-milestone-token-distribution/` - First feature specification
  - `002-audit-repo/` - Repository audit feature specification

#### `src/`
- **Purpose**: Aiken smart contract source code
- **Lifecycle**: Active - core project code
- **Cardano Dependency**: Aiken compiler, Plutus V2
- **Modification Policy**: Primary development directory
- **Structure**:
  - `cli/` - CLI command implementations
  - `contract/` - Core contract logic
  - `lib/` - Shared libraries
  - `validator/` - Validator implementations
  - `blst/` - Vendored BLS12-381 signature library (external dependency)

#### `src/blst/`
- **Purpose**: Vendored BLS12-381 signature library (external dependency)
- **Lifecycle**: External - externally maintained, not modified by this project
- **Cardano Dependency**: Used by Cardano cryptographic operations
- **Modification Policy**: DO NOT MODIFY - external dependency
- **Source**: https://github.com/supranational/blst
- **Notes**: Cryptographic library for BLS signatures, vendored for build dependencies

#### `test-data/`
- **Purpose**: Test data files including allocations and oracle configurations
- **Lifecycle**: Active - used by test suites and deployment scripts
- **Cardano Dependency**: Cardano CLI (for address validation)
- **Modification Policy**: Updated as test scenarios evolve
- **Contents**:
  - `allocations.json` - Token allocation test data
  - `oracles.json` - Oracle address test data

#### `tests/`
- **Purpose**: Test suites for unit, integration, and validator tests
- **Lifecycle**: Active - maintained alongside source code
- **Cardano Dependency**: Aiken test framework
- **Modification Policy**: Updated as features are added
- **Structure**:
  - `unit/` - Unit tests
  - `integration/` - Integration tests
  - `validator/` - Validator-specific tests

#### `validators/`
- **Purpose**: Validator example files
- **Lifecycle**: Active - examples and reference implementations
- **Cardano Dependency**: Aiken compiler
- **Modification Policy**: Updated as examples evolve

### Files

#### `aiken.lock`
- **Purpose**: Lock file for Aiken dependencies, ensures reproducible builds
- **Lifecycle**: Active - auto-generated, should be committed
- **Cardano Dependency**: Aiken compiler
- **Modification Policy**: Auto-generated, commit changes

#### `aiken.toml`
- **Purpose**: Aiken project configuration file
- **Lifecycle**: Active - project configuration
- **Cardano Dependency**: Aiken compiler
- **Modification Policy**: Updated as project configuration changes

#### `plutus.json`
- **Purpose**: Plutus script configuration
- **Lifecycle**: Active - used for Plutus script compilation
- **Cardano Dependency**: Plutus
- **Modification Policy**: Updated as Plutus scripts evolve

#### `README.md`
- **Purpose**: Project root documentation and entry point
- **Lifecycle**: Active - primary project documentation
- **Cardano Dependency**: None (documentation only)
- **Modification Policy**: Updated as project evolves

## Lifecycle Status Definitions

- **active**: Currently maintained and used in the project
- **legacy**: Still present but deprecated, may be removed in future
- **to-remove**: Marked for removal during audit
- **external**: Vendored dependency, externally maintained, not modified by this project

## Cardano Dependency Types

- **Cardano Node**: Full Cardano node implementation (vendored)
- **Cardano CLI**: Command-line tools for transaction building and node interaction
- **Aiken compiler**: Smart contract compiler for Cardano
- **Plutus**: Cardano smart contract platform
- **Aiken test framework**: Testing framework for Aiken contracts

## Inventory Completeness

**Status**: Initial inventory created - all top-level directories and key files cataloged.

**Next Steps**:
- Complete detailed inventory entries for all subdirectories (if needed)
- Identify duplicate files and overlapping content
- Classify lifecycle status for all entries
- Annotate Cardano dependencies comprehensively
- Link to related documentation

## Related Documentation

- [Retirement Log](./retirement-log.md) - Log of removed/merged files
- [Solution Architecture](./solution-architecture.md) - Project structure and dependencies
- [Cardano Ecosystem Overview](./cardano-ecosystem-overview.md) - Cardano components and usage



