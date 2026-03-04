from __future__ import annotations

from pathlib import Path

import typer

from specflow8.config import load_config
from specflow8.constants import CORE_DOCS
from specflow8.rule_engine import checker_registry
from specflow8.rule_schema import load_rules
from specflow8.workflow import rule_root


def register(app: typer.Typer) -> None:
    @app.command("check")
    def check_command() -> None:
        root = Path(".").resolve()
        cfg = load_config(root)
        typer.echo(f"Config language: {cfg.language}")
        typer.echo(f"Governance mode: {cfg.governance_mode}")
        typer.echo(f"Clarification limit: {cfg.clarification_limit}")
        typer.echo(f"Commit trace enforce: {cfg.analyze.enforce_commit_trace}")
        typer.echo(f"Commit trace depth: {cfg.analyze.git_log_depth}")

        missing_docs = [doc for doc in CORE_DOCS if not (root / doc).exists()]
        if missing_docs:
            typer.echo("Missing core docs: " + ", ".join(missing_docs))
        else:
            typer.echo("Core docs: OK")

        rules, schema_errors = load_rules(rule_root())
        if schema_errors:
            for err in schema_errors:
                typer.echo(f"RULE_SCHEMA_INVALID | {err.file} | {err.message}")
        else:
            typer.echo(f"Rule schema: OK ({len(rules)} checks)")

        available_checkers = checker_registry()
        missing_checkers = sorted(
            {rule.checker for rule in rules if rule.checker not in available_checkers}
        )
        if missing_checkers:
            typer.echo(
                "Rule engine registry incomplete. Missing checkers: "
                + ", ".join(missing_checkers)
            )
        else:
            typer.echo("Rule engine registry: OK")

        if missing_docs or schema_errors or missing_checkers:
            raise typer.Exit(code=1)
        typer.echo("specflow8 check: PASS")
