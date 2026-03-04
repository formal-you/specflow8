# STATE.md

## Document Meta / 文档元信息
- Owner: Engineering / Owner: 工程团队
- Last Updated: 2026-03-05
- Source of Truth: Current system snapshot / Source of Truth: 当前系统快照
- Review Cadence: Weekly / Review Cadence: 每周
- Upstream/Downstream:
  - Upstream: TASKS.md, DECISIONS.md
  - Downstream: PLAN.md reprioritization / Downstream: PLAN.md 优先级调整

## Snapshot / 快照
- Date: 2026-03-05
- Status: Initialized / Status: 已初始化

## State Template (Strict) / 状态模板（强约束）
- Feature: `F-XXX`
- Stage: `specify|plan|tasks|decide|implement|review`
- Owner:
- UpdatedAt: 2026-03-05

### Execution Status / 执行状态
| Item | Value | Evidence |
|---|---|---|
| Completed tasks / 完成任务 | `T-XXX,...` | Commit/log/report links / 提交/日志/报告链接 |
| Linked ADRs / 关联决策 | `ADR-XXX,...` | ADR entry links / ADR 条目链接 |
| Risk status / 风险状态 | low/medium/high / low/medium/high | Risk assessment evidence / 风险评估依据 |
| Rollback readiness / 回滚可用性 | ready/partial/not-ready / ready/partial/not-ready | Rollback drill/steps / 回滚演练/步骤 |

### Gate Results / 门禁结果
- Analyze: `specflow8 analyze --mode strict --enforce-commit-trace`
- Blocking findings / 阻塞项:
- Next actions / 下一步动作:
