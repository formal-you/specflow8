from pathlib import Path

from specflow8.rule_schema import RULE_FILES, load_rule_file, load_rules
from specflow8.workflow import rule_root


def test_builtin_rule_files_are_schema_valid():
    rules, errors = load_rules(rule_root())
    assert errors == []
    assert len(rules) >= 8


def test_load_rule_file_rejects_missing_required_keys(tmp_path: Path):
    file_path = tmp_path / "quality_gates.yaml"
    file_path.write_text("rules:\n  - check_id: BAD\n", encoding="utf-8")
    rules, errors = load_rule_file(file_path)
    assert rules == []
    assert errors
    assert "missing required keys" in errors[0].message


def test_load_rules_reports_duplicate_check_id(tmp_path: Path):
    template = """rules:
  - check_id: DUPLICATE
    checker: doc_existence
    stage: doc_existence
    severity_by_mode:
      advisory: warn
      transition: error
      strict: error
    message: test
    suggestion: fix
"""
    for name in RULE_FILES:
        (tmp_path / name).write_text(template, encoding="utf-8")
    _, errors = load_rules(tmp_path)
    assert any("Duplicate check_id" in err.message for err in errors)
