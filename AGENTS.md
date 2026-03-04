# AGENTS.md

## Document Meta / 文档元信息
- Owner: Specflow8 Maintainers / Owner: Specflow8 维护者
- Last Updated: 2026-02-10
- Source of Truth: Agent constitution and document governance / Source of Truth: Agent 宪法与文档治理
- Review Cadence: Per milestone / Review Cadence: 每个里程碑
- Upstream/Downstream:
  - Upstream: Team collaboration policy / Upstream: 团队协作策略
  - Downstream: README.md, ARCHITECTURE.md, DOMAIN.md, STATE.md, PLAN.md, TASKS.md, DECISIONS.md

## Agent Constitution / Agent 宪法
- Keep document boundaries explicit. / 保持文档边界清晰。
- Keep cross-document traceability intact. / 保持跨文档可追踪性。
- Changes to architecture, tasks, and decisions must be linked. / 架构、任务、决策变更必须可关联。
- After each stage dialogue, execute a Conventional Commits style commit (`specflow8 commit`). / 每轮对话完成后必须执行 Conventional Commits 风格提交（`specflow8 commit`，如 feat/fix/docs/chore）。

## Document Index / 文档索引
- README.md
- ARCHITECTURE.md
- DOMAIN.md
- STATE.md
- PLAN.md
- TASKS.md
- DECISIONS.md

## Commit Message Template / 提交信息模板
```text
<type>(<scope>): <subject>

<body>

<footer>
```
