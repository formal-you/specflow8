from __future__ import annotations

import json
from pathlib import Path

import typer

from specflow8.config import load_config
from specflow8.io_markdown import extract_feature_block, read_text, write_text
from specflow8.validators import parse_task_rows
from specflow8.workflow import (
    commands_template_root,
    ensure_docs,
    latest_feature_id,
    today,
)

STAGES = {
    "specify",
    "plan",
    "tasks",
    "implement",
    "analyze",
    "checklist",
    "clarify",
    "constitution",
}


def _suggested_script(stage: str, shell: str, feature_id: str | None) -> str:
    fid = feature_id or "F-XXX"
    if shell == "bash":
        mapping = {
            "specify": f'./scripts/specflow8/bash/create-new-feature.sh --json --description "<short request>" --tech "<stack>"',
            "plan": f"./scripts/specflow8/bash/setup-plan.sh --json --feature-id {fid}",
            "tasks": f"./scripts/specflow8/bash/check-prerequisites.sh --json --feature-id {fid} --include-tasks",
            "implement": f"./scripts/specflow8/bash/check-prerequisites.sh --json --feature-id {fid} --require-tasks --include-tasks",
            "analyze": f"./scripts/specflow8/bash/check-prerequisites.sh --json --feature-id {fid}",
            "checklist": f"./scripts/specflow8/bash/check-prerequisites.sh --json --feature-id {fid}",
            "clarify": f"./scripts/specflow8/bash/check-prerequisites.sh --json --feature-id {fid}",
            "constitution": "./scripts/specflow8/bash/check-prerequisites.sh --json",
        }
    else:
        mapping = {
            "specify": 'scripts/specflow8/powershell/create-new-feature.ps1 -Json -Description "<short request>" -Tech "<stack>"',
            "plan": f"scripts/specflow8/powershell/setup-plan.ps1 -Json -FeatureId {fid}",
            "tasks": f"scripts/specflow8/powershell/check-prerequisites.ps1 -Json -FeatureId {fid} -IncludeTasks",
            "implement": f"scripts/specflow8/powershell/check-prerequisites.ps1 -Json -FeatureId {fid} -RequireTasks -IncludeTasks",
            "analyze": f"scripts/specflow8/powershell/check-prerequisites.ps1 -Json -FeatureId {fid}",
            "checklist": f"scripts/specflow8/powershell/check-prerequisites.ps1 -Json -FeatureId {fid}",
            "clarify": f"scripts/specflow8/powershell/check-prerequisites.ps1 -Json -FeatureId {fid}",
            "constitution": "scripts/specflow8/powershell/check-prerequisites.ps1 -Json",
        }
    return mapping[stage]


def _suggested_commit(stage: str, feature_id: str | None) -> str:
    feature_value = feature_id or "N/A"
    subject = f"{stage} [{feature_value}] 本轮对话完成内容"
    body = f"stage: {stage}; feature: {feature_value}"
    footer = f"Refs: {feature_value}"
    return (
        f'specflow8 commit --type gitflow --scope {stage} '
        f'--subject "{subject}" --body "{body}" --footer "{footer}"'
    )


def _todo_excerpt(root: Path, feature_id: str | None) -> list[str]:
    if not feature_id:
        return ["- No feature selected."]
    tasks_block = extract_feature_block(read_text(root / "TASKS.md"), feature_id) or ""
    if not tasks_block:
        return ["- No task block found for this feature."]
    body = tasks_block
    if body.startswith("## ["):
        body = "\n".join(body.splitlines()[1:]).strip()
    rows = parse_task_rows(body)
    if not rows:
        return ["- No parsed tasks."]
    lines: list[str] = []
    for row in rows[:10]:
        check = "[x]" if row["status"] == "done" else "[ ]"
        lines.append(f"- {check} {row['id']} {row['title']} ({row['status']})")
    return lines


def register(app: typer.Typer) -> None:
    @app.command("handoff")
    def handoff_command(
        stage: str = typer.Option(..., "--stage", help="Workflow stage."),
        feature: str | None = typer.Option(
            None, "--feature", help="Feature ID (defaults to latest where applicable)."
        ),
        shell: str = typer.Option(
            "powershell", "--shell", help="Script shell: powershell | bash"
        ),
        output: Path | None = typer.Option(
            None, "--output", help="Output markdown handoff path."
        ),
        stdout: bool = typer.Option(False, "--stdout", help="Print handoff markdown."),
        json_output: bool = typer.Option(False, "--json", help="Print JSON payload."),
    ) -> None:
        stage = stage.strip().lower()
        if stage not in STAGES:
            raise typer.BadParameter(f"Invalid stage `{stage}`.")
        if shell not in {"powershell", "bash"}:
            raise typer.BadParameter("Invalid shell. Use `powershell` or `bash`.")

        root = Path(".").resolve()
        cfg = load_config(root)
        ensure_docs(root, cfg, cfg.language, cfg.docs_optional_enabled)

        feature_id = feature or latest_feature_id(root)
        local_template = root / ".specflow8" / "templates" / "commands" / f"{stage}.md"
        template_path = (
            local_template if local_template.exists() else commands_template_root() / f"{stage}.md"
        )
        if not template_path.exists():
            raise typer.BadParameter(
                f"Command template not found for stage `{stage}`: {template_path.name}"
            )
        template_text = template_path.read_text(encoding="utf-8").strip()
        suggested = _suggested_script(stage, shell, feature_id)
        suggested_commit = _suggested_commit(stage, feature_id)
        todo_lines = _todo_excerpt(root, feature_id)

        markdown = "\n".join(
            [
                f"# Subagent Handoff: {stage}",
                "",
                f"- Date: {today()}",
                f"- Feature: {feature_id or 'N/A'}",
                f"- Shell: {shell}",
                "",
                "## Suggested Script Command",
                "```bash" if shell == "bash" else "```powershell",
                suggested,
                "```",
                "",
                "## Suggested Commit Command",
                "```bash",
                suggested_commit,
                "```",
                "",
                "## Todo Excerpt",
                *todo_lines,
                "",
                "## Command Template",
                "```markdown",
                template_text,
                "```",
                "",
                "## Subagent Instructions",
                "- Use the script JSON output as runtime truth.",
                "- Execute stage-specific updates only.",
                "- Keep feature marker blocks balanced.",
                "- Run the suggested commit command before sending the final stage response.",
            ]
        ) + "\n"

        out = output or (
            root
            / ".specflow8"
            / "handoffs"
            / f"{(feature_id or 'global')}-{stage}-{shell}.md"
        )
        write_text(out, markdown)

        if stdout:
            typer.echo(markdown)
        payload = {
            "stage": stage,
            "feature_id": feature_id,
            "shell": shell,
            "template": str(template_path),
            "handoff_file": str(out),
            "suggested_command": suggested,
            "suggested_commit": suggested_commit,
        }
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False))
        else:
            typer.echo(f"Handoff generated: {out}")
