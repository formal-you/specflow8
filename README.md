# specflow8

Specflow8 is a Python CLI toolkit inspired by spec-driven workflows and adapted to an 8-document memory system:

- `AGENTS.md`
- `README.md`
- `ARCHITECTURE.md`
- `DOMAIN.md`
- `STATE.md`
- `PLAN.md`
- `TASKS.md`
- `DECISIONS.md`

Optional extensions:

- `RUNBOOK.md`
- `INTERFACES.md`

## Install

```bash
uv tool install git+https://github.com/formal-you/specflow8.git
```

Upgrade:

```bash
uv tool upgrade specflow8
```

Uninstall:

```bash
uv tool uninstall specflow8
```

For local development:

```bash
uv venv .venv
uv pip install -e ./tooling/specflow8
```

## Why uv

- Use one toolchain for environment, dependency, and CLI tool management.
- Faster installation and reproducible behavior across machines.
- No separate global-tool manager is required for this project.

## Commands

```bash
specflow8 --help
specflow8 <command> --help
```

Basic usage for each command:

```bash
# 1) initialize docs/config
specflow8 init --root . --lang bilingual --with-optional-docs

# 2) update constitution in AGENTS.md
specflow8 constitution "Security first; test before merge"

# 3) create feature spec block
specflow8 specify "Build a searchable task dashboard"

# 4) add technical plan
specflow8 plan "Python + FastAPI, p95 < 200ms" --feature F-001

# 5) generate task queue
specflow8 tasks --feature F-001 --with-tests

# 6) record ADR
specflow8 decide --title "Search strategy" --context "Need low latency search" --choice "Use full-text indexing" --feature F-001

# 7) update execution state snapshot
specflow8 state --snapshot "Planning and task generation completed" --feature F-001

# 8) export TODO markdown
specflow8 todo --feature F-001 --stdout

# 9) create subagent handoff package
specflow8 handoff --stage tasks --feature F-001 --shell powershell --stdout

# 10) run consistency/quality analysis
specflow8 analyze --feature F-001
specflow8 analyze --all

# 11) generate checklist file
specflow8 checklist --type readiness --feature F-001

# 12) derive implementation order from TASKS.md
specflow8 implement --feature F-001 --dry-run

# 13) preview commit message (template fields are required)
specflow8 commit --type feat --scope cli --subject "document command usage" --body "validated CLI behavior" --footer "Refs: F-001" --dry-run

# 13b) create commit
specflow8 commit --type feat --scope cli --subject "document command usage" --body "validated CLI behavior" --footer "Refs: F-001"

# 14) environment sanity check
specflow8 check
```

## Agent Kit (spec-kit style)

`specflow8 init` will scaffold command templates and scripts by default:

- `.specflow8/templates/commands/*.md`
- `scripts/specflow8/bash/*.sh`
- `scripts/specflow8/powershell/*.ps1`

These are designed for LLM/subagent orchestration where scripts provide JSON runtime context.

Examples:

```bash
./scripts/specflow8/bash/create-new-feature.sh --json --description "Add SSO login" --tech "Python + FastAPI"
./scripts/specflow8/bash/setup-plan.sh --json --feature-id F-001
./scripts/specflow8/bash/check-prerequisites.sh --json --feature-id F-001 --include-tasks
```

Language output:

- `--lang zh`: fully Chinese templates
- `--lang en`: fully English templates
- `--lang bilingual`: bilingual templates
- `--force`: overwrite existing managed docs with the selected language templates

## CLI Smoke Test Notes (2026-02-10)

The following sequence was tested in a temporary directory:

```bash
specflow8 init -> check -> specify -> plan -> tasks -> decide -> state -> todo -> handoff -> analyze -> checklist -> implement -> commit
```

Verified behavior:

- All commands above execute successfully with the documented minimum parameters.
- `specflow8 check` fails before initialization (missing core docs), and passes after `specflow8 init`.
- `specflow8 todo --stdout` and `specflow8 handoff --stdout` print content and still write files to default output paths.

Observed mismatches (actual vs expectation):

- None in this smoke run.
