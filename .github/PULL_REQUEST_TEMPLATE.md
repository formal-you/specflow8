# Change Summary / 变更概述
One sentence for what this PR changes: / 一句话说明本 PR 做了什么：

## Trace Links (Required) / 关联链路（必填）
- Spec: S-XXX (link)
- Plan: P-XXX (link, if applicable)
- ADR: ADR-XXXX (link, required for architecture/interface/data/security decisions)
- Issue/Task: #XXX / T-XXX

## Traceability (System Validation Fields) / Traceability（系统校验字段）
- Feature IDs: F-XXX
- Related Plan: F-XXX
- Related Tasks: T-XXX
- Related ADR: ADR-XXX
- Stage: specify | plan | tasks | decide | implement | review

## Change Type / 变更类型
- [ ] Feature
- [ ] Bugfix
- [ ] Refactor
- [ ] Docs
- [ ] Chore/Build
- [ ] Breaking Change

## Change Details / 变更详情
- Major change 1: / 主要改动点 1：
- Major change 2: / 主要改动点 2：

## Acceptance Criteria Coverage (Required) / 验收标准覆盖（必填）
> Map each AC from Spec; if uncovered, explain reason and follow-up plan / 逐条对齐 Spec 的 AC；没有覆盖就说明原因与后续计划

- AC-001: implemented; evidence: test/screenshot/log link / 已实现；证据：测试/截图/日志链接
- AC-002: partially covered; reason: / 部分覆盖；原因：
- AC-003: not covered; reason and follow-up task: / 未覆盖；原因与后续任务：

## Testing and Verification / 测试与验证
- [ ] Unit
- [ ] Integration
- [ ] E2E
- [ ] Manual verification (document steps) / 手工验证（写步骤）
- [ ] specflow8 analyze --mode transition --enforce-commit-trace
- Key test commands/results: / 关键测试命令/结果：
  - `...`
- Evidence:
- Performance/security/regression notes: / 性能/安全/回归关注点：

## Risk Assessment and Rollback / 风险评估与回滚方案
- Risk:
- Monitoring/alerts: / 监控/告警项：
- Rollback:
  - [ ] direct commit rollback is possible / 可直接回滚提交
  - [ ] data rollback/compensation required (document scripts/steps) / 需要数据回滚/补偿（说明脚本/步骤）

## Impact / 影响范围（Impact）
- Impacted modules: / 影响模块：
- Config changes: / 配置变更：
- Data migration: / 数据迁移：
- Compatibility (breaking or not): / 兼容性（是否 breaking）：

## Reviewer Checklist / Reviewer Checklist（给审阅者）
- [ ] Spec/ADR references are complete / Spec/ADR 引用完整
- [ ] Change aligns with Spec scope (Non-Goals not accidentally implemented) / 变更与 Spec 范围一致（Non-Goals 未被误实现）
- [ ] AC coverage is sufficient and evidence is reproducible / AC 覆盖充分且证据可复现
- [ ] Risk and rollback plan is clear / 风险与回滚方案清晰
- [ ] Docs/changelog updated if needed / 文档/变更日志已更新（如需要）
