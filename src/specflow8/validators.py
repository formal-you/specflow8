from __future__ import annotations

import re
from collections import defaultdict, deque
from datetime import date

from .models import DecisionRecord, TaskRecord

TASK_ROW_RE = re.compile(
    r"^\|\s*(T-\d{3})\s*\|\s*(.*?)\s*\|\s*(P[0-2])\s*\|\s*(todo|in_progress|done|blocked)\s*\|\s*(.*?)\s*\|\s*(\d{4}-\d{2}-\d{2}|None)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|$"
)

DECISION_ROW_RE = re.compile(
    r"^\|\s*(ADR-\d{3})\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|$"
)

FEATURE_ID_RE = re.compile(r"^F-\d{3}$")


def validate_feature_id(feature_id: str) -> bool:
    return bool(FEATURE_ID_RE.match(feature_id))


def validate_task_record(task: TaskRecord) -> list[str]:
    errors: list[str] = []
    if not re.match(r"^T-\d{3}$", task.id):
        errors.append("Task ID must match T-XXX.")
    if task.priority not in {"P0", "P1", "P2"}:
        errors.append("Priority must be P0/P1/P2.")
    if task.status not in {"todo", "in_progress", "done", "blocked"}:
        errors.append("Status must be todo/in_progress/done/blocked.")
    if not validate_feature_id(task.feature_id):
        errors.append("Feature ID must match F-XXX.")
    if not task.title.strip():
        errors.append("Title must not be empty.")
    if not task.owner.strip():
        errors.append("Owner must not be empty.")
    if not task.dod.strip():
        errors.append("DoD must not be empty.")
    return errors


def validate_decision_record(decision: DecisionRecord) -> list[str]:
    errors: list[str] = []
    if not re.match(r"^ADR-\d{3}$", decision.adr_id):
        errors.append("ADR ID must match ADR-XXX.")
    if not validate_feature_id(decision.feature_id):
        errors.append("Feature ID must match F-XXX.")
    if not isinstance(decision.date, date):
        errors.append("Date must be a valid date.")
    if not decision.context.strip():
        errors.append("Context must not be empty.")
    if not decision.decision.strip():
        errors.append("Decision must not be empty.")
    if not decision.alternatives.strip():
        errors.append("Alternatives must not be empty.")
    if not decision.consequences.strip():
        errors.append("Consequences must not be empty.")
    return errors


def parse_task_rows(markdown: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in markdown.splitlines():
        m = TASK_ROW_RE.match(line.strip())
        if not m:
            continue
        rows.append(
            {
                "id": m.group(1),
                "title": m.group(2),
                "priority": m.group(3),
                "status": m.group(4),
                "owner": m.group(5),
                "due": m.group(6),
                "depends_on": m.group(7),
                "dod": m.group(8),
            }
        )
    return rows


def parse_decision_rows(markdown: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in markdown.splitlines():
        m = DECISION_ROW_RE.match(line.strip())
        if not m:
            continue
        rows.append(
            {
                "adr_id": m.group(1),
                "date": m.group(2),
                "context": m.group(3),
                "decision": m.group(4),
                "alternatives": m.group(5),
                "consequences": m.group(6),
            }
        )
    return rows


def dependency_cycle(task_rows: list[dict[str, str]]) -> list[str]:
    graph: dict[str, set[str]] = {}
    indeg: dict[str, int] = {}
    for row in task_rows:
        tid = row["id"]
        deps = [x.strip() for x in row["depends_on"].split(",") if x.strip() and x.strip() != "None"]
        graph[tid] = set(deps)
        indeg.setdefault(tid, 0)
    reverse: dict[str, list[str]] = defaultdict(list)
    for node, deps in graph.items():
        for dep in deps:
            reverse[dep].append(node)
            indeg[node] = indeg.get(node, 0) + 1
            indeg.setdefault(dep, indeg.get(dep, 0))

    q = deque([n for n, d in indeg.items() if d == 0])
    visited = 0
    while q:
        node = q.popleft()
        visited += 1
        for nxt in reverse.get(node, []):
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                q.append(nxt)
    if visited != len(indeg):
        return [n for n, d in indeg.items() if d > 0]
    return []


def topological_order(task_rows: list[dict[str, str]]) -> list[str]:
    deps: dict[str, set[str]] = {}
    indeg: dict[str, int] = {}
    reverse: dict[str, list[str]] = defaultdict(list)
    for row in task_rows:
        tid = row["id"]
        dep_set = {
            x.strip() for x in row["depends_on"].split(",") if x.strip() and x.strip() != "None"
        }
        deps[tid] = dep_set
        indeg.setdefault(tid, 0)
        for dep in dep_set:
            reverse[dep].append(tid)
            indeg[tid] = indeg.get(tid, 0) + 1
            indeg.setdefault(dep, indeg.get(dep, 0))

    ready = deque(sorted(n for n, d in indeg.items() if d == 0))
    order: list[str] = []
    while ready:
        node = ready.popleft()
        order.append(node)
        for nxt in reverse.get(node, []):
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                ready.append(nxt)
    return order
