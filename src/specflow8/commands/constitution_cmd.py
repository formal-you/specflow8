from __future__ import annotations

from pathlib import Path

import typer

from specflow8.config import load_config
from specflow8.workflow import ensure_docs, upsert_constitution


def register(app: typer.Typer) -> None:
    @app.command("constitution")
    def constitution_command(
        principles: str = typer.Argument(..., help="Constitution principles text."),
        strict: bool = typer.Option(
            False, "--strict", help="Use blocking constitutional checks."
        ),
    ) -> None:
        root = Path(".").resolve()
        cfg = load_config(root)
        ensure_docs(root, cfg, cfg.language, cfg.docs_optional_enabled)
        upsert_constitution(root=root, principles=principles, strict=strict)
        typer.echo("Updated constitutional section in AGENTS.md")
