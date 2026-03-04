from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Literal

FeatureStatus = Literal["draft", "planned", "in_progress", "blocked", "done"]
TaskPriority = Literal["P0", "P1", "P2"]
TaskStatus = Literal["todo", "in_progress", "done", "blocked"]
Severity = Literal["info", "warn", "error"]
GovernanceMode = Literal["advisory", "transition", "strict"]


@dataclass(slots=True)
class FeatureRef:
    id: str
    title: str
    status: FeatureStatus
    created_at: date
    updated_at: date


@dataclass(slots=True)
class TaskRecord:
    id: str
    feature_id: str
    title: str
    priority: TaskPriority
    status: TaskStatus
    owner: str
    due: date | None
    depends_on: list[str]
    related_plan: str
    related_adr: str
    evidence: str
    dod: str
    waiver_reason: str = ""


@dataclass(slots=True)
class DecisionRecord:
    adr_id: str
    feature_id: str
    date: date
    context: str
    decision: str
    alternatives: str
    consequences: str
    related_tasks: str
    status: str
    supersedes: str
    verification: str


@dataclass(slots=True)
class QualityFinding:
    code: str
    severity: Severity
    doc: str
    feature_id: str | None
    message: str
    suggestion: str
    stage: str = "general"
    rule_id: str | None = None
