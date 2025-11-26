# API Contracts: Repository Audit & Documentation Overhaul

**Date**: 2025-01-27  
**Feature**: 002-audit-repo

## Overview

Since this is a documentation/audit feature rather than a code feature, "API contracts" represent the documentation structure, navigation pathways, and user interaction patterns rather than code APIs.

## Documentation Structure Contract

### Entry Points

**Contract**: The repository must provide clear entry points for different user personas.

**Endpoints**:
- `README.md` (root): Primary landing page with navigation to all pathways
- `docs/cardano-ecosystem-overview.md`: Cardano context entry point
- `docs/testing-guide.md`: Test execution entry point
- `docs/contribution-guide.md`: Contributor onboarding entry point

**Navigation Requirements**:
- All entry points must be reachable within 3 clicks from README
- Each entry point must include breadcrumb navigation
- Entry points must link to related documentation sections

---

## Documentation Navigation Contract

### Breadcrumb Structure

**Contract**: All documentation pages must include consistent breadcrumb navigation.

**Format**: `Home > Category > Document Title`

**Categories**:
- Overview (ecosystem, architecture)
- Setup (CLI setup, testnet deployment)
- Deployment (mainnet migration)
- Operations (testing, maintenance)
- Reference (glossary, inventory, retirement log)

**Requirements**:
- Breadcrumbs must be present on every documentation page
- Breadcrumbs must enable navigation to parent categories
- Breadcrumbs must be consistent across all pages

---

## Glossary Reference Contract

### Term Definition Pattern

**Contract**: Technical terms must be defined on first use with links to glossary.

**Pattern**: `[term](glossary.md#term)` or inline definition

**Requirements**:
- First occurrence of each term must link to glossary or define inline
- Glossary links must use consistent format: `[term](../glossary.md#term)`
- Inline definitions must be concise (1-2 sentences)
- Complex terms should link to glossary rather than inline definition

**Coverage Target**: ≥95% of technical terms must be defined or linked

---

## Repository Inventory Contract

### Inventory Entry Format

**Contract**: All repository assets must be documented in structured inventory format.

**Required Fields**:
- Asset name (path)
- Purpose (description)
- Lifecycle status (active/legacy/to-remove/external)
- Cardano dependency (if applicable)
- Documentation link (if applicable)

**Format**: Markdown table with columns: Name | Type | Purpose | Status | Cardano Dependency | Docs

**Requirements**:
- 100% of top-level directories must be included
- Lifecycle status must be one of: active, legacy, to-remove, external
- External/vendored assets must be clearly marked
- Inventory must be sortable and scannable

---

## Retirement Log Contract

### Retirement Entry Format

**Contract**: All file removals, merges, and archival actions must be logged.

**Required Fields**:
- Date (YYYY-MM-DD)
- Asset name (file/directory path)
- Action type (removed/merged/archived)
- Authoritative replacement (if merged)
- Justification (reason for action)

**Format**: Chronological Markdown list with structured entries

**Requirements**:
- Every retirement action must have a justification
- Merged assets must reference authoritative replacement
- External link preservation must be documented if applicable
- Entries must be chronological for audit trail

---

## Test Evidence Contract

### Test Output Documentation Format

**Contract**: All test suites must have documented sample outputs with interpretation.

**Required Fields**:
- Test suite name
- Command to run tests
- Sample output (pass/fail summary)
- Interpretation notes
- Prerequisites
- Expected runtime

**Format**: Markdown document in `docs/test-evidence/` with sections for each test suite

**Requirements**:
- Sample outputs must represent expected successful execution
- Prerequisites must be clearly documented
- Interpretation notes must explain pass/fail criteria
- Environment context must enable reproducibility

---

## Cardano Ecosystem Overview Contract

### Component Documentation Format

**Contract**: All Cardano components used by project must be documented with project-specific usage.

**Required Sections**:
- Component name and type
- Protocol era (Conway)
- How project uses component
- Dependencies on other Cardano components
- Applicable standards (CIP numbers)
- Project-specific configuration requirements

**Format**: Narrative Markdown with clear sections and cross-links

**Requirements**:
- All Cardano components used must be documented
- Protocol era must be specified (targeting Conway)
- Project usage must explain specific integration points
- Standards references must include CIP numbers or official documentation links

---

## Cross-Reference Contract

### Documentation Linking Standards

**Contract**: All documentation must use consistent cross-reference patterns.

**Link Types**:
- Glossary references: `[term](../glossary.md#term)`
- Documentation references: `[title](./document.md)`
- Inventory references: `[asset](../repository-inventory.md#asset-name)`
- External references: `[title](https://external-url)` (with note if link may break)

**Requirements**:
- All internal links must use relative paths
- All links must be validated (no broken references)
- External links must note if they may become unavailable
- Cross-references must be bidirectional where appropriate

---

## Validation Contract

### Documentation Quality Gates

**Contract**: Documentation must pass quality gates before publication.

**Gates**:
1. **Completeness**: All required sections present
2. **Glossary Coverage**: ≥95% of terms defined or linked
3. **Link Validity**: All internal links resolve
4. **Navigation**: All docs reachable within 3 clicks
5. **Inventory**: 100% of top-level directories inventoried
6. **Test Evidence**: All test suites have sample outputs

**Requirements**:
- Quality gates must be verified before merge
- Violations must be documented and justified
- Quality gates must be re-checked after major updates



