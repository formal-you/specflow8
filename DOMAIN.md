# DOMAIN.md

## Document Meta / 文档元信息
- Owner: Product + Engineering / Owner: 产品 + 工程
- Last Updated: 2026-03-05
- Source of Truth: Domain knowledge and business rules / Source of Truth: 领域知识与业务规则
- Review Cadence: Monthly / Review Cadence: 每月
- Upstream/Downstream:
  - Upstream: README.md
  - Downstream: PLAN.md, TASKS.md

## Domain Scope / 领域范围
This project's business domain is "engineering governance as a product capability."  
本项目的业务领域是“把工程治理本身产品化”。

## Actors / 参与者
- Primary: maintainers operating specflow8 on active repositories.
- Secondary: reviewers validating governance evidence before merge.

## Glossary / 术语
| Term | Definition | Constraints |
|---|---|---|
| Spec-Driven Governance | Governance process managed by explicit spec/plan/task/ADR artifacts | Must be machine-checkable via analyzer |
| Commit Trace | Conventional commit evidence with stage/feature/Refs fields | Missing or malformed trace is blocking in strict mode |
| PR Gate | Required PR template fields and checklist compliance | Template integrity must pass `PR_TEMPLATE_*` checks |

<!-- specflow8:feature:F-001:start -->
## [F-001] Governance Core Domain Rules
### Business Rules
| RuleID | Description | Source | Related AC |
|---|---|---|---|
| BR-001 | Every governance change must map to a feature ID (`F-XXX`) across docs | Team governance policy | AC-001 |
| BR-002 | Trace references must point to existing targets (`F/T/ADR`) | Analyzer consistency rules | AC-002 |
| BR-003 | Commit evidence must be parseable and structured | Commit governance policy | AC-003 |
<!-- specflow8:feature:F-001:end -->

<!-- specflow8:feature:F-000:start -->
## [F-000] PR and Root-Doc Hardening Rules
### Business Rules
| RuleID | Description | Source | Related AC |
|---|---|---|---|
| BR-004 | PR must include mandatory trace, AC coverage, risk, rollback fields | PR governance policy | AC-003 |
| BR-005 | Root docs must represent current governance reality, not placeholders | Self-governance baseline | AC-003 |
| BR-006 | Template source and generated runtime docs must remain consistent | Maintainability requirement | AC-003 |
<!-- specflow8:feature:F-000:end -->

## Non-Goals / 非目标
- This document does not define implementation-level Python modules.
- This document does not contain daily progress logs (see `STATE.md`).
