from __future__ import annotations

from datetime import date
from pathlib import Path

import typer

from specflow8.config import load_config
from specflow8.models import TaskRecord
from specflow8.validators import parse_task_rows, validate_task_record
from specflow8.workflow import (
    default_due,
    ensure_docs,
    latest_feature_id,
    next_task_id,
    upsert_doc_feature,
)


def _build_row(task: TaskRecord) -> str:
    due = task.due.isoformat() if isinstance(task.due, date) else "None"
    deps = ",".join(task.depends_on) if task.depends_on else "None"
    return (
        f"| {task.id} | {task.feature_id} | {task.title} | {task.priority} | {task.status} | "
        f"{task.owner} | {due} | {deps} | {task.related_plan} | {task.related_adr} | "
        f"{task.evidence} | {task.dod} | {task.waiver_reason} |"
    )


def register(app: typer.Typer) -> None:
    @app.command("tasks")
    def tasks_command(
        feature: str | None = typer.Option(
            None, "--feature", help="Feature ID (defaults to latest)."
        ),
        with_tests: bool = typer.Option(
            False,
            "--with-tests",
            help="Include baseline test tasks in generated queue.",
        ),
    ) -> None:
        root = Path(".").resolve()
        cfg = load_config(root)
        ensure_docs(root, cfg, cfg.language, cfg.docs_optional_enabled)
        feature_id = feature or latest_feature_id(root)
        if not feature_id:
            raise typer.BadParameter("No feature found. Run `specflow8 specify` first.")

        tasks_md = (root / "TASKS.md").read_text(encoding="utf-8")
        existing = parse_task_rows(tasks_md)
        n = next_task_id(existing)

        generated: list[TaskRecord] = []
        generated.append(
            TaskRecord(
                id=f"T-{n:03d}",
                feature_id=feature_id,
                title="Define concrete architecture slice for this feature",
                priority="P1",
                status="todo",
                owner="Maintainer",
                due=default_due(5),
                depends_on=[],
                related_plan=feature_id,
                related_adr="None",
                evidence="pending: architecture slice review",
                dod="ARCHITECTURE.md feature section updated and reviewed",
                waiver_reason="ADR pending during initial task generation",
            )
        )
        n += 1
        generated.append(
            TaskRecord(
                id=f"T-{n:03d}",
                feature_id=feature_id,
                title="Generate implementation-ready contracts and boundaries",
                priority="P1",
                status="todo",
                owner="Maintainer",
                due=default_due(7),
                depends_on=[generated[0].id],
                related_plan=feature_id,
                related_adr="None",
                evidence="pending: contract review checklist",
                dod="Contract assumptions and interfaces captured in feature sections",
                waiver_reason="ADR pending during initial task generation",
            )
        )
        n += 1
        if with_tests:
            generated.append(
                TaskRecord(
                    id=f"T-{n:03d}",
                    feature_id=feature_id,
                    title="Add test scenarios for main user flow",
                    priority="P1",
                    status="todo",
                    owner="Maintainer",
                    due=default_due(8),
                    depends_on=[generated[-1].id],
                    related_plan=feature_id,
                    related_adr="None",
                    evidence="pending: test scenario list",
                    dod="At least one integration scenario and one failure scenario documented",
                    waiver_reason="ADR pending during initial task generation",
                )
            )
            n += 1
        generated.append(
            TaskRecord(
                id=f"T-{n:03d}",
                feature_id=feature_id,
                title="Prepare execution readiness review",
                priority="P2",
                status="todo",
                owner="Maintainer",
                due=default_due(10),
                depends_on=[generated[-1].id],
                related_plan=feature_id,
                related_adr="None",
                evidence="pending: readiness checklist output",
                dod="Readiness checklist passes without blocking findings",
                waiver_reason="ADR pending during initial task generation",
            )
        )

        errors: list[str] = []
        for task in generated:
            errors.extend(validate_task_record(task))
        if errors:
            raise typer.BadParameter("Task validation failed: " + "; ".join(errors))

        rows = "\n".join(_build_row(task) for task in generated)
        body = f"""### Task Queue / 任务队列
| ID | Feature | Title | Priority | Status | Owner | Due | DependsOn | RelatedPlan | RelatedADR | Evidence | DoD | WaiverReason |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
{rows}
"""
        upsert_doc_feature(root, "TASKS.md", feature_id, "Execution Tasks", body)
        typer.echo(f"Generated {len(generated)} tasks for {feature_id}")
