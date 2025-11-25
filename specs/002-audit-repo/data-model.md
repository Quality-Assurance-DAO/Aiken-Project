# Data Model: Repository Audit & Documentation Overhaul

**Date**: 2025-01-27  
**Feature**: 002-audit-repo

## Overview

This document defines the key entities and relationships for the repository audit and documentation overhaul feature. Since this is a documentation/audit feature rather than a code feature, the "data model" represents the documentation structure, inventory entities, and glossary organization.

## Core Entities

### 1. Repository Asset Inventory

**Purpose**: Comprehensive catalog of all repository components (directories, files, scripts, modules)

**Attributes**:
- `name`: Asset name (directory or file path)
- `type`: Asset type (directory, script, documentation, source_code, vendored)
- `purpose`: Brief description of asset's role
- `owner`: Responsible party or team (if known)
- `lifecycle_status`: Current status (active, legacy, to-remove, external)
- `cardano_dependency`: Relationship to Cardano components (node, CLI, Aiken, standards)
- `documentation_link`: Path to related documentation
- `last_updated`: Date of last significant change (if trackable)

**Relationships**:
- Links to Documentation Corpus entries
- References Cardano Ecosystem Overview components
- Tracks Retirement Log entries (for removed assets)

**Validation Rules**:
- Every top-level directory must have an inventory entry
- Lifecycle status must be one of: active, legacy, to-remove, external
- External/vendored assets must be marked as such (cannot be modified)

---

### 2. Documentation Corpus

**Purpose**: Organized collection of all Markdown documentation files

**Attributes**:
- `path`: File path relative to repository root
- `title`: Document title
- `audience`: Target audience (newcomer, contributor, maintainer, QA)
- `category`: Documentation category (overview, setup, deployment, operations, reference)
- `glossary_coverage`: List of technical terms used (for coverage tracking)
- `breadcrumb_path`: Navigation path showing document location in structure
- `related_docs`: Links to related documentation
- `last_updated`: Date of last update

**Relationships**:
- References Glossary entries for term definitions
- Links to other Documentation Corpus entries
- May reference Repository Asset Inventory entries
- May include Test Evidence Record references

**Validation Rules**:
- Every documentation file must have a clear audience and category
- First occurrence of each technical term must link to glossary or define inline
- Breadcrumb paths must be consistent and enable navigation
- Related docs links must be valid (no broken references)

---

### 3. Glossary Entry

**Purpose**: Centralized definition of technical terms

**Attributes**:
- `term`: Technical term name
- `definition`: Clear, concise definition
- `category`: Term category (cardano_ecosystem, project_specific, general)
- `related_terms`: Links to related glossary entries
- `usage_examples`: Example usage in project context (optional)
- `external_references`: Links to official Cardano documentation (if applicable)

**Relationships**:
- Referenced by Documentation Corpus entries
- May reference Cardano Ecosystem Overview components
- Cross-references other Glossary entries

**Validation Rules**:
- Terms must be alphabetically organized for quick lookup
- Definitions must be clear and accessible to target audience
- Cardano ecosystem terms must reference official documentation when available
- Project-specific terms must explain their role in this project

---

### 4. Cardano Ecosystem Overview Component

**Purpose**: Documentation of Cardano components and how project uses them

**Attributes**:
- `component_name`: Name of Cardano component (e.g., "Cardano Node", "Aiken Compiler")
- `component_type`: Type (network, tool, standard, protocol)
- `protocol_era`: Target protocol era (Conway)
- `project_usage`: How this project uses the component
- `dependencies`: Other Cardano components this depends on
- `standards_references`: Applicable CIP numbers or standards
- `configuration_requirements`: Project-specific configuration needs

**Relationships**:
- Referenced by Repository Asset Inventory entries
- Links to Glossary entries for component-specific terms
- May reference Documentation Corpus entries

**Validation Rules**:
- All Cardano components used by project must be documented
- Protocol era must be specified (targeting Conway)
- Project usage must explain specific integration points
- Standards references must include CIP numbers or official documentation links

---

### 5. Retirement Log Entry

**Purpose**: Record of files/directories removed, merged, or archived during audit

**Attributes**:
- `date`: Date of retirement action
- `asset_name`: Name of retired asset (file or directory)
- `action_type`: Type of action (removed, merged, archived)
- `authoritative_replacement`: Path to replacement asset (if merged)
- `justification`: Reason for retirement action
- `related_inventory_entry`: Link to Repository Asset Inventory entry (if applicable)
- `external_links_preserved`: Notes about preserving external references (if applicable)

**Relationships**:
- References Repository Asset Inventory entries
- May reference Documentation Corpus entries (for merged docs)

**Validation Rules**:
- Every retirement action must have a justification
- Merged assets must reference authoritative replacement
- External link preservation must be documented if applicable
- Entries must be chronological for audit trail

---

### 6. Test Evidence Record

**Purpose**: Documented sample outputs from test suite execution

**Attributes**:
- `test_suite_name`: Name of test suite (unit, integration, validator)
- `command`: Command used to run tests
- `execution_date`: Date test was run
- `environment_context`: Environment details (OS, Cardano node version, network)
- `sample_output`: Captured test output (pass/fail summary)
- `interpretation_notes`: Explanation of what output indicates
- `prerequisites`: Required setup (Cardano socket, network connectivity, etc.)
- `expected_runtime`: Typical execution time

**Relationships**:
- Referenced by Documentation Corpus entries (testing guide)
- May reference Repository Asset Inventory entries (test scripts)

**Validation Rules**:
- Sample outputs must represent expected successful execution
- Prerequisites must be clearly documented
- Interpretation notes must explain pass/fail criteria
- Environment context must enable reproducibility

---

## State Transitions

### Repository Asset Lifecycle

```
[New Asset] → [Active] → [Legacy] → [To-Remove] → [Retired]
                ↓           ↓
            [External]  [Archived]
```

- **New Asset**: Recently added, not yet in inventory
- **Active**: Current, actively maintained
- **Legacy**: Still present but deprecated, may be removed in future
- **To-Remove**: Marked for removal in audit
- **Retired**: Removed, logged in Retirement Log
- **External**: Vendored dependency, externally managed
- **Archived**: Preserved for historical reference but not active

### Documentation Workflow

```
[Draft] → [Review] → [Published] → [Updated] → [Deprecated]
```

- **Draft**: Initial creation, not yet reviewed
- **Review**: Under review for accuracy and completeness
- **Published**: Available to users, linked from navigation
- **Updated**: Modified after publication
- **Deprecated**: Replaced by newer documentation, marked for removal

---

## Validation Rules Summary

1. **Inventory Completeness**: 100% of top-level directories must be in inventory
2. **Glossary Coverage**: ≥95% of technical terms must be defined or linked
3. **Documentation Navigation**: All docs must be reachable within 3 clicks from README
4. **Link Validity**: All internal links must resolve to existing files
5. **Lifecycle Consistency**: Assets marked "to-remove" must have Retirement Log entries
6. **Cardano Context**: All Cardano components used must be documented in ecosystem overview
7. **Test Evidence**: All documented test suites must have sample outputs

---

## Data Integrity Constraints

- No orphaned documentation (every doc must be linked from navigation)
- No broken internal links (all relative paths must resolve)
- No duplicate glossary entries (single source of truth per term)
- No inventory entries without lifecycle status
- No retirement actions without justification
- No test evidence without interpretation notes

