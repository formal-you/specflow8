from __future__ import annotations

from pathlib import Path

import typer

from specflow8.config import load_config
from specflow8.io_markdown import extract_feature_block, read_text, upsert_feature_block, write_text
from specflow8.validators import dependency_cycle, parse_task_rows, topological_order
from specflow8.workflow import ensure_docs, latest_feature_id, today, upsert_doc_feature


def _update_task_status(block: str, task_id: str, status: str) -> str:
    updated: list[str] = []
    for line in block.splitlines():
        text = line.strip()
        if not (text.startswith("|") and text.endswith("|")):
            updated.append(line)
            continue
        cells = [item.strip() for item in text.strip("|").split("|")]
        if not cells or cells[0] != task_id:
            updated.append(line)
            continue
        # Legacy table status index is 3, new table status index is 4.
        status_idx = 4 if len(cells) >= 13 else 3
        if status_idx < len(cells):
            cells[status_idx] = status
            updated.append("| " + " | ".join(cells) + " |")
        else:
            updated.append(line)
    return "\n".join(updated)


def register(app: typer.Typer) -> None:
    @app.command("implement")
    def implement_command(
        feature: str | None = typer.Option(
            None, "--feature", help="Feature ID (defaults to latest)."
        ),
        dry_run: bool = typer.Option(
            False, "--dry-run", help="Only report execution order and blockers."
        ),
    ) -> None:
        root = Path(".").resolve()
        cfg = load_config(root)
        ensure_docs(root, cfg, cfg.language, cfg.docs_optional_enabled)
        feature_id = feature or latest_feature_id(root)
        if not feature_id:
            raise typer.BadParameter("No feature found. Run `specflow8 specify` first.")

        tasks_path = root / "TASKS.md"
        tasks_text = read_text(tasks_path)
        feature_block = extract_feature_block(tasks_text, feature_id)
        if not feature_block:
            raise typer.BadParameter(
                f"No TASKS.md feature block found for {feature_id}. Run `specflow8 tasks` first."
            )
        block_body = feature_block
        if block_body.startswith("## ["):
            block_body = "\n".join(block_body.splitlines()[1:]).strip()

        rows = parse_task_rows(block_body)
        if not rows:
            raise typer.BadParameter("No valid task rows found for the selected feature.")

        cycles = dependency_cycle(rows)
        if cycles:
            typer.echo(f"Blocked by dependency cycle: {', '.join(cycles)}")
            raise typer.Exit(code=1)

        order = topological_order(rows)
        typer.echo(f"Execution order for {feature_id}:")
        for idx, task_id in enumerate(order, start=1):
            typer.echo(f"{idx}. {task_id}")

        blockers = [r["id"] for r in rows if r["status"] == "blocked"]
        if blockers:
            typer.echo("Blocked tasks: " + ", ".join(blockers))

        if dry_run:
            typer.echo("Dry-run complete. No files were modified.")
            raise typer.Exit(code=0)

        first_todo = next((r["id"] for r in rows if r["status"] == "todo"), None)
        if first_todo:
            updated_block = _update_task_status(block_body, first_todo, "in_progress")
            updated_text = upsert_feature_block(
                tasks_text, feature_id, "Execution Tasks", updated_block
            )
            write_text(tasks_path, updated_text)

        state_body = f"""### Implementation Execution / 执行驱动
- Date: {today()}
- Mode: workflow-driven (no direct business code mutation)
- Ordered tasks: {", ".join(order)}
- Next active task: {first_todo or "None"}
"""
        upsert_doc_feature(root, "STATE.md", feature_id, "Execution State", state_body)
        typer.echo("Implementation workflow state updated in TASKS.md and STATE.md")
