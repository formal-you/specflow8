"""Unit tests for config.py — v0.1 compat, v0.2 round-trip, rule_overrides."""

from __future__ import annotations

import yaml
from pathlib import Path

from specflow8.config import (
    load_config,
    save_config,
    Specflow8Config,
    ProjectConfig,
    GovernanceChain,
    AnalyzeConfig,
)


def _write_yaml(path: Path, data: dict) -> None:
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def test_load_v01_compat(tmp_path: Path):
    """A v0.1 YAML (no 'project' or 'governance_chain') should load gracefully."""
    _write_yaml(
        tmp_path / "specflow8.yaml",
        {
            "version": "0.1",
            "language": "en",
            "docs_core": ["README.md", "TASKS.md"],
            "governance_mode": "advisory",
            "analyze": {"enforce_commit_trace": False, "git_log_depth": 50},
        },
    )
    cfg = load_config(tmp_path)
    assert cfg.version == "0.1"
    assert cfg.language == "en"
    assert cfg.governance_mode == "advisory"
    assert cfg.analyze.enforce_commit_trace is False
    assert cfg.analyze.git_log_depth == 50
    # Defaults for missing v0.2 fields
    assert cfg.project.scale == "medium"
    assert cfg.project.type == "monolith"
    assert cfg.governance_chain.required_links == []


def test_load_v02_full(tmp_path: Path):
    """A full v0.2 YAML should parse all new fields."""
    _write_yaml(
        tmp_path / "specflow8.yaml",
        {
            "version": "0.2",
            "language": "bilingual",
            "project": {"scale": "large", "type": "distributed"},
            "docs_core": ["README.md", "TASKS.md", "SPECS.md"],
            "governance_mode": "strict",
            "governance_chain": {
                "required_links": ["spec_to_plan", "commit_trace"],
                "optional_links": [],
            },
            "analyze": {
                "enforce_commit_trace": True,
                "git_log_depth": 200,
                "rule_overrides": {
                    "COMMIT_TRACE_MISSING": {"advisory": "off"},
                },
            },
        },
    )
    cfg = load_config(tmp_path)
    assert cfg.version == "0.2"
    assert cfg.project.scale == "large"
    assert cfg.project.type == "distributed"
    assert "SPECS.md" in cfg.docs_core
    assert cfg.governance_chain.required_links == ["spec_to_plan", "commit_trace"]
    assert cfg.analyze.rule_overrides == {
        "COMMIT_TRACE_MISSING": {"advisory": "off"},
    }


def test_load_missing_config_returns_defaults(tmp_path: Path):
    cfg = load_config(tmp_path)
    assert cfg.version == "0.2"
    assert cfg.project.scale == "medium"
    assert cfg.project.type == "monolith"


def test_save_and_reload_roundtrip(tmp_path: Path):
    cfg = Specflow8Config(
        version="0.2",
        language="zh",
        project=ProjectConfig(scale="small", type="multi-team"),
        governance_mode="advisory",
        governance_chain=GovernanceChain(
            required_links=["feature_to_task"],
            optional_links=["commit_trace"],
        ),
        analyze=AnalyzeConfig(
            enforce_commit_trace=False,
            git_log_depth=50,
            rule_overrides={"TASK_NO_ADR_OR_WAIVER": {"advisory": "off"}},
        ),
    )
    save_config(tmp_path, cfg)
    loaded = load_config(tmp_path)
    assert loaded.version == "0.2"
    assert loaded.language == "zh"
    assert loaded.project.scale == "small"
    assert loaded.project.type == "multi-team"
    assert loaded.governance_mode == "advisory"
    assert loaded.governance_chain.required_links == ["feature_to_task"]
    assert loaded.governance_chain.optional_links == ["commit_trace"]
    assert loaded.analyze.enforce_commit_trace is False
    assert loaded.analyze.rule_overrides == {
        "TASK_NO_ADR_OR_WAIVER": {"advisory": "off"},
    }


def test_rule_overrides_ignored_when_malformed(tmp_path: Path):
    """Malformed rule_overrides should not crash — they're silently dropped."""
    _write_yaml(
        tmp_path / "specflow8.yaml",
        {
            "version": "0.2",
            "analyze": {
                "rule_overrides": {
                    "GOOD_RULE": {"advisory": "off"},
                    "BAD_RULE": "not-a-dict",
                },
            },
        },
    )
    cfg = load_config(tmp_path)
    assert "GOOD_RULE" in cfg.analyze.rule_overrides
    assert "BAD_RULE" not in cfg.analyze.rule_overrides
