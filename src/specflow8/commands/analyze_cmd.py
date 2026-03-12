from __future__ import annotations

import json
from pathlib import Path

import typer

from specflow8.config import load_config
from specflow8.models import QualityFinding
from specflow8.profiles import resolve_profile
from specflow8.rule_engine import RuleEngine, build_context
from specflow8.rule_schema import MODES, load_rules
from specflow8.workflow import ensure_docs, rule_root


def _serialize_findings(
    findings: list[QualityFinding],
    mode: str,
    feature: str | None,
    run_all: bool,
    enforce_commit_trace: bool,
    profile_id: str,
) -> dict[str, object]:
    return {
        "mode": mode,
        "profile": profile_id,
        "feature": feature,
        "all": run_all,
        "enforce_commit_trace": enforce_commit_trace,
        "summary": {
            "info": len([f for f in findings if f.severity == "info"]),
            "warn": len([f for f in findings if f.severity == "warn"]),
            "error": len([f for f in findings if f.severity == "error"]),
        },
        "findings": [
            {
                "code": f.code,
                "severity": f.severity,
                "stage": f.stage,
                "doc": f.doc,
                "feature_id": f.feature_id,
                "message": f.message,
                "suggestion": f.suggestion,
                "rule_id": f.rule_id,
            }
            for f in findings
        ],
    }


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
        mode: str | None = typer.Option(
            None,
            "--mode",
            help="Governance mode: advisory | transition | strict.",
        ),
        json_output: bool = typer.Option(
            False, "--json", help="Emit structured JSON findings."
        ),
        enforce_commit_trace: bool | None = typer.Option(
            None,
            "--enforce-commit-trace/--no-enforce-commit-trace",
            help="Enable/disable commit trace checks.",
        ),
    ) -> None:
        root = Path(".").resolve()
        cfg = load_config(root)
        ensure_docs(root, cfg, cfg.language, cfg.docs_optional_enabled)

        mode_value = (mode or cfg.governance_mode or "transition").strip().lower()
        if mode_value not in MODES:
            raise typer.BadParameter(
                f"Invalid --mode `{mode_value}`. Allowed: advisory | transition | strict."
            )
        commit_trace_enabled = (
            cfg.analyze.enforce_commit_trace
            if enforce_commit_trace is None
            else enforce_commit_trace
        )

        # Resolve active profile and merge rule overrides
        preset = resolve_profile(cfg.project.scale, cfg.project.type)
        # Profile overrides first; user config overrides win on conflict
        merged_overrides: dict[str, dict[str, str]] = {}
        merged_overrides.update(preset.rule_overrides)
        merged_overrides.update(cfg.analyze.rule_overrides)

        rules, schema_errors = load_rules(rule_root())
        if schema_errors:
            for err in schema_errors:
                typer.echo(f"[ERROR] RULE_SCHEMA_INVALID | {err.file} | - | {err.message}")
            raise typer.Exit(code=1)

        engine = RuleEngine(rules)
        ctx = build_context(
            root=root,
            mode=mode_value,  # type: ignore[arg-type]
            feature=feature,
            run_all=all,
            enforce_commit_trace=commit_trace_enabled,
            git_log_depth=max(1, cfg.analyze.git_log_depth),
            clarification_limit=cfg.clarification_limit,
            required_docs=preset.docs_core,
            rule_overrides=merged_overrides,
        )
        findings = engine.run(ctx)
        if not findings:
            findings = [
                QualityFinding(
                    code="ANALYZE_OK",
                    severity="info",
                    doc="*",
                    feature_id=feature,
                    message="No issues found.",
                    suggestion="Continue with checklist or implement flow.",
                    stage="quality_gates",
                    rule_id="engine",
                )
            ]

        if json_output:
            typer.echo(
                json.dumps(
                    _serialize_findings(
                        findings=findings,
                        mode=mode_value,
                        feature=feature,
                        run_all=all,
                        enforce_commit_trace=commit_trace_enabled,
                        profile_id=preset.profile_id,
                    ),
                    ensure_ascii=False,
                )
            )
        else:
            for item in findings:
                scope = item.feature_id or "-"
                typer.echo(
                    f"[{item.severity.upper()}] {item.code} | {item.stage} | {item.doc} | {scope} | {item.message}"
                )
            info_count = len([f for f in findings if f.severity == "info"])
            warn_count = len([f for f in findings if f.severity == "warn"])
            error_count = len([f for f in findings if f.severity == "error"])
            typer.echo(
                f"Summary: info={info_count} warn={warn_count} error={error_count} "
                f"mode={mode_value} profile={preset.profile_id}"
            )

        has_error = any(f.severity == "error" for f in findings)
        has_warn = any(f.severity == "warn" for f in findings)
        if has_error or (has_warn and fail_on_warning):
            raise typer.Exit(code=1)
