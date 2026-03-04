from __future__ import annotations

from datetime import date
from pathlib import Path

import typer

from specflow8.config import load_config
from specflow8.io_markdown import extract_feature_block, read_text
from specflow8.models import DecisionRecord
from specflow8.validators import parse_task_rows, validate_decision_record
from specflow8.workflow import ensure_docs, latest_feature_id, next_adr_id, upsert_doc_feature


def register(app: typer.Typer) -> None:
    @app.command("decide")
    def decide_command(
        title: str = typer.Option(..., "--title", help="Decision title."),
        context: str = typer.Option(..., "--context", help="Decision context."),
        choice: str = typer.Option(..., "--choice", help="Selected decision/choice."),
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

        adr_id = next_adr_id(root)
        tasks_block = extract_feature_block(read_text(root / "TASKS.md"), feature_id) or ""
        task_rows = parse_task_rows(tasks_block)
        related_tasks = ",".join(row["id"] for row in task_rows) if task_rows else "None"
        record = DecisionRecord(
            adr_id=adr_id,
            feature_id=feature_id,
            date=date.today(),
            context=context,
            decision=choice,
            alternatives="Keep current approach unchanged",
            consequences="Requires follow-up validation in tasks and state tracking",
            related_tasks=related_tasks,
            status="accepted",
            supersedes="None",
            verification="review:pending",
        )
        errors = validate_decision_record(record)
        if errors:
            raise typer.BadParameter("Decision validation failed: " + "; ".join(errors))

        body = f"""### Decision / 决策
- Title: {title}

| ADR-ID | Feature | Date | Context | Decision | Alternatives | Consequences | RelatedTasks | Status | Supersedes | Verification |
|---|---|---|---|---|---|---|---|---|---|---|
| {record.adr_id} | {record.feature_id} | {record.date.isoformat()} | {record.context} | {record.decision} | {record.alternatives} | {record.consequences} | {record.related_tasks} | {record.status} | {record.supersedes} | {record.verification} |
"""
        upsert_doc_feature(root, "DECISIONS.md", feature_id, title, body)
        typer.echo(f"Recorded decision {adr_id} for {feature_id}")
