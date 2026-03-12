"""Integration tests for profile-aware init, profile CLI, and upgrade flows."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from specflow8.cli import app


runner = CliRunner()


def test_init_small_monolith_creates_workflow_docs_without_agents():
    with runner.isolated_filesystem():
        result = runner.invoke(
            app, ["init", "--root", ".", "--scale", "small", "--type", "monolith"]
        )
        assert result.exit_code == 0
        assert "small-monolith" in result.stdout
        assert Path("README.md").exists()
        assert Path("ARCHITECTURE.md").exists()
        assert Path("DOMAIN.md").exists()
        assert Path("PLAN.md").exists()
        assert Path("STATE.md").exists()
        assert Path("TASKS.md").exists()
        assert Path("DECISIONS.md").exists()
        assert not Path("AGENTS.md").exists()
        assert not Path("SPECS.md").exists()


def test_init_large_distributed_creates_specs():
    with runner.isolated_filesystem():
        result = runner.invoke(
            app, ["init", "--root", ".", "--scale", "large", "--type", "distributed"]
        )
        assert result.exit_code == 0
        assert "large-distributed" in result.stdout
        assert Path("SPECS.md").exists()
        assert Path("AGENTS.md").exists()


def test_init_medium_sets_transition_mode():
    with runner.isolated_filesystem():
        result = runner.invoke(
            app, ["init", "--root", ".", "--scale", "medium", "--type", "monolith"]
        )
        assert result.exit_code == 0
        assert "transition" in result.stdout


def test_init_json_output_has_profile_info():
    with runner.isolated_filesystem():
        result = runner.invoke(
            app,
            ["init", "--root", ".", "--scale", "small", "--type", "monolith", "--json"],
        )
        assert result.exit_code == 0
        payload = json.loads(result.stdout.strip())
        assert payload["profile"] == "small-monolith"
        assert payload["scale"] == "small"
        assert payload["governance_mode"] == "advisory"
        assert "next_steps" in payload
        assert len(payload["next_steps"]) >= 1


def test_init_with_profile_shorthand():
    with runner.isolated_filesystem():
        result = runner.invoke(
            app,
            ["init", "--root", ".", "--profile", "large-multi-team", "--json"],
        )
        assert result.exit_code == 0
        payload = json.loads(result.stdout.strip())
        assert payload["profile"] == "large-multi-team"
        assert "SPECS.md" in payload["created_docs"]


def test_init_invalid_scale_rejected():
    with runner.isolated_filesystem():
        result = runner.invoke(
            app, ["init", "--root", ".", "--scale", "tiny", "--type", "monolith"]
        )
        assert result.exit_code != 0


def test_profile_show_command():
    with runner.isolated_filesystem():
        runner.invoke(
            app, ["init", "--root", ".", "--scale", "medium", "--type", "distributed"]
        )
        result = runner.invoke(app, ["profile", "show"])
        assert result.exit_code == 0
        assert "medium-distributed" in result.stdout


def test_profile_show_json():
    with runner.isolated_filesystem():
        runner.invoke(
            app, ["init", "--root", ".", "--scale", "small", "--type", "monolith"]
        )
        result = runner.invoke(app, ["profile", "show", "--json"])
        assert result.exit_code == 0
        payload = json.loads(result.stdout)
        assert payload["scale"] == "small"
        assert payload["type"] == "monolith"


def test_profile_list_command():
    with runner.isolated_filesystem():
        runner.invoke(app, ["init", "--root", "."])
        result = runner.invoke(app, ["profile", "list"])
        assert result.exit_code == 0
        assert "small-monolith" in result.stdout
        assert "large-multi-team" in result.stdout


def test_profile_list_json():
    with runner.isolated_filesystem():
        runner.invoke(app, ["init", "--root", "."])
        result = runner.invoke(app, ["profile", "list", "--json"])
        assert result.exit_code == 0
        items = json.loads(result.stdout)
        assert len(items) == 9


def test_profile_upgrade_adds_docs():
    with runner.isolated_filesystem():
        runner.invoke(
            app, ["init", "--root", ".", "--scale", "small", "--type", "monolith"]
        )
        assert not Path("AGENTS.md").exists()

        result = runner.invoke(app, ["profile", "upgrade", "--scale", "medium"])
        assert result.exit_code == 0
        assert Path("AGENTS.md").exists()
        assert Path(".github/PULL_REQUEST_TEMPLATE.md").exists()


def test_profile_upgrade_dry_run_does_not_create():
    with runner.isolated_filesystem():
        runner.invoke(
            app, ["init", "--root", ".", "--scale", "small", "--type", "monolith"]
        )
        result = runner.invoke(
            app, ["profile", "upgrade", "--scale", "large", "--dry-run"]
        )
        assert result.exit_code == 0
        assert "Dry-run" in result.stdout
        assert not Path("SPECS.md").exists()


def test_profile_upgrade_same_tier_no_op():
    with runner.isolated_filesystem():
        runner.invoke(
            app, ["init", "--root", ".", "--scale", "medium", "--type", "monolith"]
        )
        result = runner.invoke(app, ["profile", "upgrade", "--scale", "medium"])
        assert result.exit_code == 0
        assert "already" in result.stdout


def test_profile_upgrade_recreates_missing_pr_template():
    with runner.isolated_filesystem():
        runner.invoke(
            app, ["init", "--root", ".", "--scale", "medium", "--type", "monolith"]
        )
        Path(".github/PULL_REQUEST_TEMPLATE.md").unlink()

        result = runner.invoke(app, ["profile", "upgrade", "--scale", "large"])
        assert result.exit_code == 0
        assert Path(".github/PULL_REQUEST_TEMPLATE.md").exists()


def test_profile_upgrade_rejects_invalid_scale():
    with runner.isolated_filesystem():
        runner.invoke(app, ["init", "--root", "."])

        result = runner.invoke(app, ["profile", "upgrade", "--scale", "tiny"])
        assert result.exit_code != 0
        assert "Invalid --scale" in result.output


def test_analyze_small_profile_does_not_report_missing_agents():
    """When using a small profile, AGENTS.md is not required → no DOC_MISSING error."""
    with runner.isolated_filesystem():
        runner.invoke(
            app, ["init", "--root", ".", "--scale", "small", "--type", "monolith"]
        )
        runner.invoke(app, ["specify", "Build dashboard"])
        runner.invoke(app, ["tasks", "--feature", "F-001"])
        result = runner.invoke(
            app, ["analyze", "--feature", "F-001", "--no-enforce-commit-trace"]
        )
        assert result.exit_code == 0
        assert "DOC_MISSING" not in result.stdout
