# DECISIONS.md

## Document Meta / 文档元信息
- Owner: Engineering / Owner: 工程团队
- Last Updated: 2026-03-05
- Source of Truth: ADR-style decision records / Source of Truth: ADR 风格决策记录
- Review Cadence: Per major decision / Review Cadence: 每次关键决策
- Upstream/Downstream:
  - Upstream: PLAN.md, ARCHITECTURE.md
  - Downstream: TASKS.md, STATE.md

## ADR Triggers / ADR 触发条件
- Interface contract changes (API/Schema) / 接口契约变更（API/Schema）
- Data model or migration strategy changes / 数据模型或迁移策略调整
- Security/auth/compliance policy changes / 安全、鉴权、合规策略调整
- Changes impacting key non-functionals (performance/availability/cost) / 影响关键非功能指标（性能/可用性/成本）

## ADR Template (Required Fields) / ADR 模板（必填字段）
| ADR-ID | Feature | Date | Context | Decision | Alternatives | Consequences | RelatedTasks | Status | Supersedes | Verification |
|---|---|---|---|---|---|---|---|---|---|---|
| ADR-XXX | F-XXX | YYYY-MM-DD | Problem statement / 问题背景 | Chosen option / 选择方案 | Rejected options / 被拒绝方案 | Impact and follow-ups / 影响与后续 | T-XXX | proposed/accepted/superseded/rejected | ADR-XXX/None / None | Verification method / 验证方式 |

## Audit Requirements / 审计要求
- Every ADR must link to at least one task (`RelatedTasks`). / 每条 ADR 必须至少链接 1 个任务（`RelatedTasks`）。
- `Verification` must be reproducible (commands, logs, review records). / `Verification` 必须可复现（命令、日志、评审记录）。
- Superseded ADRs must declare lineage in `Supersedes`. / 被替代 ADR 必须在 `Supersedes` 中声明来源。
