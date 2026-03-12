# AGENTS.md

## Document Meta / 文档元信息
- Owner: Specflow8 Maintainers / Owner: Specflow8 维护者
- Last Updated: 2026-03-05
- Source of Truth: Agent constitution and document governance / Source of Truth: Agent 宪法与文档治理
- Review Cadence: Per milestone / Review Cadence: 每个里程碑
- Upstream/Downstream:
  - Upstream: Team collaboration policy / Upstream: 团队协作策略
  - Downstream: README.md, ARCHITECTURE.md, DOMAIN.md, STATE.md, PLAN.md, TASKS.md, DECISIONS.md, .github/PULL_REQUEST_TEMPLATE.md

## Active Constitution / 当前生效宪法
- Document boundary is enforced by rule engine (`BOUNDARY_RULE_VIOLATION`). / 文档边界由规则引擎强制约束（`BOUNDARY_RULE_VIOLATION`）。
- Cross-document trace is mandatory (`F/T/ADR` linkage). / 跨文档追踪强制要求（`F/T/ADR` 链接）。
- Governance checks run before merge in strict mode. / 合并前治理检查以 strict 模式执行。
- Stage-level commit trace is mandatory for each governance step. / 每个治理阶段必须留下提交痕迹。
- Evidence-first: no done status without reproducible evidence. / 证据优先：无可复现证据不得标记完成。

## Real Governance Baseline / 真实治理基线
- Primary governance spec: `S-001` (Spec-Driven Governance for Specflow8 self-management).
- Implemented plans:
  - `P-001` for `F-001`: YAML governance engine and commit trace.
  - `P-002` for `F-000`: PR-template gate and strict doc governance hardening.
- Rule-backed gates in production use:
  - `TRACE_LINK_MISSING`, `TRACE_TARGET_NOT_FOUND`
  - `TASK_NO_ADR_OR_WAIVER`, `TASK_DEP_CYCLE`
  - `COMMIT_TRACE_MISSING`, `COMMIT_TEMPLATE_INVALID`
  - `PR_TEMPLATE_MISSING`, `PR_TEMPLATE_FIELD_MISSING`

## Governance Evidence (Git) / 治理证据（Git）
| Date | Commit | Governance Event |
|---|---|---|
| 2026-03-05 | `11cb7e7` | YAML-driven governance engine and traceability foundation (`F-001`). |
| 2026-03-05 | `03c0b2b` | Conventional commit standard adopted with stage/feature/Refs fields (`F-001`). |
| 2026-03-05 | `518468f` | PR template traceability checks added (`F-000`). |
| 2026-03-05 | `8fdde03` | Core templates strengthened for strict governance (`F-000`). |
| 2026-03-05 | `0a9258e` | PR template upgraded to strong governance format (`F-000`). |
| 2026-03-05 | `3ab43bd` | Root docs refreshed for project self-governance (`F-000`). |

## Document Boundaries / 文档边界
- `README.md`: governance chain, process entry, merge gates.
- `ARCHITECTURE.md`: architecture and technical decision context only.
- `DOMAIN.md`: business semantics/rules only, no implementation detail.
- `PLAN.md`: phased intent and milestones only.
- `TASKS.md`: executable backlog with evidence and DoD.
- `DECISIONS.md`: ADR records with verification and lineage.
- `STATE.md`: current snapshot and gate outcomes.
- `.github/PULL_REQUEST_TEMPLATE.md`: PR-level enforcement checklist.

## ID Conventions / ID 规范
- Spec: `S-XXX`
- Plan: `P-XXX`
- Feature: `F-XXX`
- Task: `T-XXX`
- ADR: `ADR-XXX`
- AC: `AC-XXX`

## Commit Message Template / 提交信息模板
```text
<type>(<scope>): <subject>

stage: <specify|plan|tasks|decide|implement|review|governance|constitution>
feature: F-XXX

Refs: F-XXX[, T-XXX, ADR-XXX]
```
