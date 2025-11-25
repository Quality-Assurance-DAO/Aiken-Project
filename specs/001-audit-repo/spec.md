# Feature Specification: Repository Audit & Documentation Overhaul

**Feature Branch**: `001-audit-repo`  
**Created**: 2025-11-25  
**Status**: Draft  
**Input**: User description: "Audit and reorganize this GitHub repository to improve clarity, usability, and maintainability. Remove any duplicate, redundant, or outdated files. Consolidate all documentation into a clear, logical structure, ensuring that every technical term is defined where it appears and that all sections are coherently linked. Include an overview explaining the wider Cardano ecosystem and explicitly describe how this solution fits within that context, including its role, dependencies, and interactions with relevant Cardano components or standards. If tests are present, provide documented example test results so their purpose and expected outcomes are clear. The final repository should present a clean, well-structured, and context-rich codebase that is easy for both newcomers and experienced contributors to understand and use."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Maintainer Gains Single Source of Truth (Priority: P1)

A repository maintainer needs to review any folder or script and immediately know whether it is current, duplicated elsewhere, or can be safely removed, using the new inventory and retirement log.

**Why this priority**: Without a definitive inventory, the audit cannot guide deletions or restructure, blocking every downstream improvement.

**Independent Test**: Review the published inventory and retirement log to verify that every top-level directory and script is classified with status, owner, and action taken—no code changes are required to validate.

**Acceptance Scenarios**:

1. **Given** the repository inventory, **When** the maintainer selects any top-level directory, **Then** its purpose, current status (active/legacy), and next action are documented without needing to read source code.
2. **Given** two files with overlapping names or content, **When** the maintainer consults the retirement log, **Then** the log states which file remains authoritative and where the other was removed, archived, or merged.

---

### User Story 2 - New Contributor Understands Cardano Context (Priority: P2)

A new contributor with Cardano familiarity but no project background opens the repository and, within a single documentation pathway, learns how the contracts, CLI tools, and scripts rely on Cardano components and standards.

**Why this priority**: Onboarding efficiency directly affects contribution velocity and reduces rework caused by misunderstanding Cardano-specific dependencies.

**Independent Test**: Walk through the reorganized documentation starting from the README to verify that the Cardano ecosystem overview, glossary, and cross-linked guides explain terminology and provide next steps without external coaching.

**Acceptance Scenarios**:

1. **Given** the new README entry point, **When** the contributor follows the "Cardano ecosystem overview" link, **Then** they reach a document that defines each referenced technical term (e.g., Aiken, CIP-68, Cardano CLI) on first use and shows how this project uses it.
2. **Given** any deployment, testing, or operations guide, **When** the contributor encounters a technical term, **Then** it is either defined inline or links to the shared glossary, and the document breadcrumb indicates how it fits into the overall structure.

---

### User Story 3 - QA Captures Test Evidence (Priority: P3)

A QA engineer needs to run the existing Aiken/unit/integration tests and publish representative outputs so future readers know what success looks like without re-running every test.

**Why this priority**: Documented test evidence proves the reorganized repository still behaves correctly and provides regression baselines for future work.

**Independent Test**: Execute the prescribed `tests/` and `aiken test` commands, capture the summarized results table, and confirm that the documentation stores both the command and sample output with interpretation notes.

**Acceptance Scenarios**:

1. **Given** the new testing guide, **When** the QA engineer runs the listed command for unit tests, **Then** the resulting pass/fail summary matches the documented example output within acceptable variance.
2. **Given** integration or CLI tests that require Cardano node connectivity, **When** the QA engineer cannot run them locally, **Then** the documentation points to stored example logs and explains required preconditions (e.g., Cardano socket path).

---

### Edge Cases

- Duplicate or outdated files reside inside vendor snapshots (e.g., `cardano-node/`) where direct deletion is unsafe; the audit must flag them as externally managed instead of removing them.
- Some Markdown files may be referenced by external documentation or blog posts; removing them without redirects or pointers breaks inbound links.
- Tests that depend on live Cardano endpoints might intermittently fail; the documented sample output must note the network height and prerequisites so reviewers can distinguish environment issues from regressions.
- Very large artifacts (logs, binaries) may need archival rather than hard deletion to preserve compliance or historical debugging context.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Produce a comprehensive inventory that lists every top-level directory, major submodule, script set, and documentation area, capturing purpose, owner, Cardano dependency, and current lifecycle status (active, legacy, to-remove).
- **FR-002**: Remove or archive duplicate, redundant, or outdated files and record each action in a retirement log that cites the authoritative replacement or justification for deletion.
- **FR-003**: Consolidate all documentation into a single navigable structure (e.g., `/docs` with README entry points) that includes breadcrumbs, a table of contents, and consistent naming conventions for guides, references, and checklists.
- **FR-004**: Ensure every technical term (Cardano CLI, CIP numbers, validator, datum, redeemer, quorum, etc.) is defined at first mention through inline definitions or a shared glossary that links back to relevant sections.
- **FR-005**: Create a Cardano ecosystem overview that explains networks (testnet, mainnet), components (node, CLI, Aiken compiler, oracles), applicable standards (e.g., CIP-68, Plutus V2), and explicitly maps how this project’s contracts, CLI, and scripts interact with each item.
- **FR-006**: Document the repository’s solution architecture, highlighting module boundaries (contracts, CLI, scripts, data files), their dependencies on Cardano infrastructure, and the flow from configuration through deployment.
- **FR-007**: Update the root `README` (or equivalent landing page) to guide both newcomers and experienced contributors to the new structure within three clicks, including “Start here,” “Develop,” “Deploy,” and “Operate” pathways.
- **FR-008**: Provide contribution and maintenance guidelines describing how to add new documents, how to reference glossary terms, and how to evaluate whether future files are duplicates or outdated.
- **FR-009**: For each available automated test suite (unit, integration, validator, CLI), document how to run it, prerequisites (e.g., Cardano socket), expected runtime, and include a captured sample output or summary table that explains the meaning of pass/fail counts.
- **FR-010**: Publish verification checklists that reviewers can follow to confirm the audit outcome (inventory complete, duplicates removed, docs linked, glossary coverage), enabling repeatable acceptance testing.

### Key Entities *(include if feature involves data)*

- **Repository Asset Inventory**: Structured list of directories, modules, and scripts; attributes include purpose, owner, lifecycle status, Cardano dependency, and link to documentation.
- **Documentation Corpus**: Organized set of Markdown assets grouped by audience (overview, setup, deployment, operations, reference) with metadata for cross-linking and glossary coverage.
- **Cardano Ecosystem Overview**: Narrative and diagram describing how the project interfaces with Cardano components (node, CLI, Aiken) and standards, including dependencies and assumptions.
- **Test Evidence Record**: Collection of commands, sample outputs, timestamps, and interpretation notes that demonstrate expected test outcomes for unit, integration, and CLI checks.

### Assumptions

- Third-party vendored directories (e.g., `cardano-node`, `trace-*`) remain intact but are documented as external dependencies instead of being reorganized.
- Existing automated tests under `tests/` and `aiken test` continue to run with the current toolchain; the audit focuses on documenting and showcasing their outputs.
- Contributors agree to adopt the new glossary and documentation conventions for all future content, ensuring ongoing consistency without retroactive enforcement beyond this audit.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of top-level directories and scripts are represented in the repository inventory with lifecycle status and Cardano dependency annotations, as verified by checklist reviewers.
- **SC-002**: Every documentation page in the new structure contains either an inline definition or glossary link for the first occurrence of each technical term, achieving at least 95% coverage during spot checks.
- **SC-003**: In a usability dry-run with at least three new contributors, each person can explain how the project fits within the Cardano ecosystem and locate deployment steps in under 15 minutes.
- **SC-004**: Execution of all documented tests produces archived sample outputs, and reviewers confirm that the outputs align with the expected results described in the testing guide without rerunning tests.
- **SC-005**: After the audit, maintainers report zero duplicated or orphaned files in a repository scan (documented via the verification checklist), demonstrating removal or archival of redundant content.
