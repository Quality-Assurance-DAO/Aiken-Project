# Documentation

**Navigation**: [Home](../README.md) > Documentation

This directory contains all project documentation organized by category.

## Documentation Structure

### Overview
- [Cardano Ecosystem Overview](./cardano-ecosystem-overview.md) - Cardano context and project integration
- [Solution Architecture](./solution-architecture.md) - Project structure and module boundaries

### Setup
- [Cardano CLI Setup](./cardano-cli-setup.md) - Install and configure Cardano CLI tools (includes network configuration)
- [Testnet Deployment](./testnet-deployment.md) - Step-by-step testnet deployment guide (Preprod and Preview)

### Deployment
- [Mainnet Migration](./mainnet-migration.md) - Checklist for promoting to mainnet

### Operations
- [Testing Guide](./testing-guide.md) - Test execution and evidence documentation

### Reference
- [Glossary](./glossary.md) - Centralized technical term definitions
- [Repository Inventory](./repository-inventory.md) - Comprehensive inventory of all directories/files
- [Retirement Log](./retirement-log.md) - Log of removed/merged/archived files
- [Contribution Guide](./contribution-guide.md) - Guidelines for adding docs and evaluating duplicates

## Breadcrumb Navigation Pattern

All documentation pages follow this breadcrumb pattern:

```
Home > Category > Document Title
```

**Categories**:
- **Overview**: Ecosystem context, architecture
- **Setup**: Installation, configuration
- **Deployment**: Testnet, mainnet migration
- **Operations**: Testing, maintenance
- **Reference**: Glossary, inventory, guides

## Documentation Standards

### File Naming Conventions
- Use lowercase with hyphens: `cardano-cli-setup.md`
- Be descriptive and specific: `testnet-deployment.md` not `deployment.md`
- Group related docs with prefixes: `test-evidence/unit-tests.md`

### Organization Guidelines
- Single `/docs` directory for all documentation
- Test evidence in `docs/test-evidence/` subdirectory
- Reference materials (glossary, inventory) at top level of `docs/`
- Setup/deployment guides grouped by category

### Cross-Reference Standards
- Glossary links: `[term](./glossary.md#term)`
- Documentation links: `[title](./document.md)`
- Inventory references: `[asset](./repository-inventory.md#asset-name)`
- External links: `[title](https://external-url)` (with note if link may break)

### Link Validation Checklist
- [ ] All internal links use relative paths
- [ ] All links resolve to existing files
- [ ] External links note if they may become unavailable
- [ ] Cross-references are bidirectional where appropriate
- [ ] No broken references (validate before merge)

## Quick Links

- [Start Here](../README.md) - Project overview and entry points
- [Cardano Ecosystem Overview](./cardano-ecosystem-overview.md) - Understand Cardano context
- [Testing Guide](./testing-guide.md) - Run and understand tests
- [Contribution Guide](./contribution-guide.md) - Add documentation



