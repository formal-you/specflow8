# README.md

## Document Meta / 文档元信息
- Owner: Specflow8 Maintainers / Owner: Specflow8 维护者
- Last Updated: 2026-03-05
- Source of Truth: Project goals and navigation hub / Source of Truth: 项目目标与导航中心
- Review Cadence: Per milestone / Review Cadence: 每个里程碑
- Upstream/Downstream:
  - Upstream: AGENTS.md
  - Downstream: All project docs / Downstream: 所有项目文档

## System Goal / 系统目标
This repository follows a strong-governance workflow: every code change must be traceable, verifiable, and auditable. / 该仓库采用强约束治理流程：任何代码变更都必须具备可追踪、可验证、可审计证据。

## Governance Chain (Strict) / 治理链路（强约束）
`Spec -> Plan -> Task -> ADR -> Commit Trace -> PR Template`

## Minimum Required Trace Fields / 最小必填追踪字段
- Spec: `S-XXX` / Spec: `S-XXX`
- Plan: `P-XXX` (if applicable) / Plan: `P-XXX`（如有）
- Feature: `F-XXX`
- Task: `T-XXX`
- ADR: `ADR-XXX` (mandatory for architecture/interface/data/security changes) / （涉及架构/接口/数据/安全时必填）
- AC: `AC-XXX`

## Quickstart / 快速开始
1. Read AGENTS.md / 阅读 AGENTS.md
2. Run `specflow8 check` / 执行 `specflow8 check`
3. Run `specflow8 specify "<feature>"` / 执行 `specflow8 specify "<feature>"`
4. Run `specflow8 plan "<tech and constraints>"` / 执行 `specflow8 plan "<tech and constraints>"`
5. Run `specflow8 tasks` / 执行 `specflow8 tasks`
6. Run strict analysis: `specflow8 analyze --mode strict --enforce-commit-trace --fail-on-warning` / 执行严格分析：`specflow8 analyze --mode strict --enforce-commit-trace --fail-on-warning`
7. After each stage conversation, run a Conventional Commit with stage/feature/Refs fields / 每轮对话完成后执行 Conventional Commit（含 stage/feature/Refs 字段）
8. Complete all required fields in `.github/PULL_REQUEST_TEMPLATE.md` before opening PR / 提交前填写 `.github/PULL_REQUEST_TEMPLATE.md` 全部必填字段

## PR Merge Gates / PR 合入门槛
- [ ] Trace chain complete: Spec/Plan/Feature/Task/ADR/Commit/PR fully linked / 链路完整：Spec/Plan/Feature/Task/ADR/Commit/PR 全部可追踪
- [ ] AC coverage complete: every AC has evidence (tests/screenshots/logs) / AC 覆盖完整：逐条标注证据（测试/截图/日志）
- [ ] Risk and rollback plan is executable / 风险与回滚方案可执行
- [ ] `specflow8 analyze` has no blocking findings / `specflow8 analyze` 无阻塞项

## Subagent Workflow / 子代理工作流
- Todo export: `specflow8 todo --feature F-001` / 待办导出: `specflow8 todo --feature F-001`
- Handoff doc: `specflow8 handoff --stage tasks --feature F-001 --shell powershell` / 交接文档: `specflow8 handoff --stage tasks --feature F-001 --shell powershell`
- Stage final commit: `specflow8 commit --type docs --scope tasks --subject "tasks [F-001] 本轮对话完成内容" --body "stage: tasks; feature: F-001" --footer "Refs: F-001"` / 收尾提交: `specflow8 commit --type docs --scope tasks --subject "tasks [F-001] 本轮对话完成内容" --body "stage: tasks; feature: F-001" --footer "Refs: F-001"`
- Script entrypoints: `scripts/specflow8/*` (scaffolded by init) / 脚本入口: `scripts/specflow8/*`（由 init 自动生成）
