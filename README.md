# README.md

## Document Meta / 文档元信息
- Owner: Specflow8 Maintainers / Owner: Specflow8 维护者
- Last Updated: 2026-03-05
- Source of Truth: Project goals and governance navigation / Source of Truth: 项目目标与治理导航
- Review Cadence: Per milestone / Review Cadence: 每个里程碑
- Upstream/Downstream:
  - Upstream: AGENTS.md
  - Downstream: ARCHITECTURE.md, DOMAIN.md, PLAN.md, TASKS.md, DECISIONS.md, STATE.md

## System Goal / 系统目标
Specflow8 is managed by its own Spec-Driven Governance workflow.  
Specflow8 以“自治理”方式运行：治理规则本身必须可追踪、可验证、可审计。

## Governance Chain (Enforced) / 治理链路（强制执行）
`Spec -> Plan -> Task -> ADR -> Commit Trace -> PR Template`

## Operating Mode / 当前运行模式
- Rule engine supports `advisory | transition | strict`.
- Merge gate policy: run `specflow8 analyze --mode strict --enforce-commit-trace`.
- Default local config may remain `transition`, but PR acceptance uses strict output.

## Feature Registry / 特性治理台账
| Feature | Spec | Plan | Status | Primary Evidence |
|---|---|---|---|---|
| F-001 | S-001 | P-001 | done | `11cb7e7`, `03c0b2b` |
| F-000 | S-001 | P-002 | done | `518468f`, `8fdde03`, `0a9258e`, `3ab43bd` |

## Merge Gates / 合入门禁
- [ ] Spec/Plan/Task/ADR/Commit/PR trace chain complete.
- [ ] Every AC has reproducible evidence.
- [ ] Risk and rollback plan is concrete and executable.
- [ ] `specflow8 analyze` has no blocking findings in strict mode.

## Governance Command Set / 治理命令集
1. `specflow8 check`
2. `specflow8 specify "<feature>"`
3. `specflow8 plan --feature F-XXX "<tech and constraints>"`
4. `specflow8 tasks --feature F-XXX`
5. `specflow8 decide --feature F-XXX ...`
6. `specflow8 state --feature F-XXX --snapshot "..."`
7. `specflow8 analyze --mode strict --all --enforce-commit-trace`
8. `specflow8 commit --type <type> --scope <scope> --subject "<subject>" --body "stage: <stage>; feature: F-XXX" --footer "Refs: F-XXX"`

## Governance Evidence Timeline / 治理证据时间线
| Date | Commit | Event |
|---|---|---|
| 2026-03-05 | `11cb7e7` | Introduced YAML-driven governance engine and traceability checks. |
| 2026-03-05 | `03c0b2b` | Adopted Conventional Commit trace format for stage governance. |
| 2026-03-05 | `518468f` | Added PR template governance checks (`PR_TEMPLATE_*`). |
| 2026-03-05 | `8fdde03` | Strengthened core template governance constraints. |
| 2026-03-05 | `0a9258e` | Upgraded PR template to strong-governance structure. |
| 2026-03-05 | `3ab43bd` | Refreshed root docs for project self-governance. |

<!-- specflow8:feature:F-001:start -->
## [F-001] YAML Governance Engine and Commit Trace
### Summary / 概述
- Goal: establish rule-driven governance with cross-document traceability.
- Delivered: rule schema/engine, consistency and quality rules, commit trace checks.

### Acceptance Criteria / 验收标准
- AC-001: governance checks are YAML-driven and executable (`11cb7e7`).
- AC-002: trace links validate `F/T/ADR` integrity (`11cb7e7`).
- AC-003: commit evidence follows Conventional Commit + stage/feature/Refs (`03c0b2b`).
<!-- specflow8:feature:F-001:end -->

<!-- specflow8:feature:F-000:start -->
## [F-000] Governance Hardening for Project Self-Management
### Summary / 概述
- Goal: move from partial chain to full PR-enforced governance loop.
- Delivered: PR template checks, stronger templates, root docs synchronized.

### Acceptance Criteria / 验收标准
- AC-001: PR template exists and is governed by analyzer (`518468f`).
- AC-002: core templates enforce stricter governance structure (`8fdde03`).
- AC-003: repository root docs switched from placeholders to governance baseline (`3ab43bd` and current update).
<!-- specflow8:feature:F-000:end -->
