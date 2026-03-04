# specflow8

`specflow8` 是一个面向 Spec-Driven 开发流程的 Python CLI。  
它把“需求-计划-任务-决策-提交”变成一条可验证、可审计的文档溯源链，而不是零散笔记。

如果你第一次接触这个项目，先看下面三步：

1. 安装：`uv tool install git+https://github.com/formal-you/specflow8.git`
2. 初始化：`specflow8 init --root . --lang bilingual`
3. 体验完整流程：`specify -> plan -> tasks -> decide -> analyze`

## 这个项目解决什么问题

很多团队有文档，但缺少“硬约束”：

- 需求、计划、任务、ADR 之间没有强关联
- 跨会话/跨人协作时上下文容易丢失
- 提交信息和文档变更之间不可追踪
- CI 中很难自动阻断治理违规

`specflow8` 提供了规则驱动的治理引擎（YAML 为真源），通过 `specflow8 analyze` 做一致性与可追溯性校验。

## 核心文档模型（8 文档）

`specflow8` 默认维护以下 8 个核心文档：

- `AGENTS.md`
- `README.md`
- `ARCHITECTURE.md`
- `DOMAIN.md`
- `STATE.md`
- `PLAN.md`
- `TASKS.md`
- `DECISIONS.md`

可选文档：

- `RUNBOOK.md`
- `INTERFACES.md`

每个 feature 采用标准标记块：

```md
<!-- specflow8:feature:F-001:start -->
... feature content ...
<!-- specflow8:feature:F-001:end -->
```

## 安装与依赖

前置要求：

- Python `>=3.11`
- Git（启用 commit trace 校验时必需）
- [uv](https://docs.astral.sh/uv/)

安装 CLI：

```bash
uv tool install git+https://github.com/formal-you/specflow8.git
```

升级：

```bash
uv tool upgrade specflow8
```

卸载：

```bash
uv tool uninstall specflow8
```

本地开发安装：

```bash
uv venv .venv
uv pip install -e ./tooling/specflow8
```

## 10 分钟快速上手

在一个新目录里执行：

```bash
# 1) 初始化文档与配置
specflow8 init --root . --lang bilingual --with-optional-docs

# 2) 环境体检（文档、规则 schema、引擎注册）
specflow8 check

# 3) 创建 feature 需求
specflow8 specify "Build a searchable task dashboard"

# 4) 写技术计划
specflow8 plan "Python + FastAPI, p95 < 200ms" --feature F-001

# 5) 生成任务队列（含新治理字段）
specflow8 tasks --feature F-001 --with-tests

# 6) 记录 ADR
specflow8 decide --title "Search strategy" --context "Need low latency search" --choice "Use full-text indexing" --feature F-001

# 7) 运行治理分析（建议默认）
specflow8 analyze --feature F-001 --mode transition
```

此时你会得到一条最小可用链路：

`Feature(F-001) -> Plan -> Tasks(T-xxx) -> ADR(ADR-xxx) -> Analyze Findings`

## 日常使用流程（推荐）

```bash
# 需求定义
specflow8 specify "<feature description>"

# 技术计划
specflow8 plan "<tech and constraints>" --feature F-XXX

# 任务拆解
specflow8 tasks --feature F-XXX --with-tests

# 决策记录
specflow8 decide --feature F-XXX --title "<title>" --context "<context>" --choice "<choice>"

# 状态快照
specflow8 state --feature F-XXX --snapshot "<current status>"

# 生成待办视图
specflow8 todo --feature F-XXX --stdout

# 生成子代理交接包
specflow8 handoff --stage tasks --feature F-XXX --shell powershell --stdout

# 治理分析（人读 + 机器读）
specflow8 analyze --feature F-XXX --mode transition
specflow8 analyze --feature F-XXX --mode strict --json

# 规范提交（建议每阶段完成后执行）
specflow8 commit --type gitflow --scope tasks --subject "tasks [F-XXX] 本轮对话完成内容" --body "stage: tasks; feature: F-XXX" --footer "Refs: F-XXX"
```

## 命令速查

- `init`：初始化文档、配置和 agent-kit 脚手架
- `check`：检查核心文档、规则 schema、规则引擎注册
- `specify`：创建 feature 需求块并生成澄清项
- `plan`：补充技术路径与约束
- `tasks`：生成可执行任务队列（含依赖）
- `decide`：记录 ADR 决策条目
- `state`：记录执行快照
- `todo`：从 TASKS 导出可读待办列表
- `handoff`：生成子代理交接文档与建议命令
- `analyze`：规则驱动治理分析（支持 JSON）
- `checklist`：生成检查清单
- `implement`：计算任务拓扑顺序并推进状态
- `commit`：按模板生成并执行规范提交

查看帮助：

```bash
specflow8 --help
specflow8 <command> --help
```

## 治理模式与退出语义

`analyze` 支持三种模式：

- `advisory`：以提示为主，适合探索阶段
- `transition`：迁移模式，默认推荐
- `strict`：关键治理项违规直接失败（非零退出）

常用参数：

```bash
specflow8 analyze --feature F-001 --mode transition
specflow8 analyze --all --mode advisory
specflow8 analyze --feature F-001 --mode strict --json --enforce-commit-trace
specflow8 analyze --feature F-001 --fail-on-warning
```

常见检查码示例：

- `TRACE_TARGET_NOT_FOUND`
- `TRACE_LINK_MISSING`
- `TASK_NO_ADR_OR_WAIVER`
- `FEATURE_NO_TASK_OR_REASON`
- `FEATURE_NO_ADR_OR_REASON`
- `COMMIT_TRACE_MISSING`
- `COMMIT_TEMPLATE_INVALID`
- `BOUNDARY_RULE_VIOLATION`

## 配置文件（specflow8.yaml）

初始化后可配置治理默认值：

```yaml
version: "0.1"
language: bilingual
docs_optional_enabled: false
clarification_limit: 3
governance_mode: transition
analyze:
  enforce_commit_trace: true
  git_log_depth: 100
```

说明：

- `governance_mode`：`analyze` 默认模式
- `enforce_commit_trace`：是否在 `analyze` 中校验提交痕迹
- `git_log_depth`：提交扫描深度

## Agent Kit（LLM/子代理协作）

`init` 默认生成以下资产：

- `.specflow8/templates/commands/*.md`
- `scripts/specflow8/bash/*.sh`
- `scripts/specflow8/powershell/*.ps1`

典型调用：

```bash
./scripts/specflow8/bash/create-new-feature.sh --json --description "Add SSO login" --tech "Python + FastAPI"
./scripts/specflow8/bash/setup-plan.sh --json --feature-id F-001
./scripts/specflow8/bash/check-prerequisites.sh --json --feature-id F-001 --include-tasks
```

语言控制：

- `--lang zh`：中文模板
- `--lang en`：英文模板
- `--lang bilingual`：双语模板
- `--force`：强制覆盖已有受管文档

## 常见问题

`specflow8 check` 失败怎么办？

- 先执行 `specflow8 init`
- 再执行 `specflow8 check`
- 若仍失败，按输出先修复 `RULE_SCHEMA_INVALID` 或缺失文件

`analyze` 报 `COMMIT_TRACE_MISSING`？

- 说明最近提交里没有可匹配该 feature 的提交痕迹
- 使用 `specflow8 commit` 按模板补充提交后重跑 `analyze`

`strict` 太严格影响迁移？

- 先用 `transition` 平滑迁移
- 逐步修复告警后切换到 `strict`

## 最小验收脚本

```bash
specflow8 init --root .
specflow8 check
specflow8 specify "Demo feature"
specflow8 plan "Python + FastAPI" --feature F-001
specflow8 tasks --feature F-001
specflow8 decide --feature F-001 --title "Demo ADR" --context "Need decision" --choice "Adopt option A"
specflow8 analyze --feature F-001 --mode transition
```
