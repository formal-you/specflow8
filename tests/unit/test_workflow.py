from pathlib import Path

from specflow8.workflow import (
    clarification_candidates,
    ensure_agent_kit,
    next_feature_id,
    normalize_language,
)


def test_next_feature_id_from_empty(tmp_path: Path):
    assert next_feature_id(tmp_path) == "F-001"


def test_clarification_limit():
    description = "Build a feature"
    markers = clarification_candidates(description, limit=3)
    assert len(markers) <= 3


def test_normalize_language():
    assert normalize_language("zh") == "zh"
    assert normalize_language("en") == "en"
    assert normalize_language("bilingual") == "bilingual"
    assert normalize_language("ZH") == "zh"
    assert normalize_language("unknown") == "bilingual"


def test_ensure_agent_kit_scaffolds_expected_assets(tmp_path: Path):
    created, skipped = ensure_agent_kit(tmp_path, force=False, script_variant="powershell")
    assert skipped == []
    normalized = [path.replace("\\", "/") for path in created]
    assert any(path.endswith(".specflow8/templates/commands/specify.md") for path in normalized)
    assert any(path.endswith("scripts/specflow8/powershell/create-new-feature.ps1") for path in normalized)
    assert not any("/bash/" in path for path in normalized)
