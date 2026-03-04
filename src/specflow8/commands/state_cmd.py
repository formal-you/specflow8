from __future__ import annotations

from pathlib import Path

import typer

from specflow8.config import load_config
from specflow8.workflow import ensure_docs, latest_feature_id, today, upsert_doc_feature


def register(app: typer.Typer) -> None:
    @app.command("state")
    def state_command(
        snapshot: str = typer.Option(..., "--snapshot", help="Current status snapshot."),
        feature: str | None = typer.Option(
            None, "--feature", help="Feature ID (defaults to latest)."
        ),
    ) -> None:
        root = Path(".").resolve()
        cfg = load_config(root)
        ensure_docs(root, cfg, cfg.language, cfg.docs_optional_enabled)
        feature_id = feature or latest_feature_id(root)
        if not feature_id:
            raise typer.BadParameter("No feature found. Run `specflow8 specify` first.")

        body = f"""### Snapshot / 快照
- Date: {today()}
- Summary: {snapshot}

### Traceability / 追踪关系
- Tasks: see `{feature_id}` section in `TASKS.md`
- Decisions: see `{feature_id}` section in `DECISIONS.md`
"""
        upsert_doc_feature(root, "STATE.md", feature_id, "Execution State", body)
        typer.echo(f"Updated state snapshot for {feature_id}")
