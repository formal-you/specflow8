from __future__ import annotations

import typer

from .commands import (
    analyze_cmd,
    checklist_cmd,
    check_cmd,
    commit_cmd,
    constitution_cmd,
    decide_cmd,
    handoff_cmd,
    implement_cmd,
    init_cmd,
    plan_cmd,
    specify_cmd,
    state_cmd,
    tasks_cmd,
    todo_cmd,
)

app = typer.Typer(
    help="Specflow8: spec-driven workflow toolkit for 8-document memory systems."
)

init_cmd.register(app)
constitution_cmd.register(app)
specify_cmd.register(app)
plan_cmd.register(app)
tasks_cmd.register(app)
decide_cmd.register(app)
state_cmd.register(app)
todo_cmd.register(app)
handoff_cmd.register(app)
analyze_cmd.register(app)
checklist_cmd.register(app)
implement_cmd.register(app)
commit_cmd.register(app)
check_cmd.register(app)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
