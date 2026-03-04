from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path

import yaml

from .constants import (
    CORE_DOCS,
    DEFAULT_CLARIFICATION_LIMIT,
    DEFAULT_FEATURE_ID_PATTERN,
    REVIEW_CADENCE_DEFAULTS,
)


@dataclass(slots=True)
class Specflow8Config:
    version: str = "0.1"
    language: str = "bilingual"
    docs_core: list[str] = field(default_factory=lambda: list(CORE_DOCS))
    docs_optional_enabled: bool = False
    feature_id_pattern: str = DEFAULT_FEATURE_ID_PATTERN
    clarification_limit: int = DEFAULT_CLARIFICATION_LIMIT
    review_cadence_defaults: dict[str, str] = field(
        default_factory=lambda: dict(REVIEW_CADENCE_DEFAULTS)
    )


CONFIG_FILE_NAME = "specflow8.yaml"


def config_path(root: Path) -> Path:
    return root / CONFIG_FILE_NAME


def load_config(root: Path) -> Specflow8Config:
    path = config_path(root)
    if not path.exists():
        return Specflow8Config()
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return Specflow8Config(
        version=str(data.get("version", "0.1")),
        language=str(data.get("language", "bilingual")),
        docs_core=list(data.get("docs_core", CORE_DOCS)),
        docs_optional_enabled=bool(data.get("docs_optional_enabled", False)),
        feature_id_pattern=str(
            data.get("feature_id_pattern", DEFAULT_FEATURE_ID_PATTERN)
        ),
        clarification_limit=int(
            data.get("clarification_limit", DEFAULT_CLARIFICATION_LIMIT)
        ),
        review_cadence_defaults=dict(
            data.get("review_cadence_defaults", REVIEW_CADENCE_DEFAULTS)
        ),
    )


def save_config(root: Path, cfg: Specflow8Config) -> Path:
    path = config_path(root)
    path.write_text(yaml.safe_dump(asdict(cfg), sort_keys=False), encoding="utf-8")
    return path
