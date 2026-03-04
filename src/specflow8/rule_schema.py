from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

MODES = ("advisory", "transition", "strict")
SEVERITIES = ("info", "warn", "error", "off")
STAGES = ("doc_existence", "syntax_marker", "traceability", "quality_gates", "commit_trace")
RULE_FILES = ("boundary_rules.yaml", "consistency_rules.yaml", "quality_gates.yaml")


@dataclass(slots=True)
class ExecutableRule:
    check_id: str
    checker: str
    stage: str
    severity_by_mode: dict[str, str]
    message: str
    suggestion: str
    params: dict[str, Any] = field(default_factory=dict)
    source_file: str = ""


@dataclass(slots=True)
class RuleSchemaError:
    file: str
    message: str


def _validate_severity_map(value: Any, file_name: str, idx: int) -> list[RuleSchemaError]:
    errors: list[RuleSchemaError] = []
    if not isinstance(value, dict):
        return [
            RuleSchemaError(
                file=file_name,
                message=f"rules[{idx}].severity_by_mode must be a mapping.",
            )
        ]
    for mode in MODES:
        if mode not in value:
            errors.append(
                RuleSchemaError(
                    file=file_name,
                    message=f"rules[{idx}].severity_by_mode missing `{mode}`.",
                )
            )
            continue
        severity = value.get(mode)
        if severity not in SEVERITIES:
            errors.append(
                RuleSchemaError(
                    file=file_name,
                    message=(
                        f"rules[{idx}].severity_by_mode.{mode} must be one of: "
                        + ", ".join(SEVERITIES)
                    ),
                )
            )
    return errors


def load_rule_file(path: Path) -> tuple[list[ExecutableRule], list[RuleSchemaError]]:
    file_name = path.name
    if not path.exists():
        return [], [RuleSchemaError(file=file_name, message="Rule file is missing.")]
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        return [], [RuleSchemaError(file=file_name, message=f"YAML parse error: {exc}")]

    if not isinstance(raw, dict):
        return [], [RuleSchemaError(file=file_name, message="Top-level YAML must be a mapping.")]
    rules_raw = raw.get("rules")
    if not isinstance(rules_raw, list):
        return [], [RuleSchemaError(file=file_name, message="Top-level `rules` must be a list.")]

    errors: list[RuleSchemaError] = []
    parsed: list[ExecutableRule] = []
    required_keys = {
        "check_id",
        "checker",
        "stage",
        "severity_by_mode",
        "message",
        "suggestion",
    }
    for idx, entry in enumerate(rules_raw):
        if not isinstance(entry, dict):
            errors.append(
                RuleSchemaError(file=file_name, message=f"rules[{idx}] must be a mapping.")
            )
            continue
        missing = sorted(required_keys - set(entry))
        if missing:
            errors.append(
                RuleSchemaError(
                    file=file_name,
                    message=f"rules[{idx}] missing required keys: {', '.join(missing)}.",
                )
            )
            continue
        stage = str(entry["stage"])
        if stage not in STAGES:
            errors.append(
                RuleSchemaError(
                    file=file_name,
                    message=f"rules[{idx}].stage must be one of: {', '.join(STAGES)}.",
                )
            )
        errors.extend(_validate_severity_map(entry["severity_by_mode"], file_name, idx))
        parsed.append(
            ExecutableRule(
                check_id=str(entry["check_id"]).strip(),
                checker=str(entry["checker"]).strip(),
                stage=stage,
                severity_by_mode={
                    mode: str(entry["severity_by_mode"].get(mode, "off"))
                    for mode in MODES
                },
                message=str(entry["message"]).strip(),
                suggestion=str(entry["suggestion"]).strip(),
                params=dict(entry.get("params", {}) or {}),
                source_file=file_name,
            )
        )
    return parsed, errors


def load_rules(rule_dir: Path) -> tuple[list[ExecutableRule], list[RuleSchemaError]]:
    all_rules: list[ExecutableRule] = []
    errors: list[RuleSchemaError] = []
    for file_name in RULE_FILES:
        parsed, schema_errors = load_rule_file(rule_dir / file_name)
        all_rules.extend(parsed)
        errors.extend(schema_errors)
    duplicates = _duplicate_check_ids(all_rules)
    for check_id in duplicates:
        errors.append(
            RuleSchemaError(
                file="*",
                message=f"Duplicate check_id found across rule files: {check_id}",
            )
        )
    return all_rules, errors


def _duplicate_check_ids(rules: list[ExecutableRule]) -> list[str]:
    seen: set[str] = set()
    dup: set[str] = set()
    for rule in rules:
        if rule.check_id in seen:
            dup.add(rule.check_id)
        seen.add(rule.check_id)
    return sorted(dup)
