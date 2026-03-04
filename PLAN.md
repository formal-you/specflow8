# PLAN.md

## Document Meta / 文档元信息
- Owner: Engineering / Owner: 工程团队
- Last Updated: 2026-03-05
- Source of Truth: Milestone intent and phased planning / Source of Truth: 里程碑意图与分阶段计划
- Review Cadence: Per milestone / Review Cadence: 每个里程碑
- Upstream/Downstream:
  - Upstream: README.md, ARCHITECTURE.md, STATE.md
  - Downstream: TASKS.md

## Scope / 范围
Future intent only. No execution logs. / 仅记录未来计划，不记录执行日志。

## Plan Template (Strict) / 计划模板（强约束）
| PlanID | Feature | RelatedSpec | Goal | Non-Goals | Exit Criteria | Owner | Target Milestone | Risks |
|---|---|---|---|---|---|---|---|---|
| P-XXX | F-XXX | S-XXX | Milestone goal / 里程碑目标 | Explicit non-goals / 明确不做内容 | Verifiable exit criteria / 可验证退出条件 | Name/Role / 姓名/角色 | M-XXX/Date / 日期 | Top risks and mitigations / Top 风险及缓解 |

## Stage Gates / 阶段门禁
- specify -> plan: must include `S-XXX`, `F-XXX`, and initial AC list. / specify -> plan：必须有 `S-XXX`、`F-XXX`、初版 AC 列表。
- plan -> tasks: each deliverable must map to at least 1 task. / plan -> tasks：每个可执行输出必须映射到至少 1 个任务。
- tasks -> decide: ADR is mandatory for architecture/interface/data/security changes. / tasks -> decide：涉及架构/接口/数据/安全时必须产出 ADR。
- Before implementation, pass `specflow8 analyze --mode strict --enforce-commit-trace`. / 实现前必须通过 `specflow8 analyze --mode strict --enforce-commit-trace`。
