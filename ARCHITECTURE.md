# ARCHITECTURE.md

## Document Meta / 文档元信息
- Owner: Engineering / Owner: 工程团队
- Last Updated: 2026-03-05
- Source of Truth: Technical architecture and design choices / Source of Truth: 技术架构与设计选择
- Review Cadence: Per milestone / Review Cadence: 每个里程碑
- Upstream/Downstream:
  - Upstream: AGENTS.md, README.md
  - Downstream: PLAN.md, DECISIONS.md

## System Architecture / 系统架构
- CLI layer: `Typer` commands (`specify/plan/tasks/decide/state/analyze/commit/...`).
- Governance core: `rule_schema.py`, `rule_engine.py`, YAML rule files.
- Traceability support: markdown feature blocks + cross-doc ID references.
- Audit surface: git trace extraction + commit template checks + PR template checks.

<!-- specflow8:feature:F-001:start -->
## [F-001] Governance Engine Foundation
### Context
- Need deterministic governance checks for docs-first workflow.
- Checks must evolve by configuration, not hardcoded branching.

### Architecture Decisions
- Rule definitions externalized to YAML and loaded via schema validation.
- Checker registry maps rule `checker` to executable functions.
- Analyze output supports both human-readable and JSON payload.

### Related Decisions
- ADRs: `ADR-001`, `ADR-002`
- Evidence: `11cb7e7`, `03c0b2b`
<!-- specflow8:feature:F-001:end -->

<!-- specflow8:feature:F-000:start -->
## [F-000] PR Gate and Governance Hardening
### Context
- Commit-level trace existed, but PR-level structure was not enforced.
- Root docs needed operational content rather than pure templates.

### Architecture Decisions
- Add `pr_template` checker to rule engine with missing/required-field modes.
- Keep PR template source and runtime file synchronized.
- Treat root docs as first-class governance runtime artifacts.

### Related Decisions
- ADRs: `ADR-003`, `ADR-004`
- Evidence: `518468f`, `8fdde03`, `0a9258e`, `3ab43bd`
<!-- specflow8:feature:F-000:end -->
