# Tasks: Repository Audit & Documentation Overhaul

**Input**: Design documents from `/specs/002-audit-repo/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Tests are NOT requested for this documentation/audit feature. This feature focuses on documentation creation and repository organization.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Documentation files: `docs/` at repository root
- Test evidence: `docs/test-evidence/` subdirectory
- Source code structure remains unchanged: `src/`, `tests/`, `scripts/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and documentation structure setup

- [ ] T001 Create `docs/` directory structure per implementation plan in plan.md
- [ ] T002 [P] Create `docs/test-evidence/` subdirectory for test output documentation
- [ ] T003 [P] Audit existing documentation files in repository root and identify current locations

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core documentation infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Create documentation navigation structure and breadcrumb pattern standards in `docs/README.md`
- [ ] T005 [P] Establish documentation file naming conventions and organization guidelines
- [ ] T006 [P] Create cross-reference link validation checklist for documentation quality gates
- [ ] T007 Audit all top-level directories and create initial inventory data structure

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Maintainer Gains Single Source of Truth (Priority: P1) 🎯 MVP

**Goal**: Create comprehensive repository inventory and retirement log so maintainers can immediately determine asset status, duplicates, and removal actions without reading source code.

**Independent Test**: Review the published `docs/repository-inventory.md` and `docs/retirement-log.md` to verify that every top-level directory and script is classified with status, owner, and action taken—no code changes are required to validate.

### Implementation for User Story 1

- [ ] T008 [US1] Catalog all top-level directories and create initial inventory entries in `docs/repository-inventory.md`
- [ ] T009 [US1] Identify duplicate files and overlapping content across repository
- [ ] T010 [US1] Create `docs/retirement-log.md` with chronological entry structure per retirement log contract
- [ ] T011 [US1] Document first retirement log entry for any identified duplicates in `docs/retirement-log.md`
- [ ] T012 [US1] Complete repository inventory table with all required fields (Name, Type, Purpose, Status, Cardano Dependency, Docs) in `docs/repository-inventory.md`
- [ ] T013 [US1] Classify each inventory entry with lifecycle status (active/legacy/to-remove/external) in `docs/repository-inventory.md`
- [ ] T014 [US1] Annotate Cardano dependencies for each inventory entry that uses Cardano components in `docs/repository-inventory.md`
- [ ] T015 [US1] Link inventory entries to related documentation where applicable in `docs/repository-inventory.md`
- [ ] T016 [US1] Verify 100% of top-level directories are represented in inventory per success criteria SC-001
- [ ] T017 [US1] Remove or archive duplicate files identified during audit and log actions in `docs/retirement-log.md`
- [ ] T018 [US1] Document authoritative replacements for merged files in `docs/retirement-log.md`
- [ ] T019 [US1] Add justification for each retirement action in `docs/retirement-log.md`
- [ ] T020 [US1] Mark vendored directories (cardano-node/, src/blst/) as external dependencies in `docs/repository-inventory.md`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Maintainers can review inventory and retirement log to understand repository structure.

---

## Phase 4: User Story 2 - New Contributor Understands Cardano Context (Priority: P2)

**Goal**: Create Cardano ecosystem overview, centralized glossary, and navigation structure so new contributors can understand project context and locate deployment steps within 15 minutes.

**Independent Test**: Walk through the reorganized documentation starting from the README to verify that the Cardano ecosystem overview, glossary, and cross-linked guides explain terminology and provide next steps without external coaching.

### Implementation for User Story 2

- [ ] T021 [US2] Extract technical terms from existing documentation files for glossary creation
- [ ] T022 [US2] Create `docs/glossary.md` with alphabetical organization per glossary organization decision in research.md
- [ ] T023 [US2] Define Cardano ecosystem terms (validator, datum, redeemer, UTXO, CIP numbers) in `docs/glossary.md`
- [ ] T024 [US2] Define project-specific terms (milestone token distribution, oracle quorum) in `docs/glossary.md`
- [ ] T025 [US2] Add cross-references between related glossary terms in `docs/glossary.md`
- [ ] T026 [US2] Link glossary entries to official Cardano documentation where applicable in `docs/glossary.md`
- [ ] T027 [US2] Create `docs/cardano-ecosystem-overview.md` with high-level Cardano overview targeting Conway era
- [ ] T028 [US2] Document Cardano networks (testnet, mainnet) and protocol eras in `docs/cardano-ecosystem-overview.md`
- [ ] T029 [US2] Document Cardano Node component and project usage in `docs/cardano-ecosystem-overview.md`
- [ ] T030 [US2] Document Cardano CLI component and project usage in `docs/cardano-ecosystem-overview.md`
- [ ] T031 [US2] Document Aiken Compiler component and project usage in `docs/cardano-ecosystem-overview.md`
- [ ] T032 [US2] Document applicable CIP standards (CIP-68, Plutus V2) in `docs/cardano-ecosystem-overview.md`
- [ ] T033 [US2] Map project contracts, CLI tools, and scripts to Cardano infrastructure in `docs/cardano-ecosystem-overview.md`
- [ ] T034 [US2] Create `docs/solution-architecture.md` documenting module boundaries and dependencies per FR-006
- [ ] T035 [US2] Document flow from configuration through deployment in `docs/solution-architecture.md`
- [ ] T036 [US2] Consolidate existing documentation files into `docs/` directory structure per FR-003
- [ ] T037 [US2] Add breadcrumb navigation to all documentation pages per navigation contract
- [ ] T038 [US2] Update root `README.md` with clear entry points (Start here, Develop, Deploy, Operate) per FR-007
- [ ] T039 [US2] Add navigation links to Cardano ecosystem overview from README in `README.md`
- [ ] T040 [US2] Add navigation links to setup guides from README in `README.md`
- [ ] T041 [US2] Add navigation links to testing guide from README in `README.md`
- [ ] T042 [US2] Ensure all documentation reachable within 3 clicks from README per navigation contract
- [ ] T043 [US2] Add glossary links to first occurrence of each technical term in existing documentation files
- [ ] T044 [US2] Verify ≥95% glossary term coverage per success criteria SC-002
- [ ] T045 [US2] Create `docs/contribution-guide.md` with documentation standards per FR-008
- [ ] T046 [US2] Document how to add new documents in `docs/contribution-guide.md`
- [ ] T047 [US2] Document glossary reference guidelines in `docs/contribution-guide.md`
- [ ] T048 [US2] Document duplicate evaluation process in `docs/contribution-guide.md`
- [ ] T049 [US2] Document link validation requirements in `docs/contribution-guide.md`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. New contributors can navigate documentation and understand Cardano context.

---

## Phase 5: User Story 3 - QA Captures Test Evidence (Priority: P3)

**Goal**: Document test suites with sample outputs so QA engineers and future readers know what success looks like without re-running every test.

**Independent Test**: Execute the prescribed `tests/` and `aiken test` commands, capture the summarized results table, and confirm that the documentation stores both the command and sample output with interpretation notes.

### Implementation for User Story 3

- [ ] T050 [US3] Create `docs/testing-guide.md` documenting how to run all test suites per FR-009
- [ ] T051 [US3] Document unit test execution command and prerequisites in `docs/testing-guide.md`
- [ ] T052 [US3] Document integration test execution command and prerequisites in `docs/testing-guide.md`
- [ ] T053 [US3] Document validator test execution command and prerequisites in `docs/testing-guide.md`
- [ ] T054 [US3] Document CLI test execution command and prerequisites in `docs/testing-guide.md`
- [ ] T055 [US3] Run unit tests and capture sample output for `docs/test-evidence/unit-tests.md`
- [ ] T056 [US3] Document unit test sample output with pass/fail summary in `docs/test-evidence/unit-tests.md`
- [ ] T057 [US3] Add interpretation notes explaining pass/fail criteria for unit tests in `docs/test-evidence/unit-tests.md`
- [ ] T058 [US3] Document prerequisites (Cardano socket, network requirements) for unit tests in `docs/test-evidence/unit-tests.md`
- [ ] T059 [US3] Document expected runtime for unit tests in `docs/test-evidence/unit-tests.md`
- [ ] T060 [US3] Run integration tests and capture sample output for `docs/test-evidence/integration-tests.md`
- [ ] T061 [US3] Document integration test sample output with pass/fail summary in `docs/test-evidence/integration-tests.md`
- [ ] T062 [US3] Add interpretation notes explaining pass/fail criteria for integration tests in `docs/test-evidence/integration-tests.md`
- [ ] T063 [US3] Document prerequisites (Cardano socket path, network connectivity) for integration tests in `docs/test-evidence/integration-tests.md`
- [ ] T064 [US3] Document expected runtime for integration tests in `docs/test-evidence/integration-tests.md`
- [ ] T065 [US3] Run validator tests and capture sample output for `docs/test-evidence/validator-tests.md`
- [ ] T066 [US3] Document validator test sample output with pass/fail summary in `docs/test-evidence/validator-tests.md`
- [ ] T067 [US3] Add interpretation notes explaining pass/fail criteria for validator tests in `docs/test-evidence/validator-tests.md`
- [ ] T068 [US3] Document prerequisites for validator tests in `docs/test-evidence/validator-tests.md`
- [ ] T069 [US3] Document expected runtime for validator tests in `docs/test-evidence/validator-tests.md`
- [ ] T070 [US3] Link test evidence documents from testing guide in `docs/testing-guide.md`
- [ ] T071 [US3] Add environment context (OS, Cardano node version, network) to test evidence documents
- [ ] T072 [US3] Verify all test suites have documented sample outputs per success criteria SC-004

**Checkpoint**: All user stories should now be independently functional. Test evidence is documented and accessible.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Quality gates, verification, and final polish affecting all user stories

- [ ] T073 [P] Validate all internal links resolve correctly across all documentation files
- [ ] T074 [P] Verify 100% of top-level directories are in inventory per quality gate
- [ ] T075 [P] Spot check ≥95% glossary term coverage per quality gate
- [ ] T076 [P] Verify all documentation reachable within 3 clicks from README per quality gate
- [ ] T077 Create verification checklist in `specs/002-audit-repo/checklists/requirements.md` per FR-010
- [ ] T078 Document inventory completeness verification steps in verification checklist
- [ ] T079 Document glossary coverage verification steps in verification checklist
- [ ] T080 Document link validity verification steps in verification checklist
- [ ] T081 Document navigation pathway verification steps in verification checklist
- [ ] T082 Document test evidence verification steps in verification checklist
- [ ] T083 Run usability dry-run with new contributor persona per success criteria SC-003
- [ ] T084 Document zero duplicate or orphaned files verification per success criteria SC-005
- [ ] T085 Update any external references that may break due to file moves
- [ ] T086 Ensure all breadcrumb navigation is consistent across documentation pages
- [ ] T087 Verify retirement log entries are chronological and complete
- [ ] T088 Final review of all documentation for consistency and completeness

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Depends on US1 for inventory structure but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May reference US2 documentation but should be independently testable

### Within Each User Story

- Inventory creation before retirement log entries (US1)
- Glossary creation before adding glossary links to documentation (US2)
- Test execution before documenting test evidence (US3)
- Core documentation before navigation updates
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, user stories can start in parallel (if team capacity allows)
- Within US1: Inventory cataloging and duplicate identification can run in parallel
- Within US2: Glossary creation, ecosystem overview, and solution architecture can run in parallel
- Within US3: Different test suite documentation can run in parallel
- All Polish phase tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch inventory cataloging and duplicate identification together:
Task: "Catalog all top-level directories and create initial inventory entries in docs/repository-inventory.md"
Task: "Identify duplicate files and overlapping content across repository"

# Launch Cardano dependency annotation and lifecycle classification together:
Task: "Classify each inventory entry with lifecycle status (active/legacy/to-remove/external) in docs/repository-inventory.md"
Task: "Annotate Cardano dependencies for each inventory entry that uses Cardano components in docs/repository-inventory.md"
```

---

## Parallel Example: User Story 2

```bash
# Launch glossary and ecosystem overview creation together:
Task: "Create docs/glossary.md with alphabetical organization per glossary organization decision in research.md"
Task: "Create docs/cardano-ecosystem-overview.md with high-level Cardano overview targeting Conway era"
Task: "Create docs/solution-architecture.md documenting module boundaries and dependencies per FR-006"

# Launch documentation consolidation and navigation updates together:
Task: "Consolidate existing documentation files into docs/ directory structure per FR-003"
Task: "Add breadcrumb navigation to all documentation pages per navigation contract"
Task: "Update root README.md with clear entry points (Start here, Develop, Deploy, Operate) per FR-007"
```

---

## Parallel Example: User Story 3

```bash
# Launch test evidence documentation for different test suites together:
Task: "Run unit tests and capture sample output for docs/test-evidence/unit-tests.md"
Task: "Run integration tests and capture sample output for docs/test-evidence/integration-tests.md"
Task: "Run validator tests and capture sample output for docs/test-evidence/validator-tests.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Inventory & Retirement Log)
4. **STOP and VALIDATE**: Review inventory and retirement log to verify 100% coverage and clear status classification
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Review (MVP!)
3. Add User Story 2 → Test independently → Review
4. Add User Story 3 → Test independently → Review
5. Add Polish phase → Final verification → Complete

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple team members:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Team Member A: User Story 1 (Inventory & Retirement Log)
   - Team Member B: User Story 2 (Glossary & Ecosystem Overview) - can start after US1 inventory structure
   - Team Member C: User Story 3 (Test Evidence) - can start independently
3. Stories complete and integrate independently
4. Team collaborates on Polish phase for final verification

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- This is a documentation/audit feature - no code changes required
- Verify quality gates after each phase
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- All file paths must be absolute or relative to repository root
- Preserve external links when moving documentation files

---

## Summary

**Total Task Count**: 88 tasks

**Task Count Per User Story**:
- Phase 1 (Setup): 3 tasks
- Phase 2 (Foundational): 4 tasks
- Phase 3 (User Story 1 - P1): 13 tasks
- Phase 4 (User Story 2 - P2): 28 tasks
- Phase 5 (User Story 3 - P3): 23 tasks
- Phase 6 (Polish): 16 tasks

**Parallel Opportunities Identified**:
- Setup phase: 2 parallel tasks
- Foundational phase: 2 parallel tasks
- User Story 1: Multiple parallel opportunities for inventory cataloging and classification
- User Story 2: Multiple parallel opportunities for glossary, ecosystem overview, and navigation
- User Story 3: All test evidence documentation can run in parallel
- Polish phase: 4 parallel verification tasks

**Independent Test Criteria**:
- **User Story 1**: Review published inventory and retirement log to verify 100% coverage and clear status classification
- **User Story 2**: Walk through documentation from README to verify Cardano context understanding and navigation within 3 clicks
- **User Story 3**: Execute test commands and verify documented outputs match expected results

**Suggested MVP Scope**: User Story 1 only (Inventory & Retirement Log) - provides immediate value to maintainers and enables downstream improvements

**Format Validation**: ✅ All tasks follow the checklist format:
- ✅ Checkbox: `- [ ]`
- ✅ Task ID: T001-T088
- ✅ [P] marker: Included where tasks can run in parallel
- ✅ [Story] label: US1, US2, US3 included for user story phases
- ✅ File paths: All tasks include exact file paths

