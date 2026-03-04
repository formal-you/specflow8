from datetime import date

from specflow8.models import DecisionRecord, TaskRecord
from specflow8.validators import (
    detect_decisions_table_schema,
    detect_tasks_table_schema,
    parse_decision_rows,
    parse_task_rows,
    validate_decision_record,
    validate_task_record,
)


def test_validate_task_record_ok():
    task = TaskRecord(
        id="T-001",
        feature_id="F-001",
        title="Task title",
        priority="P1",
        status="todo",
        owner="Maintainer",
        due=date.today(),
        depends_on=[],
        related_plan="F-001",
        related_adr="ADR-001",
        evidence="test_task_record",
        dod="Done condition",
    )
    assert validate_task_record(task) == []


def test_validate_decision_record_ok():
    record = DecisionRecord(
        adr_id="ADR-001",
        feature_id="F-001",
        date=date.today(),
        context="ctx",
        decision="dec",
        alternatives="alt",
        consequences="cons",
        related_tasks="T-001",
        status="accepted",
        supersedes="None",
        verification="review:ok",
    )
    assert validate_decision_record(record) == []


def test_parse_task_rows_supports_new_and_legacy_schema():
    new_row = "| T-001 | F-001 | Task A | P1 | todo | owner | 2026-03-01 | None | F-001 | ADR-001 | ev | dod | None |"
    legacy_row = "| T-002 | Task B | P1 | todo | owner | 2026-03-01 | None | dod |"
    parsed = parse_task_rows("\n".join([new_row, legacy_row]))
    assert len(parsed) == 2
    assert parsed[0]["schema"] == "new"
    assert parsed[1]["schema"] == "legacy"
    assert parsed[0]["feature_id"] == "F-001"


def test_parse_decision_rows_supports_new_and_legacy_schema():
    new_row = "| ADR-001 | F-001 | 2026-03-01 | ctx | dec | alt | cons | T-001 | accepted | None | review:ok |"
    legacy_row = "| ADR-002 | 2026-03-01 | ctx | dec | alt | cons |"
    parsed = parse_decision_rows("\n".join([new_row, legacy_row]))
    assert len(parsed) == 2
    assert parsed[0]["schema"] == "new"
    assert parsed[1]["schema"] == "legacy"


def test_detect_table_schema_helpers():
    assert (
        detect_tasks_table_schema(
            "| ID | Feature | Title | Priority | Status | Owner | Due | DependsOn | RelatedPlan | RelatedADR | Evidence | DoD | WaiverReason |"
        )
        == "new"
    )
    assert (
        detect_decisions_table_schema(
            "| ADR-ID | Date | Context | Decision | Alternatives | Consequences |"
        )
        == "legacy"
    )
