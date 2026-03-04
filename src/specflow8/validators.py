from __future__ import annotations

import re
from collections import defaultdict, deque
from datetime import date

from .models import DecisionRecord, TaskRecord

FEATURE_ID_RE = re.compile(r"^F-\d{3}$")
TASK_ID_RE = re.compile(r"^T-\d{3}$")
ADR_ID_RE = re.compile(r"^ADR-\d{3}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

TASK_HEADER_NEW = [
    "ID",
    "Feature",
    "Title",
    "Priority",
    "Status",
    "Owner",
    "Due",
    "DependsOn",
    "RelatedPlan",
    "RelatedADR",
    "Evidence",
    "DoD",
    "WaiverReason",
]
TASK_HEADER_LEGACY = [
    "ID",
    "Title",
    "Priority",
    "Status",
    "Owner",
    "Due",
    "DependsOn",
    "DoD",
]

DECISION_HEADER_NEW = [
    "ADR-ID",
    "Feature",
    "Date",
    "Context",
    "Decision",
    "Alternatives",
    "Consequences",
    "RelatedTasks",
    "Status",
    "Supersedes",
    "Verification",
]
DECISION_HEADER_LEGACY = [
    "ADR-ID",
    "Date",
    "Context",
    "Decision",
    "Alternatives",
    "Consequences",
]


def _split_markdown_row(line: str) -> list[str]:
    text = line.strip()
    if not text.startswith("|") or not text.endswith("|"):
        return []
    return [item.strip() for item in text.strip("|").split("|")]


def validate_feature_id(feature_id: str) -> bool:
    return bool(FEATURE_ID_RE.match(feature_id))


def validate_task_record(task: TaskRecord) -> list[str]:
    errors: list[str] = []
    if not TASK_ID_RE.match(task.id):
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
    if not task.related_plan.strip():
        errors.append("RelatedPlan must not be empty.")
    if not task.evidence.strip():
        errors.append("Evidence must not be empty.")
    if not task.dod.strip():
        errors.append("DoD must not be empty.")
    return errors


def validate_decision_record(decision: DecisionRecord) -> list[str]:
    errors: list[str] = []
    if not ADR_ID_RE.match(decision.adr_id):
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
    if not decision.related_tasks.strip():
        errors.append("RelatedTasks must not be empty.")
    if decision.status not in {"proposed", "accepted", "superseded", "rejected"}:
        errors.append("Status must be proposed/accepted/superseded/rejected.")
    if not decision.verification.strip():
        errors.append("Verification must not be empty.")
    return errors


def parse_task_rows(markdown: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in markdown.splitlines():
        cells = _split_markdown_row(line)
        if not cells:
            continue
        if len(cells) == len(TASK_HEADER_NEW) and TASK_ID_RE.match(cells[0]):
            rows.append(
                {
                    "id": cells[0],
                    "feature_id": cells[1],
                    "title": cells[2],
                    "priority": cells[3],
                    "status": cells[4],
                    "owner": cells[5],
                    "due": cells[6],
                    "depends_on": cells[7],
                    "related_plan": cells[8],
                    "related_adr": cells[9],
                    "evidence": cells[10],
                    "dod": cells[11],
                    "waiver_reason": cells[12],
                    "schema": "new",
                }
            )
            continue
        if len(cells) == len(TASK_HEADER_LEGACY) and TASK_ID_RE.match(cells[0]):
            rows.append(
                {
                    "id": cells[0],
                    "feature_id": "",
                    "title": cells[1],
                    "priority": cells[2],
                    "status": cells[3],
                    "owner": cells[4],
                    "due": cells[5],
                    "depends_on": cells[6],
                    "related_plan": "",
                    "related_adr": "",
                    "evidence": "",
                    "dod": cells[7],
                    "waiver_reason": "",
                    "schema": "legacy",
                }
            )
    return rows


def parse_decision_rows(markdown: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in markdown.splitlines():
        cells = _split_markdown_row(line)
        if not cells:
            continue
        if len(cells) == len(DECISION_HEADER_NEW) and ADR_ID_RE.match(cells[0]):
            rows.append(
                {
                    "adr_id": cells[0],
                    "feature_id": cells[1],
                    "date": cells[2],
                    "context": cells[3],
                    "decision": cells[4],
                    "alternatives": cells[5],
                    "consequences": cells[6],
                    "related_tasks": cells[7],
                    "status": cells[8],
                    "supersedes": cells[9],
                    "verification": cells[10],
                    "schema": "new",
                }
            )
            continue
        if len(cells) == len(DECISION_HEADER_LEGACY) and ADR_ID_RE.match(cells[0]):
            rows.append(
                {
                    "adr_id": cells[0],
                    "feature_id": "",
                    "date": cells[1],
                    "context": cells[2],
                    "decision": cells[3],
                    "alternatives": cells[4],
                    "consequences": cells[5],
                    "related_tasks": "",
                    "status": "",
                    "supersedes": "",
                    "verification": "",
                    "schema": "legacy",
                }
            )
    return rows


def detect_tasks_table_schema(markdown: str) -> str:
    for line in markdown.splitlines():
        cells = _split_markdown_row(line)
        if cells == TASK_HEADER_NEW:
            return "new"
        if cells == TASK_HEADER_LEGACY:
            return "legacy"
    return "missing"


def detect_decisions_table_schema(markdown: str) -> str:
    for line in markdown.splitlines():
        cells = _split_markdown_row(line)
        if cells == DECISION_HEADER_NEW:
            return "new"
        if cells == DECISION_HEADER_LEGACY:
            return "legacy"
    return "missing"


def dependency_cycle(task_rows: list[dict[str, str]]) -> list[str]:
    graph: dict[str, set[str]] = {}
    indeg: dict[str, int] = {}
    for row in task_rows:
        tid = row["id"]
        deps = [
            x.strip()
            for x in row["depends_on"].split(",")
            if x.strip() and x.strip().lower() != "none"
        ]
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
    indeg: dict[str, int] = {}
    reverse: dict[str, list[str]] = defaultdict(list)
    for row in task_rows:
        tid = row["id"]
        dep_set = {
            x.strip()
            for x in row["depends_on"].split(",")
            if x.strip() and x.strip().lower() != "none"
        }
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


def is_valid_due(value: str) -> bool:
    if value.lower() == "none":
        return True
    return bool(DATE_RE.match(value))
