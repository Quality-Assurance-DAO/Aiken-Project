# Contribution Guide

**Navigation**: [Home](../README.md) > [Documentation](./README.md) > Contribution Guide

This guide provides standards and guidelines for contributing to the project documentation and codebase.

## Documentation Standards

### File Naming Conventions

- Use lowercase with hyphens: `cardano-cli-setup.md`
- Be descriptive and specific: `testnet-deployment.md` not `deployment.md`
- Group related docs with prefixes: `test-evidence/unit-tests.md`

### Documentation Structure

All documentation should be placed in the `docs/` directory:

- **Overview documents**: Ecosystem overview, architecture
- **Setup guides**: Installation, configuration
- **Deployment guides**: Testnet, mainnet migration
- **Reference materials**: Glossary, inventory, retirement log
- **Test evidence**: Sample test outputs in `docs/test-evidence/`

### Breadcrumb Navigation

All documentation pages must include breadcrumb navigation at the top:

```markdown
**Navigation**: [Home](../README.md) > [Documentation](./README.md) > Document Title
```

**Format**: `Home > Category > Document Title`

**Categories**:
- Overview (ecosystem, architecture)
- Setup (CLI setup, testnet deployment)
- Deployment (mainnet migration)
- Operations (testing, maintenance)
- Reference (glossary, inventory, retirement log)

## Adding New Documentation

### Step 1: Create Document

1. Create new Markdown file in appropriate `docs/` subdirectory
2. Use descriptive filename following naming conventions
3. Add breadcrumb navigation at top
4. Include clear title and overview section

### Step 2: Add Navigation Links

1. Add link to new document in `docs/README.md` under appropriate category
2. Update root `README.md` if document is a primary entry point
3. Add cross-references from related documents

### Step 3: Add Glossary Links

1. Identify technical terms used in document
2. Link first occurrence of each term to glossary: `[term](./glossary.md#term)`
3. Ensure ≥95% glossary term coverage

### Step 4: Validate Links

1. Verify all internal links resolve correctly
2. Check external links are valid
3. Ensure breadcrumb navigation is consistent

## Glossary Reference Guidelines

### When to Link to Glossary

- **First occurrence** of each technical term in a document
- **Complex terms** that benefit from detailed explanation
- **Cardano-specific terms** that may be unfamiliar to new contributors
- **Project-specific terms** that have specific meaning in this context

### Link Format

Use relative paths for glossary links:

```markdown
[validator](./glossary.md#validator)
[Cardano CLI](./glossary.md#cardano-cli)
[milestone token distribution](./glossary.md#milestone-token-distribution)
```

### Inline Definitions

For simple terms or when glossary link would be disruptive:

- Provide brief inline definition (1-2 sentences)
- Still link to glossary for detailed explanation
- Use inline definition for immediate context

### Adding New Glossary Terms

1. Add term to `docs/glossary.md` alphabetically within appropriate category
2. Provide clear, concise definition
3. Include related terms and external references
4. Add usage examples for project-specific terms
5. Update documentation to link to new term

## Duplicate Evaluation Process

### Identifying Duplicates

When adding new documentation, check for:

1. **Duplicate files**: Same content in multiple locations
2. **Overlapping content**: Similar information in different documents
3. **Outdated versions**: Old documentation that should be replaced

### Evaluation Criteria

Consider:
- **Purpose**: Does each document serve a distinct purpose?
- **Audience**: Are documents targeting different audiences?
- **Content**: Is there significant overlap or duplication?
- **Maintenance**: Can both documents be maintained effectively?

### Resolution Process

1. **Identify authoritative version**: Determine which document is the source of truth
2. **Merge content**: Consolidate unique content into authoritative version
3. **Update links**: Update all references to point to authoritative version
4. **Log retirement**: Add entry to `docs/retirement-log.md` if file is removed
5. **Preserve external links**: Document any external references that may break

### Retirement Log Entry

When removing or merging files, add entry to `docs/retirement-log.md`:

```markdown
## YYYY-MM-DD: [Action Type] - [Asset Name]

- **Asset**: Path to retired asset
- **Action**: removed | merged | archived
- **Authoritative Replacement**: Path to replacement (if merged)
- **Justification**: Reason for retirement action
- **Related Inventory Entry**: Link to repository inventory entry
- **External Links Preserved**: Notes about preserving external references
```

## Link Validation Requirements

### Internal Links

- **Use relative paths**: `./document.md` or `../README.md`
- **Verify links resolve**: Test all links before committing
- **Update broken links**: Fix or remove broken references
- **Use descriptive link text**: `[Cardano CLI Setup](./cardano-cli-setup.md)` not `[here](./cardano-cli-setup.md)`

### External Links

- **Verify links are valid**: Check external URLs before committing
- **Note link stability**: Document if external links may become unavailable
- **Use official sources**: Prefer official Cardano documentation over third-party sources

### Cross-References

- **Bidirectional where appropriate**: If Document A links to Document B, consider linking back
- **Contextual links**: Link to related sections, not just top-level documents
- **Consistent formatting**: Use same link format throughout documentation

### Validation Checklist

Before submitting documentation changes:

- [ ] All internal links resolve correctly
- [ ] External links are valid and accessible
- [ ] Breadcrumb navigation is consistent
- [ ] Glossary links use correct format
- [ ] Cross-references are bidirectional where appropriate
- [ ] No broken references or orphaned links

## Code Contribution Guidelines

### Code Structure

- Follow existing code organization in `src/`
- Place new modules in appropriate directories (`contract/`, `validator/`, `cli/`)
- Use Aiken coding standards and best practices

### Testing

- Add tests for new functionality in `tests/`
- Update test evidence documentation if test behavior changes
- Ensure all tests pass before submitting changes

### Documentation Updates

- Update relevant documentation when adding features
- Add glossary terms for new concepts
- Update architecture documentation if module structure changes

## Review Process

### Documentation Review

1. **Self-review**: Check links, formatting, and completeness
2. **Peer review**: Get feedback from other contributors
3. **Quality gates**: Verify glossary coverage, link validity, navigation consistency

### Quality Gates

Documentation must pass these checks:

- ✅ All internal links resolve correctly
- ✅ ≥95% glossary term coverage
- ✅ All documentation reachable within 3 clicks from README
- ✅ Breadcrumb navigation consistent across all pages
- ✅ No duplicate or orphaned files

## Related Documentation

- [Documentation Index](./README.md) - Complete documentation structure
- [Glossary](./glossary.md) - Technical term definitions
- [Repository Inventory](./repository-inventory.md) - Component catalog
- [Retirement Log](./retirement-log.md) - File removal log


