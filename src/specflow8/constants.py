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
