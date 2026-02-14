# GOVERNANCE.md

## Architectural Principles
1. **Modularity**: Components must be loosely coupled and highly cohesive.
2. **Immutability**: Structural integrity must be preserved. Root directories are fixed.
3. **Agent-Centric**: Designed for autonomous agent interaction and management.
4. **Auditability**: All actions must be logged and traceable.

## Branch Control Policy
- **Main Branch**: STRICTLY READ-ONLY for automated agents. Requires human approval for merges.
- **Development Branches**: All work must be conducted in feature or integration branches (e.g., `integration/gravity`).

## Agent Operational Limits
- Agents may not modify the root directory structure.
- Agents may not delete files without explicit authorization.
- Agents must validate their environment before execution.

## Structural Immutability Rule
- The root directories (00_GOVERNANCE to 08_DOCUMENTATION) are immutable.
- New root directories require a governance review.

## Mandatory Version Control
- All changes must be committed with clear, descriptive messages.
- Updates to `VERSION.md` are mandatory for release transitions.

## Audit Requirement
- Execution logs must be generated for significant structural changes and stored in `07_LOGS`.
