from datetime import date

from specflow8.models import DecisionRecord, TaskRecord
from specflow8.validators import validate_decision_record, validate_task_record


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
    )
    assert validate_decision_record(record) == []
