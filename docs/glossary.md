# Glossary

**Navigation**: [Home](../README.md) > [Documentation](./README.md) > Glossary

This glossary provides definitions for technical terms used throughout the project documentation. Terms are organized alphabetically for quick lookup.

## Cardano Ecosystem Terms

### Aiken
A smart contract compiler and development framework for Cardano. Aiken compiles smart contract code written in the Aiken language to Plutus V2 scripts that run on Cardano. This project uses Aiken for all smart contract development.

**Related Terms**: [Plutus](#plutus), [Validator](#validator)  
**External Reference**: [Aiken Documentation](https://aiken-lang.org/)

### Cardano CLI
Command-line interface tools for interacting with Cardano networks. The Cardano CLI (`cardano-cli`) provides commands for building transactions, querying blockchain state, managing keys, and interacting with Cardano nodes. This project uses Cardano CLI for transaction building and deployment scripts.

**Related Terms**: [Cardano Node](#cardano-node), [Transaction](#transaction)  
**External Reference**: [Cardano CLI Documentation](https://github.com/IntersectMBO/cardano-node/tree/master/cardano-cli)

### Cardano Node
The core Cardano blockchain node software that maintains the blockchain state, validates transactions, and participates in consensus. This project vendors the Cardano Node repository for local development and testing.

**Related Terms**: [Cardano CLI](#cardano-cli), [Testnet](#testnet), [Mainnet](#mainnet), [Chain Tip](#chain-tip), [Fork](#fork)  
**External Reference**: [Cardano Node Repository](https://github.com/intersectmbo/cardano-node)

### Chain Tip
The most recent block at the end of the best (longest) valid blockchain. The tip represents the current state of the blockchain from the node's perspective. When logs show "Chain extended, new tip", it means a new block was successfully added to the chain and is now the latest block. The tip changes as new blocks are added through consensus.

**Related Terms**: [Fork](#fork), [Cardano Node](#cardano-node)  
**Usage**: Query with `cardano-cli query tip` to see the current chain tip

### Fork
A blockchain fork occurs when there are multiple valid chain branches (alternative histories). When a node receives a block that "fits onto some fork", it means the block is valid and can be added to one of the possible chain branches, but it may not be on the main chain yet. The node will eventually select the longest valid chain as the canonical chain. Temporary forks are normal in distributed systems and resolve through consensus.

**Related Terms**: [Chain Tip](#chain-tip), [Cardano Node](#cardano-node)  
**Usage**: Log messages like "Block fits onto some fork" indicate normal blockchain operation

### CIP (Cardano Improvement Proposal)
A formal proposal document describing improvements, standards, or features for the Cardano ecosystem. CIPs are numbered (e.g., CIP-68) and follow a standardized format. This project may reference CIPs for standards compliance.

**Related Terms**: [Cardano Ecosystem](#cardano-ecosystem)  
**External Reference**: [CIP Repository](https://github.com/cardano-foundation/CIPs)

### Conway Era
The current Cardano protocol era, named after mathematician John Horton Conway. The Conway era introduces governance features and represents the latest Cardano protocol capabilities. This project targets Conway era for all smart contracts.

**Related Terms**: [Protocol Era](#protocol-era), [Cardano Ecosystem](#cardano-ecosystem)  
**External Reference**: [Cardano Protocol Eras](https://docs.cardano.org/cardano-testnet/about/introduction/)

### Datum
Data attached to a UTXO in Cardano's extended UTXO (eUTXO) model. Datums store state information for smart contracts and can be referenced by validators during transaction validation. This project uses datums to store contract state (allocations, claims, milestones).

**Related Terms**: [UTXO](#utxo), [Validator](#validator), [Redeemer](#redeemer)  
**External Reference**: [Cardano Datum Documentation](https://docs.cardano.org/plutus/datumhash-redeemers/)

### Mainnet
The production Cardano blockchain network where real ADA and assets are transacted. Mainnet is the live network used by end users. This project provides migration guides for deploying contracts to mainnet.

**Related Terms**: [Testnet](#testnet), [Cardano Node](#cardano-node), [Network Magic](#network-magic)  
**External Reference**: [Cardano Mainnet](https://cardano.org/)

### Network Magic
A numeric identifier that distinguishes different Cardano networks. Testnets use network magic values (e.g., Preprod uses 1, Preview uses 2), while mainnet uses no magic value (specified with `--mainnet`). Network magic prevents accidental cross-network transactions and ensures database isolation.

**Related Terms**: [Preprod](#preprod), [Preview](#preview), [Mainnet](#mainnet)  
**Usage**: See `docs/cardano-cli-setup.md` for network configuration details

### Preprod
A stable Cardano testnet with NetworkMagic 1, designed for production-like testing. Preprod mirrors mainnet behavior and is recommended for final testing before mainnet deployment. This project uses separate database directories (`db-preprod/`) for Preprod.

**Related Terms**: [Preview](#preview), [Testnet](#testnet), [Network Magic](#network-magic)  
**Usage**: Start with `./scripts/start_node.sh preprod`

### Preview
A bleeding-edge Cardano testnet with NetworkMagic 2, used for testing the latest Cardano features and protocol updates. Preview may have more frequent changes than Preprod. This project uses separate database directories (`db-preview/`) for Preview.

**Related Terms**: [Preprod](#preprod), [Testnet](#testnet), [Network Magic](#network-magic)  
**Usage**: Start with `./scripts/start_node.sh preview`

### Oracle
An external data source that provides information to smart contracts. In this project, oracles provide milestone completion data that triggers token distribution. The project uses an oracle quorum system where multiple oracle signatures are required.

**Related Terms**: [Oracle Quorum](#oracle-quorum), [Validator](#validator)  
**Usage**: See `test-data/oracles.json` for oracle address configuration

### Oracle Quorum
A consensus mechanism where multiple oracle signatures are required to validate milestone completion. This project uses a quorum threshold (e.g., 2 of 3 oracles) to ensure milestone data reliability before triggering token distribution.

**Related Terms**: [Oracle](#oracle), [Milestone Token Distribution](#milestone-token-distribution)

### Plutus
Cardano's smart contract platform and programming language. Plutus enables writing on-chain code (validators) and off-chain code (transaction building). This project compiles Aiken code to Plutus V2 scripts.

**Related Terms**: [Aiken](#aiken), [Validator](#validator), [Plutus V2](#plutus-v2)  
**External Reference**: [Plutus Documentation](https://plutus.readthedocs.io/)

### Plutus V2
The second version of the Plutus smart contract platform, introducing improved performance and new features. This project targets Plutus V2 for all smart contracts compiled from Aiken.

**Related Terms**: [Plutus](#plutus), [Aiken](#aiken)  
**External Reference**: [Plutus V2 Documentation](https://plutus.readthedocs.io/en/latest/plutus/v2/index.html)

### Protocol Era
A distinct phase in Cardano's evolution, each introducing new features and capabilities. Cardano has progressed through multiple eras: Byron, Shelley, Goguen, Babbage, and Conway. This project targets the Conway era.

**Related Terms**: [Conway Era](#conway-era), [Cardano Ecosystem](#cardano-ecosystem)

### Redeemer
Data provided when spending a UTXO that contains a validator script. Redeemers pass information to validators to control how UTXOs are spent. This project uses redeemers to specify claim actions and milestone identifiers.

**Related Terms**: [UTXO](#utxo), [Validator](#validator), [Datum](#datum)  
**External Reference**: [Cardano Redeemer Documentation](https://docs.cardano.org/plutus/datumhash-redeemers/)

### Testnet
A test network for Cardano that mirrors mainnet functionality but uses test tokens (tADA) instead of real ADA. Testnets allow developers to test smart contracts without financial risk. This project supports two testnets: [Preprod](#preprod) (NetworkMagic 1) and [Preview](#preview) (NetworkMagic 2), each with separate database directories.

**Related Terms**: [Mainnet](#mainnet), [Cardano Node](#cardano-node), [Preprod](#preprod), [Preview](#preview), [Network Magic](#network-magic)  
**External Reference**: [Cardano Testnet](https://docs.cardano.org/cardano-testnet/about/introduction/)

### Transaction
A unit of work on the Cardano blockchain that transfers value, executes smart contracts, or updates blockchain state. Transactions consume UTXOs as inputs and produce new UTXOs as outputs. This project uses Cardano CLI to build and submit transactions.

**Related Terms**: [UTXO](#utxo), [Cardano CLI](#cardano-cli), [Validator](#validator)  
**External Reference**: [Cardano Transaction Documentation](https://docs.cardano.org/cardano-components/cardano-cli/)

### UTXO (Unspent Transaction Output)
The fundamental unit of value on Cardano. UTXOs represent unspent outputs from previous transactions and serve as inputs for new transactions. Cardano uses an extended UTXO (eUTXO) model where UTXOs can contain datums and validator scripts.

**Related Terms**: [Datum](#datum), [Validator](#validator), [Transaction](#transaction)  
**External Reference**: [Cardano UTXO Model](https://docs.cardano.org/cardano-components/utxo-model/)

### Validator
A smart contract script that validates whether a UTXO can be spent. Validators run on-chain and check conditions based on datum, redeemer, and transaction context. This project implements validators in Aiken that compile to Plutus V2 scripts.

**Related Terms**: [Aiken](#aiken), [Plutus](#plutus), [Datum](#datum), [Redeemer](#redeemer)  
**Usage**: See `src/validator/` for validator implementations

## Project-Specific Terms

### Milestone Token Distribution
A token distribution system where tokens are distributed to beneficiaries based on milestone completion. Milestones are validated by an oracle quorum, and tokens are released according to vesting schedules. This is the core feature implemented by this project.

**Related Terms**: [Oracle Quorum](#oracle-quorum), [Vesting](#vesting), [Beneficiary](#beneficiary)

### Beneficiary
A recipient of tokens in the milestone token distribution system. Beneficiaries are specified in allocation data with addresses, token amounts, and milestone identifiers.

**Related Terms**: [Milestone Token Distribution](#milestone-token-distribution), [Allocation](#allocation)

### Allocation
A record specifying token distribution details for a beneficiary, including address, token amount, milestone identifier, and vesting timestamp. Allocations are stored in contract datums.

**Related Terms**: [Milestone Token Distribution](#milestone-token-distribution), [Beneficiary](#beneficiary), [Datum](#datum)

### Vesting
A time-based mechanism that delays token distribution until a specified timestamp. This project uses vesting timestamps to control when tokens become available to beneficiaries.

**Related Terms**: [Milestone Token Distribution](#milestone-token-distribution), [Allocation](#allocation)

## General Terms

### Build Artifacts
Compiled outputs and intermediate files generated during the build process. For Aiken projects, build artifacts include compiled Plutus scripts (`.plutus` files) and package lock files.

**Related Terms**: [Aiken](#aiken), [Plutus](#plutus)

### Execution Budget
Resource limits for smart contract execution on Cardano, measured in CPU units and memory units. Validators must operate within execution budget limits to be accepted by the network.

**Related Terms**: [Validator](#validator), [Transaction](#transaction)

## Cross-References

Terms are cross-referenced where relationships exist. Use the links to navigate between related concepts.

## Contributing

When adding new terms to this glossary:
1. Place terms alphabetically within their category
2. Provide clear, concise definitions
3. Include related terms and external references where applicable
4. Add usage examples for project-specific terms
5. Link to relevant documentation sections



