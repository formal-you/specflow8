"""
profiles.py — Three-tier governance profile system.

A Profile is the combination of:
  - scale: small | medium | large (team size)
  - type:  monolith | distributed | multi-team (architecture)

The 9 = 3×3 combinations each pre-configure:
  - Required core documents
  - Default governance_mode
  - Governance chain links
  - Rule severity overrides
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .constants import (
    PROFILE_DOC_MAP,
    PROFILE_RULE_OVERRIDES,
    SCALES,
    PROJECT_TYPES,
    CORE_DOCS,
)

# ---------------------------------------------------------------------------
# Domain types
# ---------------------------------------------------------------------------

PROFILE_MODES: dict[str, str] = {
    "small": "advisory",
    "medium": "transition",
    "large": "strict",
}

PROFILE_COMMIT_TRACE: dict[str, bool] = {
    "small": False,
    "medium": True,
    "large": True,
}

PROFILE_CLARIFICATION_LIMIT: dict[str, int] = {
    "small": 5,
    "medium": 3,
    "large": 1,
}

# Governance chain links per scale
PROFILE_CHAIN: dict[str, dict[str, list[str]]] = {
    "small": {
        "required": ["feature_to_task"],
        "optional": ["task_to_adr_or_waiver", "commit_trace"],
    },
    "medium": {
        "required": ["feature_to_task", "task_to_adr_or_waiver", "adr_to_task", "commit_trace"],
        "optional": ["pr_template"],
    },
    "large": {
        "required": [
            "spec_to_plan",
            "feature_to_task",
            "task_to_adr_or_waiver",
            "adr_to_task",
            "commit_trace",
            "pr_template",
        ],
        "optional": [],
    },
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class ProfilePreset:
    """A fully resolved governance profile."""

    profile_id: str                          # e.g. "medium-distributed"
    scale: str                               # small | medium | large
    project_type: str                        # monolith | distributed | multi-team
    governance_mode: str                     # advisory | transition | strict
    docs_core: list[str]                     # required document list
    enforce_commit_trace: bool
    clarification_limit: int
    chain_required: list[str] = field(default_factory=list)
    chain_optional: list[str] = field(default_factory=list)
    rule_overrides: dict[str, dict[str, str]] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------


def profile_id(scale: str, project_type: str) -> str:
    return f"{scale}-{project_type}"


def list_profiles() -> list[str]:
    """Return all valid profile IDs."""
    return [profile_id(s, t) for s in SCALES for t in PROJECT_TYPES]


def resolve_profile(scale: str, project_type: str) -> ProfilePreset:
    """
    Derive the ProfilePreset from a (scale, type) pair.

    Falls back to 'medium-monolith' for unknown combinations.
    """
    scale = scale.strip().lower() if scale else "medium"
    project_type = project_type.strip().lower() if project_type else "monolith"

    if scale not in SCALES:
        scale = "medium"
    if project_type not in PROJECT_TYPES:
        project_type = "monolith"

    pid = profile_id(scale, project_type)
    docs = list(PROFILE_DOC_MAP.get(pid, PROFILE_DOC_MAP.get(f"{scale}-monolith", CORE_DOCS)))
    chain = PROFILE_CHAIN.get(scale, PROFILE_CHAIN["medium"])
    rule_ov = PROFILE_RULE_OVERRIDES.get(scale, {})

    return ProfilePreset(
        profile_id=pid,
        scale=scale,
        project_type=project_type,
        governance_mode=PROFILE_MODES.get(scale, "transition"),
        docs_core=docs,
        enforce_commit_trace=PROFILE_COMMIT_TRACE.get(scale, True),
        clarification_limit=PROFILE_CLARIFICATION_LIMIT.get(scale, 3),
        chain_required=list(chain["required"]),
        chain_optional=list(chain["optional"]),
        rule_overrides=dict(rule_ov),
    )


def resolve_profile_from_id(pid: str) -> ProfilePreset:
    """Parse 'scale-type' string and resolve."""
    parts = pid.split("-", 1)
    if len(parts) != 2:
        return resolve_profile("medium", "monolith")
    return resolve_profile(parts[0], parts[1])


def upgrade_profile(
    current: ProfilePreset,
    new_scale: str | None = None,
    new_type: str | None = None,
) -> tuple[ProfilePreset, list[str]]:
    """
    Upgrade a profile to a new scale/type.

    Returns (new_preset, list_of_new_docs_to_add).
    """
    target_scale = new_scale or current.scale
    target_type = new_type or current.project_type
    new_preset = resolve_profile(target_scale, target_type)
    new_docs = [d for d in new_preset.docs_core if d not in current.docs_core]
    return new_preset, new_docs


def profile_to_config_dict(preset: ProfilePreset) -> dict:
    """Serialize preset fields for writing into specflow8.yaml."""
    return {
        "project": {
            "scale": preset.scale,
            "type": preset.project_type,
        },
        "docs_core": preset.docs_core,
        "governance_mode": preset.governance_mode,
        "clarification_limit": preset.clarification_limit,
        "analyze": {
            "enforce_commit_trace": preset.enforce_commit_trace,
            "git_log_depth": 100,
            "rule_overrides": preset.rule_overrides,
        },
        "governance_chain": {
            "required_links": preset.chain_required,
            "optional_links": preset.chain_optional,
        },
    }
