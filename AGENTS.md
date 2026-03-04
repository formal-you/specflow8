# AGENTS.md

## Document Meta / 文档元信息
- Owner: Specflow8 Maintainers / Owner: Specflow8 维护者
- Last Updated: 2026-03-05
- Source of Truth: Agent constitution and document governance / Source of Truth: Agent 宪法与文档治理
- Review Cadence: Per milestone / Review Cadence: 每个里程碑
- Upstream/Downstream:
  - Upstream: Team collaboration policy / Upstream: 团队协作策略
  - Downstream: README.md, ARCHITECTURE.md, DOMAIN.md, STATE.md, PLAN.md, TASKS.md, DECISIONS.md, .github/PULL_REQUEST_TEMPLATE.md

## Agent Constitution / Agent 宪法
- Keep document boundaries explicit; no cross-document responsibility drift. / 保持文档边界清晰，禁止跨文档职责漂移。
- Keep cross-document traceability intact; every change must be traceable from Spec to PR. / 保持跨文档可追踪性，任何变更必须可从 Spec 追溯到 PR。
- Changes to architecture, tasks, and decisions must be bi-directionally linked (Feature/Task/ADR). / 架构、任务、决策变更必须双向链接（Feature/Task/ADR）。
- After each stage dialogue, execute a Conventional Commits style commit (`specflow8 commit`, e.g. feat/fix/docs/chore). / 每轮对话完成后必须执行 Conventional Commits 风格提交（`specflow8 commit`，如 feat/fix/docs/chore）。
- Never mark work done without evidence; Evidence/Verification fields must not be empty. / 严禁在无证据情况下标记完成；Evidence/Verification 字段不可留空。

## Governance Gates / 治理门禁
| Gate | Trigger | Required Evidence | Blocking Rule |
|---|---|---|---|
| Traceability / Traceability | Any feature change / 任意 feature 变更 | `F-XXX` + `RelatedPlan` + `RelatedADR/waiver` | TRACE_LINK_MISSING / TRACE_TARGET_NOT_FOUND |
| Quality / Quality | `tasks/decide/implement` | Evidence + Verification + checklist output | TASK_NO_ADR_OR_WAIVER / CLARIFICATION_LIMIT_EXCEEDED |
| Commit Trace / Commit Trace | Before commit / 提交前 | Conventional Commit + `stage/feature/Refs` | COMMIT_TRACE_MISSING / COMMIT_TEMPLATE_INVALID |
| PR Gate / PR Gate | Before opening PR / 发起 PR 前 | `.github/PULL_REQUEST_TEMPLATE.md` 完整字段 | PR_TEMPLATE_MISSING / PR_TEMPLATE_FIELD_MISSING |

## Document Index / 文档索引
- README.md
- ARCHITECTURE.md
- DOMAIN.md
- STATE.md
- PLAN.md
- TASKS.md
- DECISIONS.md
- .github/PULL_REQUEST_TEMPLATE.md

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

stage: <specify|plan|tasks|decide|implement|review>
feature: F-XXX

Refs: F-XXX[, T-XXX, ADR-XXX]
```
