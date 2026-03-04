from __future__ import annotations

from pathlib import Path

import typer

from specflow8.config import load_config
from specflow8.constants import CORE_DOCS
from specflow8.workflow import rule_root


def register(app: typer.Typer) -> None:
    @app.command("check")
    def check_command() -> None:
        root = Path(".").resolve()
        cfg = load_config(root)
        typer.echo(f"Config language: {cfg.language}")
        typer.echo(f"Clarification limit: {cfg.clarification_limit}")

        missing = [doc for doc in CORE_DOCS if not (root / doc).exists()]
        if missing:
            typer.echo("Missing core docs: " + ", ".join(missing))
        else:
            typer.echo("Core docs: OK")

        rules = ["boundary_rules.yaml", "consistency_rules.yaml", "quality_gates.yaml"]
        missing_rules = [x for x in rules if not (rule_root() / x).exists()]
        if missing_rules:
            typer.echo("Missing rule files: " + ", ".join(missing_rules))
        else:
            typer.echo("Rules: OK")

        if missing or missing_rules:
            raise typer.Exit(code=1)
        typer.echo("specflow8 check: PASS")
