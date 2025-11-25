# Research: Repository Audit & Documentation Overhaul

**Date**: 2025-01-27  
**Feature**: 002-audit-repo

## Purpose

This document consolidates research findings to resolve all "NEEDS CLARIFICATION" items identified in the Technical Context section of plan.md and establish best practices for repository documentation structure.

## Research Areas

### 1. Repository Documentation Structure Best Practices

**Decision**: Consolidate all documentation into `/docs` directory with clear navigation pathways:
- Overview documents (README, ecosystem overview, architecture)
- Setup/Deployment guides (testnet, mainnet, CLI setup)
- Reference materials (glossary, inventory, retirement log)
- Test evidence (sample outputs in `docs/test-evidence/`)

**Rationale**:
- Single location for all documentation improves discoverability
- Clear separation from source code (`src/`) and scripts (`scripts/`)
- Follows common open-source project conventions (e.g., GitHub documentation standards)
- Enables consistent cross-linking and breadcrumb navigation
- Test evidence stored separately prevents cluttering main documentation

**Alternatives Considered**:
- **Distributed documentation**: Keep docs near related code (e.g., `src/README.md`) - Rejected because it fragments documentation and makes onboarding harder
- **Wiki-based documentation**: Use GitHub Wiki - Rejected because it's harder to version control and review via PRs
- **Separate documentation site**: Use MkDocs/Docusaurus - Rejected because it adds complexity and the current Markdown structure is sufficient

---

### 2. Cardano Ecosystem Documentation Patterns

**Decision**: Create comprehensive Cardano ecosystem overview (`docs/cardano-ecosystem-overview.md`) that:
- Explains Cardano networks (testnet, mainnet) and protocol eras (targeting Conway)
- Documents Cardano components (node, CLI, Aiken compiler, oracles)
- References applicable standards (CIP-68, Plutus V2, etc.)
- Maps project's contracts, CLI tools, and scripts to Cardano infrastructure
- Links to official Cardano documentation and standards

**Rationale**:
- Provides essential context for contributors new to Cardano
- Clarifies project dependencies and assumptions
- Demonstrates how project fits within broader Cardano ecosystem
- Targets Conway era to ensure future-proof accuracy
- Enables contributors to understand Cardano-specific terminology before diving into code

**Alternatives Considered**:
- **Inline Cardano explanations**: Define terms only where they appear - Rejected because it creates repetition and doesn't provide ecosystem context
- **External links only**: Link to Cardano docs without project-specific mapping - Rejected because it doesn't explain how THIS project uses Cardano components
- **Separate Cardano tutorial**: Create full Cardano tutorial - Rejected because it's out of scope; focus on project-specific Cardano integration

---

### 3. Glossary Organization Approach

**Decision**: Single centralized glossary file (`docs/glossary.md`) with:
- Alphabetical organization for quick lookup
- Inline definitions on first use in other docs with links to glossary
- Cross-references between related terms
- Cardano-specific terms prioritized (validator, datum, redeemer, UTXO, CIP numbers, etc.)
- Project-specific terms included (milestone token distribution, oracle quorum, etc.)

**Rationale**:
- Single source of truth prevents definition drift
- Alphabetical organization enables quick scanning
- Links from docs to glossary maintain consistency without repetition
- Centralized location makes it easy to maintain and update
- Clear separation between Cardano ecosystem terms and project-specific terms

**Alternatives Considered**:
- **Distributed glossaries**: Separate glossary per documentation section - Rejected because it creates duplication and inconsistency
- **Inline-only definitions**: Define terms only where they appear - Rejected because it creates repetition and makes updates harder
- **JSON/YAML glossary**: Structured data format - Rejected because Markdown is more readable and easier to maintain

---

### 4. Test Evidence Documentation Standards

**Decision**: Document test evidence in `docs/test-evidence/` with:
- Markdown summaries for each test suite (unit, integration, validator)
- Sample command outputs showing expected pass/fail patterns
- Interpretation notes explaining what counts indicate success
- Prerequisites documented (Cardano socket path, network requirements)
- Timestamps and environment context for reproducibility

**Rationale**:
- Provides baseline for regression testing
- Enables reviewers to verify test behavior without running tests
- Documents expected outcomes for contributors
- Captures environment requirements that might not be obvious
- Markdown format is version-controlled and reviewable via PRs

**Alternatives Considered**:
- **Inline test outputs**: Embed outputs directly in testing guide - Rejected because it makes the guide too long and harder to maintain
- **Git-ignored test logs**: Store outputs but don't commit - Rejected because it doesn't help reviewers who can't run tests
- **Separate test evidence repo**: Store in different repository - Rejected because it fragments documentation and makes linking harder

---

### 5. Repository Inventory Format

**Decision**: Single Markdown file (`docs/repository-inventory.md`) with structured tables:
- Top-level directories: Purpose, owner, lifecycle status (active/legacy/to-remove), Cardano dependency
- Scripts: Purpose, usage, dependencies
- Documentation: Location, audience, last updated
- Vendored dependencies: Source, version, modification policy

**Rationale**:
- Single file provides comprehensive view of entire repository
- Structured tables enable quick scanning and filtering
- Markdown format is version-controlled and reviewable
- Clear lifecycle status guides maintenance decisions
- Cardano dependency annotations help understand project architecture

**Alternatives Considered**:
- **JSON/YAML inventory**: Structured data format - Rejected because Markdown is more readable and easier to review
- **Separate files per category**: One file per directory type - Rejected because it fragments the inventory and makes it harder to get complete picture
- **Embedded in README**: Include inventory in main README - Rejected because it makes README too long and harder to maintain

---

### 6. Retirement Log Format

**Decision**: Single Markdown file (`docs/retirement-log.md`) with chronological entries:
- Date of action
- File/directory removed/merged/archived
- Authoritative replacement (if merged)
- Justification for deletion
- Links to related documentation

**Rationale**:
- Chronological organization shows audit progression
- Documents rationale for each action enables future decision-making
- Links to replacements prevent broken references
- Single file provides complete audit trail
- Markdown format enables version control and review

**Alternatives Considered**:
- **Separate files per action**: One file per removed item - Rejected because it creates too many files and makes audit trail harder to follow
- **JSON/YAML log**: Structured data format - Rejected because Markdown narrative format is more readable for audit documentation
- **Git history only**: Rely on git log - Rejected because it doesn't capture rationale or link to replacements

---

## Implementation Notes

- All documentation will use consistent Markdown formatting with clear headings and cross-links
- Glossary terms will be linked using relative paths (`[term](../glossary.md#term)`)
- Test evidence will include both command outputs and interpretation summaries
- Repository inventory will be maintained as a living document, updated as repository evolves
- Retirement log will be append-only during audit phase, then maintained for future changes

