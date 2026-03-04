from __future__ import annotations

from pathlib import Path

import typer

from specflow8.config import load_config
from specflow8.io_markdown import write_text
from specflow8.workflow import (
    ensure_docs,
    latest_feature_id,
    make_translator,
    normalize_language,
    render_template,
    today,
)


def register(app: typer.Typer) -> None:
    @app.command("checklist")
    def checklist_command(
        type: str = typer.Option(
            ...,
            "--type",
            help="Checklist type: requirements | readiness | ops",
            case_sensitive=False,
        ),
        feature: str | None = typer.Option(
            None, "--feature", help="Feature ID (defaults to latest)."
        ),
    ) -> None:
        allowed = {"requirements", "readiness", "ops"}
        if type not in allowed:
            raise typer.BadParameter("Checklist type must be requirements/readiness/ops.")

        root = Path(".").resolve()
        cfg = load_config(root)
        ensure_docs(root, cfg, cfg.language, cfg.docs_optional_enabled)
        feature_id = feature or latest_feature_id(root)
        if not feature_id:
            raise typer.BadParameter("No feature found. Run `specflow8 specify` first.")

        rel_template = f"checklists/{type}.md.j2"
        content = render_template(
            rel_template,
            {
                "feature_id": feature_id,
                "today": today(),
                "type": type,
                "language": normalize_language(cfg.language),
                "tr": make_translator(cfg.language),
            },
        )
        output = root / "checklists" / "specflow8" / feature_id / f"{type}.md"
        write_text(output, content)
        typer.echo(f"Checklist generated: {output}")
