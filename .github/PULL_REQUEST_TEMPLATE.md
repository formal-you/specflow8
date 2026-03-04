# 变更概述
一句话说明本 PR 做了什么：

## 关联链路（必填）
- Spec：S-XXX（链接）
- Plan：P-XXX（链接，如有）
- ADR：ADR-XXXX（链接，如有；涉及架构/接口/数据/安全决策时必填）
- Issue/Task：#XXX / T-XXX

## Traceability（系统校验字段）
- Feature IDs: F-XXX
- Related Plan: F-XXX
- Related Tasks: T-XXX
- Related ADR: ADR-XXX
- Stage: specify | plan | tasks | decide | implement | review

## 变更类型
- [ ] Feature
- [ ] Bugfix
- [ ] Refactor
- [ ] Docs
- [ ] Chore/Build
- [ ] Breaking Change

## 变更详情
- 主要改动点 1：
- 主要改动点 2：

## 验收标准覆盖（必填）
> 逐条对齐 Spec 的 AC；没有覆盖就说明原因与后续计划

- AC-001：✅ 已实现；证据：测试/截图/日志链接
- AC-002：🟨 部分覆盖；原因：
- AC-003：❌ 未覆盖；原因 & 后续任务：

## 测试与验证
- [ ] Unit
- [ ] Integration
- [ ] E2E
- [ ] 手工验证（写步骤）
- [ ] specflow8 analyze --mode transition --enforce-commit-trace
- 关键测试命令/结果：
  - `...`
- Evidence:
- 性能/安全/回归关注点：

## 风险评估 & 回滚方案
- Risk:
- 监控/告警项：
- Rollback:
  - [ ] 可直接回滚提交
  - [ ] 需要数据回滚/补偿（说明脚本/步骤）

## 影响范围（Impact）
- 影响模块：
- 配置变更：
- 数据迁移：
- 兼容性（是否 breaking）：

## Reviewer Checklist（给审阅者）
- [ ] Spec/ADR 引用完整
- [ ] 变更与 Spec 范围一致（Non-Goals 未被误实现）
- [ ] AC 覆盖充分且证据可复现
- [ ] 风险与回滚方案清晰
- [ ] 文档/变更日志已更新（如需要）
