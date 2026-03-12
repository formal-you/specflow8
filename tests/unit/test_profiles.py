"""Unit tests for profiles.py — three-tier governance profile system."""

from __future__ import annotations

import pytest

from specflow8.profiles import (
    list_profiles,
    resolve_profile,
    resolve_profile_from_id,
    upgrade_profile,
)
from specflow8.constants import SCALES, PROJECT_TYPES, PROFILE_DOC_MAP


def test_all_nine_profiles_resolve():
    """Every scale × type combination must resolve without error."""
    for scale in SCALES:
        for ptype in PROJECT_TYPES:
            p = resolve_profile(scale, ptype)
            assert p.profile_id == f"{scale}-{ptype}"
            assert p.scale == scale
            assert p.project_type == ptype


def test_small_profile_has_fewer_docs():
    small = resolve_profile("small", "monolith")
    large = resolve_profile("large", "monolith")
    assert len(small.docs_core) < len(large.docs_core)
    assert len(small.docs_core) == 3


def test_small_monolith_doc_set():
    p = resolve_profile("small", "monolith")
    assert "README.md" in p.docs_core
    assert "TASKS.md" in p.docs_core
    assert "DECISIONS.md" in p.docs_core
    # No heavy docs
    assert "AGENTS.md" not in p.docs_core
    assert "PLAN.md" not in p.docs_core


def test_large_profile_has_specs():
    p = resolve_profile("large", "distributed")
    assert "SPECS.md" in p.docs_core


def test_medium_profile_has_full_8_docs():
    p = resolve_profile("medium", "monolith")
    expected = [
        "AGENTS.md", "README.md", "ARCHITECTURE.md", "DOMAIN.md",
        "STATE.md", "PLAN.md", "TASKS.md", "DECISIONS.md",
    ]
    for doc in expected:
        assert doc in p.docs_core


def test_governance_mode_by_scale():
    assert resolve_profile("small", "monolith").governance_mode == "advisory"
    assert resolve_profile("medium", "monolith").governance_mode == "transition"
    assert resolve_profile("large", "monolith").governance_mode == "strict"


def test_commit_trace_by_scale():
    assert resolve_profile("small", "monolith").enforce_commit_trace is False
    assert resolve_profile("medium", "monolith").enforce_commit_trace is True
    assert resolve_profile("large", "monolith").enforce_commit_trace is True


def test_small_rule_overrides_disable_commit_trace():
    p = resolve_profile("small", "monolith")
    assert "COMMIT_TRACE_MISSING" in p.rule_overrides
    assert p.rule_overrides["COMMIT_TRACE_MISSING"]["advisory"] == "off"
    assert p.rule_overrides["COMMIT_TRACE_MISSING"]["transition"] == "off"


def test_large_profile_has_no_relaxation():
    p = resolve_profile("large", "multi-team")
    # large does not override anything to "off"
    for rule_id, sev_map in p.rule_overrides.items():
        for mode, severity in sev_map.items():
            assert severity != "off", f"{rule_id}[{mode}] should not be 'off' for large"


def test_unknown_scale_falls_back_to_medium():
    p = resolve_profile("tiny", "monolith")
    assert p.scale == "medium"


def test_unknown_type_falls_back_to_monolith():
    p = resolve_profile("small", "serverless")
    assert p.project_type == "monolith"


def test_list_profiles_returns_nine():
    profiles = list_profiles()
    assert len(profiles) == 9
    assert "small-monolith" in profiles
    assert "large-multi-team" in profiles


def test_resolve_profile_from_id():
    p = resolve_profile_from_id("medium-distributed")
    assert p.scale == "medium"
    assert p.project_type == "distributed"


def test_upgrade_profile_adds_docs():
    small = resolve_profile("small", "monolith")
    new_preset, new_docs = upgrade_profile(small, new_scale="medium")
    assert new_preset.scale == "medium"
    assert len(new_docs) > 0


def test_upgrade_profile_same_returns_no_diff():
    medium = resolve_profile("medium", "monolith")
    new_preset, new_docs = upgrade_profile(medium, new_scale="medium", new_type="monolith")
    assert new_preset.profile_id == medium.profile_id
    assert new_docs == []


def test_chain_required_grows_with_scale():
    small = resolve_profile("small", "monolith")
    large = resolve_profile("large", "monolith")
    assert len(large.chain_required) > len(small.chain_required)
    assert "pr_template" in large.chain_required
    assert "spec_to_plan" in large.chain_required


def test_small_distributed_has_architecture():
    p = resolve_profile("small", "distributed")
    assert "ARCHITECTURE.md" in p.docs_core


@pytest.mark.parametrize("pid", list_profiles())
def test_all_profiles_have_required_doc_baseline(pid: str):
    """Every profile must include at least README.md, TASKS.md, DECISIONS.md."""
    parts = pid.split("-", 1)
    p = resolve_profile(parts[0], parts[1])
    for must_have in ["README.md", "TASKS.md", "DECISIONS.md"]:
        assert must_have in p.docs_core, f"{pid} missing {must_have}"
