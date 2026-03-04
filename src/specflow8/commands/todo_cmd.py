from __future__ import annotations

import json
from pathlib import Path

import typer

from specflow8.config import load_config
from specflow8.io_markdown import extract_feature_block, read_text, write_text
from specflow8.validators import parse_task_rows
from specflow8.workflow import ensure_docs, latest_feature_id, today


def _checkbox(status: str) -> str:
    return "[x]" if status == "done" else "[ ]"


def _status_suffix(status: str) -> str:
    if status == "todo":
        return ""
    return f" ({status})"


def register(app: typer.Typer) -> None:
    @app.command("todo")
    def todo_command(
        feature: str | None = typer.Option(
            None, "--feature", help="Feature ID (defaults to latest)."
        ),
        output: Path | None = typer.Option(
            None, "--output", help="Output markdown path for TODO list."
        ),
        stdout: bool = typer.Option(False, "--stdout", help="Print TODO markdown to stdout."),
        json_output: bool = typer.Option(False, "--json", help="Print result as JSON."),
    ) -> None:
        root = Path(".").resolve()
        cfg = load_config(root)
        ensure_docs(root, cfg, cfg.language, cfg.docs_optional_enabled)
        feature_id = feature or latest_feature_id(root)
        if not feature_id:
            raise typer.BadParameter("No feature found. Run `specflow8 specify` first.")

        tasks_text = read_text(root / "TASKS.md")
        block = extract_feature_block(tasks_text, feature_id)
        if not block:
            raise typer.BadParameter(
                f"No TASKS feature block found for {feature_id}. Run `specflow8 tasks --feature {feature_id}`."
            )
        body = block
        if body.startswith("## ["):
            body = "\n".join(body.splitlines()[1:]).strip()
        rows = parse_task_rows(body)
        if not rows:
            raise typer.BadParameter(
                f"No valid task rows found for {feature_id}. Populate TASKS.md first."
            )

        lines = [
            f"# TODO List: {feature_id}",
            f"",
            f"- Generated: {today()}",
            f"- Source: TASKS.md feature block `{feature_id}`",
            "",
        ]
        for row in rows:
            dep = f" | deps: {row['depends_on']}" if row["depends_on"] != "None" else ""
            due = f" | due: {row['due']}" if row["due"] != "None" else ""
            lines.append(
                f"- {_checkbox(row['status'])} {row['id']} {row['title']}{_status_suffix(row['status'])}{due}{dep}"
            )

        content = "\n".join(lines) + "\n"
        out_path = output or (root / ".specflow8" / "todos" / f"{feature_id}.md")
        write_text(out_path, content)

        if stdout:
            typer.echo(content)

        done_count = len([r for r in rows if r["status"] == "done"])
        payload = {
            "feature_id": feature_id,
            "output": str(out_path),
            "total": len(rows),
            "done": done_count,
            "pending": len(rows) - done_count,
        }
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False))
        else:
            typer.echo(
                f"TODO list generated: {out_path} (total={payload['total']}, done={payload['done']}, pending={payload['pending']})"
            )
