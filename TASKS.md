# TASKS.md

## Document Meta / 文档元信息
- Owner: Engineering / Owner: 工程团队
- Last Updated: 2026-03-05
- Source of Truth: Executable task queue / Source of Truth: 可执行任务队列
- Review Cadence: Weekly / Review Cadence: 每周
- Upstream/Downstream:
  - Upstream: PLAN.md, DECISIONS.md
  - Downstream: STATE.md

## Task Governance Constraints / 任务治理约束
- Required columns are enforced by parser and rule checks.
- `RelatedADR` must be linked, otherwise `WaiverReason` must explain.
- `DependsOn` must not create dependency cycles.

<!-- specflow8:feature:F-001:start -->
## [F-001] Governance Engine Foundation Tasks
### Task Queue / 任务队列
| ID | Feature | Title | Priority | Status | Owner | Due | DependsOn | RelatedPlan | RelatedADR | Evidence | DoD | WaiverReason |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T-001 | F-001 | Build YAML rule schema and runtime rule loader | P0 | done | Maintainers | 2026-03-05 | None | F-001 | ADR-001 | commit:11cb7e7 | `load_rules` validates schema and loads all configured rule files | None |
| T-002 | F-001 | Implement traceability and quality gate checks | P0 | done | Maintainers | 2026-03-05 | T-001 | F-001 | ADR-001 | commit:11cb7e7 | Analyzer reports TRACE/QUALITY findings with stage-aware severity | None |
| T-003 | F-001 | Enforce conventional commit trace validation | P1 | done | Maintainers | 2026-03-05 | T-002 | F-001 | ADR-002 | commit:03c0b2b | Commit message format includes header + stage/feature/Refs fields | None |
<!-- specflow8:feature:F-001:end -->

<!-- specflow8:feature:F-000:start -->
## [F-000] PR Gate and Root Governance Hardening Tasks
### Task Queue / 任务队列
| ID | Feature | Title | Priority | Status | Owner | Due | DependsOn | RelatedPlan | RelatedADR | Evidence | DoD | WaiverReason |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T-004 | F-000 | Add PR template presence and field checks in analyzer | P0 | done | Maintainers | 2026-03-05 | None | F-000 | ADR-003 | commit:518468f | `PR_TEMPLATE_MISSING` and `PR_TEMPLATE_FIELD_MISSING` fire in strict mode | None |
| T-005 | F-000 | Upgrade PR template and keep source/runtime template aligned | P1 | done | Maintainers | 2026-03-05 | T-004 | F-000 | ADR-003 | commit:0a9258e | `.github` and template source contain the same governance-required fields | None |
| T-006 | F-000 | Replace root placeholder docs with project self-governance records | P1 | done | Maintainers | 2026-03-05 | T-005 | F-000 | ADR-004 | commit:3ab43bd | Root docs are actionable governance docs for operating specflow8 on itself | None |
<!-- specflow8:feature:F-000:end -->

## AC Mapping / AC 映射
| AC-ID | RelatedTasks | Evidence |
|---|---|---|
| AC-001 | T-001,T-002 | commit:11cb7e7 |
| AC-002 | T-003 | commit:03c0b2b |
| AC-003 | T-004,T-005,T-006 | commit:518468f, commit:0a9258e, commit:3ab43bd |
