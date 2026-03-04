import json
import re
import shutil
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from specflow8.cli import app


def test_full_flow():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(app, ["init", "--root", ".", "--with-optional-docs"])
        assert result.exit_code == 0

        result = runner.invoke(app, ["specify", "Build searchable dashboard"])
        assert result.exit_code == 0

        result = runner.invoke(app, ["plan", "--feature", "F-001", "Python + FastAPI"])
        assert result.exit_code == 0

        result = runner.invoke(app, ["tasks", "--feature", "F-001", "--with-tests"])
        assert result.exit_code == 0

        result = runner.invoke(
            app,
            [
                "decide",
                "--feature",
                "F-001",
                "--title",
                "Use API-first",
                "--context",
                "Need stable contracts",
                "--choice",
                "Adopt API-first design",
            ],
        )
        assert result.exit_code == 0

        result = runner.invoke(app, ["state", "--feature", "F-001", "--snapshot", "Planning done"])
        assert result.exit_code == 0

        result = runner.invoke(app, ["analyze", "--feature", "F-001"])
        assert result.exit_code == 0

        result = runner.invoke(app, ["implement", "--feature", "F-001", "--dry-run"])
        assert result.exit_code == 0


def test_init_language_and_force_overwrite():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(app, ["init", "--root", ".", "--lang", "en"])
        assert result.exit_code == 0
        readme = open("README.md", "r", encoding="utf-8").read()
        assert "System Goal" in readme
        assert "系统目标" not in readme

        result = runner.invoke(app, ["init", "--root", ".", "--lang", "zh", "--force"])
        assert result.exit_code == 0
        readme = open("README.md", "r", encoding="utf-8").read()
        assert "系统目标" in readme
        assert "System Goal" not in readme


def test_agent_kit_todo_and_handoff_flow():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(app, ["init", "--root", "."])
        assert result.exit_code == 0
        assert Path(".specflow8/templates/commands/specify.md").exists()
        assert Path("scripts/specflow8/bash/create-new-feature.sh").exists()
        assert Path("scripts/specflow8/powershell/check-prerequisites.ps1").exists()

        assert runner.invoke(app, ["specify", "Build task triage board"]).exit_code == 0
        assert (
            runner.invoke(app, ["plan", "--feature", "F-001", "Python + FastAPI"])
            .exit_code
            == 0
        )
        assert runner.invoke(app, ["tasks", "--feature", "F-001"]).exit_code == 0

        todo_result = runner.invoke(app, ["todo", "--feature", "F-001", "--json"])
        assert todo_result.exit_code == 0
        todo_payload = json.loads(todo_result.stdout.strip().splitlines()[-1])
        assert todo_payload["feature_id"] == "F-001"
        assert Path(todo_payload["output"]).exists()

        handoff_result = runner.invoke(
            app,
            [
                "handoff",
                "--stage",
                "tasks",
                "--feature",
                "F-001",
                "--shell",
                "bash",
                "--json",
            ],
        )
        assert handoff_result.exit_code == 0
        handoff_payload = json.loads(handoff_result.stdout.strip().splitlines()[-1])
        handoff_file = Path(handoff_payload["handoff_file"])
        assert handoff_file.exists()
        assert ".specflow8" in handoff_payload["template"]
        assert handoff_payload["suggested_commit"].startswith(
            "specflow8 commit --type gitflow --scope tasks"
        )
        text = handoff_file.read_text(encoding="utf-8")
        assert "Subagent Handoff: tasks" in text
        assert "check-prerequisites.sh" in text
        assert "specflow8 commit --type gitflow --scope tasks" in text


def test_commit_command_gitflow_branch():
    if shutil.which("git") is None:
        return

    runner = CliRunner()
    with runner.isolated_filesystem():
        subprocess.run(["git", "init"], check=True)
        subprocess.run(["git", "config", "user.name", "Specflow8 Bot"], check=True)
        subprocess.run(
            ["git", "config", "user.email", "specflow8@example.com"], check=True
        )
        subprocess.run(["git", "checkout", "-b", "feature/F-001-docflow"], check=True)

        Path("README.md").write_text("hello\n", encoding="utf-8")
        result = runner.invoke(
            app,
            [
                "commit",
                "--type",
                "gitflow",
                "--scope",
                "tasks",
                "--subject",
                "tasks [F-001] 本轮对话完成内容",
                "--body",
                "stage: tasks; feature: F-001",
                "--footer",
                "Refs: F-001",
            ],
        )
        assert result.exit_code == 0
        assert "Committed" in result.stdout

        subject = subprocess.run(
            ["git", "log", "-1", "--pretty=%s"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        assert subject == "gitflow(tasks): tasks [F-001] 本轮对话完成内容"

        full_message = subprocess.run(
            ["git", "log", "-1", "--pretty=%B"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        assert re.match(
            r"^[a-z][a-z0-9_-]*\([^)]+\): .+\n\n[\s\S]+\n\n[\s\S]+$",
            full_message,
        )


def test_commit_command_skips_without_changes():
    if shutil.which("git") is None:
        return

    runner = CliRunner()
    with runner.isolated_filesystem():
        subprocess.run(["git", "init"], check=True)
        subprocess.run(["git", "config", "user.name", "Specflow8 Bot"], check=True)
        subprocess.run(
            ["git", "config", "user.email", "specflow8@example.com"], check=True
        )
        Path("README.md").write_text("base\n", encoding="utf-8")
        subprocess.run(["git", "add", "-A"], check=True)
        subprocess.run(["git", "commit", "-m", "init"], check=True)

        result = runner.invoke(
            app,
            [
                "commit",
                "--type",
                "gitflow",
                "--scope",
                "tasks",
                "--subject",
                "tasks [F-001] 本轮对话完成内容",
                "--body",
                "stage: tasks; feature: F-001",
                "--footer",
                "Refs: F-001",
            ],
        )
        assert result.exit_code == 0
        assert "No changes detected. Skipped commit." in result.stdout


def test_commit_command_rejects_legacy_stage_feature_options():
    runner = CliRunner()
    result = runner.invoke(app, ["commit", "--stage", "tasks", "--feature", "F-001"])
    assert result.exit_code != 0
    assert "--stage" in result.output
