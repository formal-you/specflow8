from __future__ import annotations

CORE_DOCS = [
    "AGENTS.md",
    "README.md",
    "ARCHITECTURE.md",
    "DOMAIN.md",
    "STATE.md",
    "PLAN.md",
    "TASKS.md",
    "DECISIONS.md",
]

OPTIONAL_DOCS = ["RUNBOOK.md", "INTERFACES.md"]
PR_TEMPLATE_DOC = ".github/PULL_REQUEST_TEMPLATE.md"

FEATURE_START_FMT = "<!-- specflow8:feature:{feature_id}:start -->"
FEATURE_END_FMT = "<!-- specflow8:feature:{feature_id}:end -->"

MANUAL_START = "<!-- specflow8:manual:start -->"
MANUAL_END = "<!-- specflow8:manual:end -->"

DEFAULT_FEATURE_ID_PATTERN = r"F-\d{3}"
DEFAULT_CLARIFICATION_LIMIT = 3

REVIEW_CADENCE_DEFAULTS = {
    "state": "weekly",
    "tasks": "weekly",
    "plan": "milestone",
    "architecture": "milestone",
    "decisions": "milestone",
}

# ---------------------------------------------------------------------------
# Three-tier governance profile system
# ---------------------------------------------------------------------------

#: Valid scale values (team size)
SCALES = ("small", "medium", "large")

#: Valid project type values (architecture)
PROJECT_TYPES = ("monolith", "distributed", "multi-team")

# Smallest required doc set per profile ("scale-type")
# small: 3 docs (no process overhead)
# medium: 7 docs (standard 8-doc set minus SPECS)
# large: 9 docs (full 8-doc set + SPECS.md)
_SMALL_DOCS = ["README.md", "TASKS.md", "DECISIONS.md"]
_SMALL_DIST_DOCS = ["README.md", "ARCHITECTURE.md", "TASKS.md", "DECISIONS.md"]
_MEDIUM_DOCS = [
    "AGENTS.md", "README.md", "ARCHITECTURE.md", "DOMAIN.md",
    "STATE.md", "PLAN.md", "TASKS.md", "DECISIONS.md",
]
_LARGE_DOCS = [
    "AGENTS.md", "README.md", "ARCHITECTURE.md", "DOMAIN.md",
    "STATE.md", "PLAN.md", "TASKS.md", "DECISIONS.md", "SPECS.md",
]

PROFILE_DOC_MAP: dict[str, list[str]] = {
    "small-monolith":    _SMALL_DOCS,
    "small-distributed": _SMALL_DIST_DOCS,
    "small-multi-team":  _SMALL_DIST_DOCS,
    "medium-monolith":   _MEDIUM_DOCS,
    "medium-distributed": _MEDIUM_DOCS,
    "medium-multi-team": _MEDIUM_DOCS,
    "large-monolith":    _LARGE_DOCS,
    "large-distributed": _LARGE_DOCS,
    "large-multi-team":  _LARGE_DOCS,
}

# Per-scale rule severity overrides.
# Keys map check_id → {mode → severity}.
# "off" means the rule is suppressed for that mode.
PROFILE_RULE_OVERRIDES: dict[str, dict[str, dict[str, str]]] = {
    "small": {
        "COMMIT_TRACE_MISSING": {
            "advisory": "off",
            "transition": "off",
            "strict": "warn",
        },
        "COMMIT_TEMPLATE_INVALID": {
            "advisory": "off",
            "transition": "off",
            "strict": "warn",
        },
        "PR_TEMPLATE_MISSING": {
            "advisory": "off",
            "transition": "off",
            "strict": "warn",
        },
        "PR_TEMPLATE_FIELD_MISSING": {
            "advisory": "off",
            "transition": "off",
            "strict": "warn",
        },
        "FEATURE_NO_ADR_OR_REASON": {
            "advisory": "off",
            "transition": "off",
            "strict": "warn",
        },
        "TASK_NO_ADR_OR_WAIVER": {
            "advisory": "off",
            "transition": "off",
            "strict": "warn",
        },
    },
    "medium": {
        # Keep defaults from YAML — no overrides needed
    },
    "large": {
        # large enforces everything strictly; no relaxation
    },
}
