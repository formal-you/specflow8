# TASKS.md

## Document Meta / 文档元信息
- Owner: Engineering / Owner: 工程团队
- Last Updated: 2026-03-05
- Source of Truth: Executable task queue / Source of Truth: 可执行任务队列
- Review Cadence: Weekly / Review Cadence: 每周
- Upstream/Downstream:
  - Upstream: PLAN.md, STATE.md
  - Downstream: STATE.md

## Task Governance Constraints / 任务治理约束
- Each task must include: `ID`, `Feature`, `RelatedPlan`, `Evidence`, and `DoD`. / 每条任务必须包含：`ID`、`Feature`、`RelatedPlan`、`Evidence`、`DoD`。
- If `RelatedADR` is empty, `WaiverReason` is mandatory. / `RelatedADR` 为空时必须填写 `WaiverReason`。
- `DependsOn` only allows `T-XXX` or `None`, and must not form cycles. / `DependsOn` 仅允许 `T-XXX` 或 `None`，不得形成环。
- Status flow allowed only: `todo -> in_progress -> done` (or `blocked`). / 状态流转仅允许：`todo -> in_progress -> done`（或 `blocked`）。

## Task Template (Required Fields) / 任务模板（必填字段）
| ID | Feature | Title | Priority | Status | Owner | Due | DependsOn | RelatedPlan | RelatedADR | Evidence | DoD | WaiverReason |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T-XXX | F-XXX | Short task title / 简短任务标题 | P0/P1/P2 | todo/in_progress/done/blocked | Name/Role / 姓名/角色 | YYYY-MM-DD | Task IDs or None / 任务 ID 或 None | F-XXX | ADR-XXX/None / None | Verifiable evidence / 可验证证据 | Verifiable completion statement / 可验证的完成标准 | Waiver reason or None / 原因或 None |

## AC Mapping Template / AC 映射模板
| AC-ID | RelatedTasks | Evidence |
|---|---|---|
| AC-001 | T-XXX,T-YYY | Test report/log/screenshot link / 测试报告/日志/截图链接 |
