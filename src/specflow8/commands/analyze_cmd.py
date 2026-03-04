from __future__ import annotations

import re
from pathlib import Path

import typer

from specflow8.config import load_config
from specflow8.constants import CORE_DOCS
from specflow8.io_markdown import extract_feature_block, read_text
from specflow8.models import QualityFinding
from specflow8.validators import dependency_cycle, parse_decision_rows, parse_task_rows
from specflow8.workflow import all_feature_ids, ensure_docs, latest_feature_id


def _analyze_docs(root: Path, feature: str | None, run_all: bool) -> list[QualityFinding]:
    findings: list[QualityFinding] = []

    for doc in CORE_DOCS:
        path = root / doc
        if not path.exists():
            findings.append(
                QualityFinding(
                    code="DOC_MISSING",
                    severity="error",
                    doc=doc,
                    feature_id=feature,
                    message=f"Core doc missing: {doc}",
                    suggestion="Run `specflow8 init` to repair baseline docs.",
                )
            )
            continue

        content = read_text(path)
        starts = re.findall(r"<!-- specflow8:feature:(F-\d{3}):start -->", content)
        ends = re.findall(r"<!-- specflow8:feature:(F-\d{3}):end -->", content)
        for fid in set(starts + ends):
            if starts.count(fid) != ends.count(fid):
                findings.append(
                    QualityFinding(
                        code="MARKER_UNBALANCED",
                        severity="error",
                        doc=doc,
                        feature_id=fid,
                        message=f"Unbalanced markers for {fid}.",
                        suggestion="Fix start/end marker pairs for this feature block.",
                    )
                )

    target_features: list[str]
    if run_all:
        target_features = all_feature_ids(root)
    elif feature:
        target_features = [feature]
    else:
        latest = latest_feature_id(root)
        target_features = [latest] if latest else []

    if feature and feature not in all_feature_ids(root):
        findings.append(
            QualityFinding(
                code="FEATURE_NOT_FOUND",
                severity="error",
                doc="*",
                feature_id=feature,
                message=f"Feature {feature} not found in docs.",
                suggestion="Create feature with `specflow8 specify` or use --all.",
            )
        )

    tasks_content = read_text(root / "TASKS.md")
    task_rows = parse_task_rows(tasks_content)
    decision_content = read_text(root / "DECISIONS.md")
    decision_rows = parse_decision_rows(decision_content)

    for fid in target_features:
        has_tasks = fid in tasks_content
        if not has_tasks:
            findings.append(
                QualityFinding(
                    code="TASKS_MISSING_FEATURE",
                    severity="warn",
                    doc="TASKS.md",
                    feature_id=fid,
                    message=f"No task section found for {fid}.",
                    suggestion=f"Run `specflow8 tasks --feature {fid}`.",
                )
            )
        has_decisions = fid in decision_content
        if not has_decisions:
            findings.append(
                QualityFinding(
                    code="DECISION_MISSING_FEATURE",
                    severity="warn",
                    doc="DECISIONS.md",
                    feature_id=fid,
                    message=f"No decision section found for {fid}.",
                    suggestion=f"Run `specflow8 decide --feature {fid} ...`.",
                )
            )
        if task_rows:
            cycles = dependency_cycle(task_rows)
            if cycles:
                findings.append(
                    QualityFinding(
                        code="TASK_DEP_CYCLE",
                        severity="error",
                        doc="TASKS.md",
                        feature_id=fid,
                        message=f"Dependency cycle detected: {', '.join(cycles)}",
                        suggestion="Break cyclic DependsOn references.",
                    )
                )
        readme_feature_block = extract_feature_block(read_text(root / "README.md"), fid) or ""
        clarify_count = readme_feature_block.count("NEEDS CLARIFICATION")
        if clarify_count > 3:
            findings.append(
                QualityFinding(
                    code="CLARIFICATION_LIMIT_EXCEEDED",
                    severity="warn",
                    doc="README.md",
                    feature_id=fid,
                    message=f"{clarify_count} clarification markers found (limit 3).",
                    suggestion="Refine assumptions and keep at most 3 markers.",
                )
            )

    if not findings:
        findings.append(
            QualityFinding(
                code="ANALYZE_OK",
                severity="info",
                doc="*",
                feature_id=feature,
                message="No blocking issues found.",
                suggestion="Continue with checklist or implement flow.",
            )
        )
    return findings


def register(app: typer.Typer) -> None:
    @app.command("analyze")
    def analyze_command(
        feature: str | None = typer.Option(
            None, "--feature", help="Target feature (F-XXX)."
        ),
        all: bool = typer.Option(False, "--all", help="Analyze all known features."),
        fail_on_warning: bool = typer.Option(
            False, "--fail-on-warning", help="Return non-zero exit code on warnings."
        ),
    ) -> None:
        root = Path(".").resolve()
        cfg = load_config(root)
        ensure_docs(root, cfg, cfg.language, cfg.docs_optional_enabled)
        findings = _analyze_docs(root, feature=feature, run_all=all)
        for item in findings:
            scope = item.feature_id or "-"
            typer.echo(
                f"[{item.severity.upper()}] {item.code} | {item.doc} | {scope} | {item.message}"
            )
        has_error = any(f.severity == "error" for f in findings)
        has_warn = any(f.severity == "warn" for f in findings)
        if has_error or (fail_on_warning and has_warn):
            raise typer.Exit(code=1)
