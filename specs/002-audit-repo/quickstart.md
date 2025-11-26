# Quickstart: Repository Audit & Documentation Overhaul

**Date**: 2025-01-27  
**Feature**: 002-audit-repo

## Overview

This quickstart guide provides a step-by-step approach to executing the repository audit and documentation overhaul. Follow these steps to systematically audit, reorganize, and enhance the repository documentation.

## Prerequisites

- Git repository access
- Markdown editor or text editor
- Understanding of repository structure
- Familiarity with Cardano ecosystem (helpful but not required)

## Phase 1: Inventory Creation

### Step 1.1: Catalog Top-Level Directories

1. List all top-level directories and files:
   ```bash
   ls -la /Users/stephen/Documents/GitHub/Aiken-Project
   ```

2. For each directory/file, determine:
   - Purpose: What is this asset used for?
   - Owner: Who maintains this? (if known)
   - Lifecycle status: active, legacy, to-remove, or external
   - Cardano dependency: Does it depend on Cardano components?

3. Create `docs/repository-inventory.md` with structured table:
   ```markdown
   | Name | Type | Purpose | Status | Cardano Dependency | Docs |
   |------|------|---------|--------|-------------------|------|
   | src/ | directory | Aiken smart contract source | active | Aiken compiler | [link] |
   ```

**Deliverable**: Complete inventory table with all top-level assets

---

### Step 1.2: Identify Duplicates and Redundancies

1. Search for duplicate file names:
   ```bash
   find . -type f -name "*.md" | sort | uniq -d
   ```

2. Review similar files for content overlap:
   - Compare README files in different directories
   - Check for duplicate documentation
   - Identify outdated versions

3. Document findings in `docs/retirement-log.md`:
   ```markdown
   ## 2025-01-27: Duplicate README files
   - **Removed**: `old/README.md`
   - **Authoritative**: `docs/README.md`
   - **Justification**: Content merged into main documentation
   ```

**Deliverable**: Retirement log entries for all duplicates identified

---

## Phase 2: Documentation Consolidation

### Step 2.1: Create Documentation Structure

1. Create `/docs` directory structure:
   ```bash
   mkdir -p docs/test-evidence
   ```

2. Organize existing documentation:
   - Move existing docs to `/docs` (if not already there)
   - Group by category (overview, setup, deployment, operations, reference)
   - Ensure consistent naming conventions

3. Create navigation structure:
   - Update root `README.md` with clear entry points
   - Add breadcrumbs to all documentation pages
   - Create table of contents for longer documents

**Deliverable**: Organized `/docs` structure with navigation

---

### Step 2.2: Create Glossary

1. Extract technical terms from existing documentation:
   - Scan all Markdown files for Cardano-specific terms
   - Identify project-specific terminology
   - Note terms that need definition

2. Create `docs/glossary.md`:
   - Organize alphabetically
   - Define each term clearly
   - Add cross-references between related terms
   - Link to Cardano official documentation where applicable

3. Update existing documentation:
   - Add glossary links to first occurrence of each term
   - Ensure ≥95% coverage of technical terms

**Deliverable**: Complete glossary with ≥95% term coverage

---

### Step 2.3: Create Cardano Ecosystem Overview

1. Identify Cardano components used:
   - Cardano Node (for testnet/mainnet)
   - Cardano CLI (for transaction building)
   - Aiken Compiler (for smart contracts)
   - CIP standards (CIP-68, etc.)

2. Document each component:
   - Component name and type
   - Protocol era (Conway)
   - How project uses component
   - Dependencies on other components
   - Applicable standards

3. Create `docs/cardano-ecosystem-overview.md`:
   - Start with high-level Cardano overview
   - Map project components to Cardano infrastructure
   - Explain project's role in Cardano ecosystem
   - Link to glossary for technical terms

**Deliverable**: Comprehensive Cardano ecosystem overview

---

## Phase 3: Test Evidence Documentation

### Step 3.1: Run Test Suites

1. Unit tests:
   ```bash
   cd /Users/stephen/Documents/GitHub/Aiken-Project
   aiken test
   ```

2. Integration tests:
   ```bash
   # Follow integration test instructions
   ```

3. Validator tests:
   ```bash
   # Follow validator test instructions
   ```

### Step 3.2: Capture Test Outputs

1. For each test suite:
   - Run tests and capture output
   - Note execution date and environment
   - Document prerequisites (Cardano socket, network, etc.)

2. Create test evidence documents:
   - `docs/test-evidence/unit-tests.md`
   - `docs/test-evidence/integration-tests.md`
   - `docs/test-evidence/validator-tests.md`

3. Include in each document:
   - Command used to run tests
   - Sample output (pass/fail summary)
   - Interpretation notes
   - Prerequisites
   - Expected runtime

**Deliverable**: Complete test evidence documentation

---

## Phase 4: README and Navigation Updates

### Step 4.1: Update Root README

1. Create clear entry points:
   - "Start Here" for newcomers
   - "Develop" for contributors
   - "Deploy" for deployment
   - "Operate" for operations

2. Add navigation structure:
   - Link to Cardano ecosystem overview
   - Link to setup guides
   - Link to testing guide
   - Link to contribution guide

3. Ensure all pathways reachable within 3 clicks

**Deliverable**: Updated README with clear navigation

---

### Step 4.2: Create Contribution Guide

1. Document documentation standards:
   - How to add new documentation
   - Glossary reference guidelines
   - How to evaluate duplicates
   - Link validation requirements

2. Create `docs/contribution-guide.md`:
   - Documentation structure guidelines
   - Glossary contribution process
   - Review process
   - Quality gates

**Deliverable**: Complete contribution guide

---

## Phase 5: Verification

### Step 5.1: Quality Gate Checks

1. **Inventory Completeness**: Verify 100% of top-level directories in inventory
2. **Glossary Coverage**: Spot check ≥95% term coverage
3. **Link Validity**: Validate all internal links resolve
4. **Navigation**: Verify all docs reachable within 3 clicks
5. **Test Evidence**: Confirm all test suites have sample outputs

### Step 5.2: Usability Testing

1. Test with new contributor persona:
   - Can they find Cardano ecosystem overview?
   - Can they understand project structure?
   - Can they locate deployment steps?

2. Test with maintainer persona:
   - Can they use inventory to find assets?
   - Can they check retirement log for removed files?
   - Can they verify test evidence?

**Deliverable**: Quality gate verification and usability test results

---

## Success Criteria

- ✅ 100% of top-level directories inventoried
- ✅ ≥95% glossary term coverage
- ✅ All documentation reachable within 3 clicks
- ✅ All test suites have documented sample outputs
- ✅ Zero duplicate or orphaned files (documented in retirement log)
- ✅ Cardano ecosystem overview complete
- ✅ Contribution guide published

---

## Next Steps

After completing this quickstart:

1. Review generated documentation for accuracy
2. Get feedback from contributors
3. Iterate based on feedback
4. Maintain documentation as repository evolves

## Troubleshooting

**Issue**: Cannot determine lifecycle status for asset  
**Solution**: Mark as "NEEDS REVIEW" in inventory, document uncertainty

**Issue**: Test outputs differ from documented examples  
**Solution**: Update test evidence with current outputs, note environment differences

**Issue**: Broken internal links  
**Solution**: Use link checker tool, fix all broken links before merge

**Issue**: Glossary term not found  
**Solution**: Add term to glossary, update documentation to link to it



