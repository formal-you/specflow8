from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .constants import (
    CORE_DOCS,
    DEFAULT_CLARIFICATION_LIMIT,
    DEFAULT_FEATURE_ID_PATTERN,
    REVIEW_CADENCE_DEFAULTS,
)


@dataclass(slots=True)
class AnalyzeConfig:
    enforce_commit_trace: bool = True
    git_log_depth: int = 100
    #: Per-rule severity overrides: {check_id: {mode: severity}}
    rule_overrides: dict[str, dict[str, str]] = field(default_factory=dict)


@dataclass(slots=True)
class ProjectConfig:
    """Describes team and architecture dimension of the project."""
    scale: str = "medium"       # small | medium | large
    type: str = "monolith"      # monolith | distributed | multi-team


@dataclass(slots=True)
class GovernanceChain:
    """Describes which governance links are required vs optional."""
    required_links: list[str] = field(default_factory=list)
    optional_links: list[str] = field(default_factory=list)


@dataclass(slots=True)
class Specflow8Config:
    version: str = "0.2"
    language: str = "bilingual"
    project: ProjectConfig = field(default_factory=ProjectConfig)
    docs_core: list[str] = field(default_factory=lambda: list(CORE_DOCS))
    docs_optional_enabled: bool = False
    feature_id_pattern: str = DEFAULT_FEATURE_ID_PATTERN
    clarification_limit: int = DEFAULT_CLARIFICATION_LIMIT
    governance_mode: str = "transition"
    governance_chain: GovernanceChain = field(default_factory=GovernanceChain)
    analyze: AnalyzeConfig = field(default_factory=AnalyzeConfig)
    review_cadence_defaults: dict[str, str] = field(
        default_factory=lambda: dict(REVIEW_CADENCE_DEFAULTS)
    )


CONFIG_FILE_NAME = "specflow8.yaml"


def config_path(root: Path) -> Path:
    return root / CONFIG_FILE_NAME


def _load_analyze(raw: Any) -> AnalyzeConfig:
    data = raw if isinstance(raw, dict) else {}
    overrides_raw = data.get("rule_overrides", {})
    rule_overrides: dict[str, dict[str, str]] = {}
    if isinstance(overrides_raw, dict):
        for check_id, sev_map in overrides_raw.items():
            if isinstance(sev_map, dict):
                rule_overrides[str(check_id)] = {
                    str(k): str(v) for k, v in sev_map.items()
                }
    try:
        git_log_depth = int(data.get("git_log_depth", 100))
    except (ValueError, TypeError):
        git_log_depth = 100
    return AnalyzeConfig(
        enforce_commit_trace=bool(data.get("enforce_commit_trace", True)),
        git_log_depth=git_log_depth,
        rule_overrides=rule_overrides,
    )


def _load_project(raw: Any) -> ProjectConfig:
    data = raw if isinstance(raw, dict) else {}
    return ProjectConfig(
        scale=str(data.get("scale", "medium")),
        type=str(data.get("type", "monolith")),
    )


def _load_governance_chain(raw: Any) -> GovernanceChain:
    data = raw if isinstance(raw, dict) else {}
    return GovernanceChain(
        required_links=list(data.get("required_links", [])),
        optional_links=list(data.get("optional_links", [])),
    )


def load_config(root: Path) -> Specflow8Config:
    path = config_path(root)
    if not path.exists():
        return Specflow8Config()
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ValueError(
            f"specflow8.yaml has invalid YAML syntax: {exc}"
        ) from exc

    try:
        clarification_limit = int(
            data.get("clarification_limit", DEFAULT_CLARIFICATION_LIMIT)
        )
    except (ValueError, TypeError):
        clarification_limit = DEFAULT_CLARIFICATION_LIMIT

    return Specflow8Config(
        version=str(data.get("version", "0.2")),
        language=str(data.get("language", "bilingual")),
        project=_load_project(data.get("project", {})),
        docs_core=list(data.get("docs_core", CORE_DOCS)),
        docs_optional_enabled=bool(data.get("docs_optional_enabled", False)),
        feature_id_pattern=str(
            data.get("feature_id_pattern", DEFAULT_FEATURE_ID_PATTERN)
        ),
        clarification_limit=clarification_limit,
        governance_mode=str(data.get("governance_mode", "transition")),
        governance_chain=_load_governance_chain(data.get("governance_chain", {})),
        analyze=_load_analyze(data.get("analyze", {})),
        review_cadence_defaults=dict(
            data.get("review_cadence_defaults", REVIEW_CADENCE_DEFAULTS)
        ),
    )


def _config_to_dict(cfg: Specflow8Config) -> dict:
    """Convert config to a serializable dict (handles nested dataclasses)."""
    d = asdict(cfg)
    return d


def save_config(root: Path, cfg: Specflow8Config) -> Path:
    path = config_path(root)
    raw = _config_to_dict(cfg)
    path.write_text(yaml.safe_dump(raw, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return path
