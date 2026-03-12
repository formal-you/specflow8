# PLAN.md

## Document Meta / 文档元信息
- Owner: Engineering / Owner: 工程团队
- Last Updated: 2026-03-05
- Source of Truth: Milestone intent and phased planning / Source of Truth: 里程碑意图与分阶段计划
- Review Cadence: Per milestone / Review Cadence: 每个里程碑
- Upstream/Downstream:
  - Upstream: README.md, ARCHITECTURE.md, DOMAIN.md
  - Downstream: TASKS.md, DECISIONS.md

## Current Program Plan / 当前项目计划
| PlanID | Feature | RelatedSpec | Goal | Status | Owner | Exit Criteria |
|---|---|---|---|---|---|---|
| P-001 | F-001 | S-001 | Build rule-driven governance core and commit trace checks | done | Maintainers | Rule engine, rule schema, analyze checks are integrated and tested |
| P-002 | F-000 | S-001 | Close PR template governance loop and harden root governance docs | done | Maintainers | PR template checks active and root docs aligned with governance chain |

## Stage Gates / 阶段门禁
- specify -> plan: must include `S-XXX`, `F-XXX`, initial AC list.
- plan -> tasks: each deliverable maps to at least one `T-XXX`.
- tasks -> decide: architecture/interface/data/security change requires `ADR-XXX`.
- pre-merge: `specflow8 analyze --mode strict --all --enforce-commit-trace` must pass.

<!-- specflow8:feature:F-001:start -->
## [F-001] Governance Engine Foundation
### Plan Record
| PlanID | Feature | RelatedSpec | Goal | Non-Goals | Exit Criteria | Risks |
|---|---|---|---|---|---|---|
| P-001 | F-001 | S-001 | YAML-driven governance engine, traceability checks, commit trace checks | No CI provider integration in this phase | Rule execution and JSON reporting available; strict mode blocks required findings | Rule sprawl and schema drift |

### Delivery Scope
- Rule schema loader and stage-aware rule engine.
- Consistency, quality, and commit-trace checks.
- JSON output support for machine-readable governance evidence.
<!-- specflow8:feature:F-001:end -->

<!-- specflow8:feature:F-000:start -->
## [F-000] PR Gate and Root Governance Hardening
### Plan Record
| PlanID | Feature | RelatedSpec | Goal | Non-Goals | Exit Criteria | Risks |
|---|---|---|---|---|---|---|
| P-002 | F-000 | S-001 | Enforce PR template structure and sync root docs to real governance baseline | No external PR API integration in this phase | `PR_TEMPLATE_*` checks active, PR template upgraded, root docs reflect real governance history | Mismatch between template source and root files |

### Delivery Scope
- Add PR template checks to analyzer.
- Upgrade PR template to governance-strong structure.
- Replace placeholder root docs with governance-operational records.
<!-- specflow8:feature:F-000:end -->
