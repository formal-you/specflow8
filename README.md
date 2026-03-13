# Specflow8

Specflow8 is a spec-driven workflow toolkit for software teams that want to manage requirements, plans, tasks, decisions, and governance in a consistent document-first way.

## What It Does / 作用

Specflow8 helps a repository maintain a lightweight engineering memory system around a feature lifecycle:

- `specify`: capture the feature intent and open questions
- `plan`: record technical direction and constraints
- `tasks`: generate an executable task queue
- `decide`: write ADR-style decisions
- `state`: snapshot current progress
- `analyze`: validate traceability and governance quality
- `commit`: create structured commit messages aligned with the workflow

The tool is designed for teams that want a repeatable path from idea to implementation without scattering context across chats, tickets, and ad hoc notes.

## Purpose / 目的

The project exists to solve three common problems:

1. Requirements, plans, and implementation decisions are often disconnected.
2. Important context is easy to lose during handoff or long-running work.
3. Governance checks are usually informal, manual, and hard to audit.

Specflow8 turns those steps into a CLI workflow backed by versioned Markdown documents and rule-based checks, so teams can keep context close to the codebase.

## Key Features

- Document-first workflow built around repository-local Markdown files
- Three governance profiles: `small`, `medium`, `large`
- Rule-driven analysis with `advisory`, `transition`, and `strict` modes
- Traceability checks across feature IDs, tasks, ADRs, commits, and PR templates
- Built-in templates for docs, checklists, and agent handoff assets
- CLI designed for both local use and automation-friendly output

## Requirements

- Python `>= 3.11`
- Git recommended for commit-trace and PR-governance workflows

## Download And Install / 下载与安装

### Option 1: install from source with `pip`

```bash
git clone https://github.com/formal-you/specflow8.git
cd specflow8
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
pip install -e .[dev]
```

macOS / Linux:

```bash
source .venv/bin/activate
pip install -e .[dev]
```

### Option 2: use `uv`

```bash
git clone https://github.com/formal-you/specflow8.git
cd specflow8
uv sync --dev
```

After installation, verify the CLI:

```bash
specflow8 --help
```

## Quick Start / 基本使用

Initialize a repository:

```bash
specflow8 init --root . --scale medium --type monolith
```

Create your first feature:

```bash
specflow8 specify "Build searchable dashboard"
```

Add a technical plan:

```bash
specflow8 plan --feature F-001 "Python + FastAPI"
```

Generate tasks:

```bash
specflow8 tasks --feature F-001 --with-tests
```

Record a decision:

```bash
specflow8 decide --feature F-001 --title "Use API-first" --context "Need stable contracts" --choice "Adopt API-first design"
```

Run governance checks:

```bash
specflow8 analyze --feature F-001 --mode strict --enforce-commit-trace
```

## Basic Workflow / 使用流程

1. Run `specflow8 init` to scaffold docs and config.
2. Use `specflow8 specify` when a new feature or change starts.
3. Use `specflow8 plan` to capture the technical approach.
4. Use `specflow8 tasks` to create the execution backlog.
5. Use `specflow8 decide` for architecture or policy decisions.
6. Use `specflow8 state` and `specflow8 implement` during execution.
7. Run `specflow8 analyze` before review or merge.

## Generated Project Artifacts

Depending on the selected profile, Specflow8 manages a set of repository documents such as:

- `README.md`
- `ARCHITECTURE.md`
- `DOMAIN.md`
- `PLAN.md`
- `TASKS.md`
- `DECISIONS.md`
- `STATE.md`
- `AGENTS.md`
- `.github/PULL_REQUEST_TEMPLATE.md`

Larger profiles can also include `SPECS.md` and stricter governance checks.

## Governance Profiles

- `small`: lighter governance, fewer mandatory controls, good for smaller teams
- `medium`: balanced default for most projects
- `large`: strongest traceability and governance enforcement

You can inspect or change the profile later:

```bash
specflow8 profile show
specflow8 profile list
specflow8 profile upgrade --scale large
```

## Development / 开发

Run tests:

```bash
python -m pytest -q
```

The CLI entry point is defined in [`pyproject.toml`](pyproject.toml), and the main app is registered in [`src/specflow8/cli.py`](src/specflow8/cli.py).

## Contributing

Issues and pull requests are welcome. A good contribution should:

- explain the problem or change clearly
- include reproducible validation when behavior changes
- keep documentation and CLI behavior aligned
- pass the local test suite before submission

## License

This project is released under the MIT License. See [`LICENSE`](LICENSE).

## Project Governance

Specflow8 also uses its own spec-driven governance model internally. If you want the deeper project records behind the CLI workflow, see:

- [`AGENTS.md`](AGENTS.md)
- [`ARCHITECTURE.md`](ARCHITECTURE.md)
- [`PLAN.md`](PLAN.md)
- [`TASKS.md`](TASKS.md)
- [`DECISIONS.md`](DECISIONS.md)
