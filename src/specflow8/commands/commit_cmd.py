from __future__ import annotations

import re
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile

import typer

HEADER_PATTERN = re.compile(r"^[a-z][a-z0-9_-]*\([^)]+?\): .+\S$")


def _run_git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
    )
    if check and proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip() or "git command failed."
        raise RuntimeError(detail)
    return proc


def _is_git_repo(root: Path) -> bool:
    try:
        out = _run_git(root, "rev-parse", "--is-inside-work-tree", check=True).stdout
    except RuntimeError:
        return False
    return out.strip() == "true"


def _current_branch(root: Path) -> str:
    out = _run_git(root, "branch", "--show-current", check=True).stdout.strip()
    return out or "detached-head"


def _build_message(
    commit_type: str, scope: str, subject: str, body: str, footer: str
) -> str:
    header = f"{commit_type}({scope}): {subject}"
    clean_body = body.strip()
    clean_footer = footer.strip()
    return f"{header}\n\n{clean_body}\n\n{clean_footer}"


def _validate_commit_message(message: str) -> list[str]:
    errors: list[str] = []
    text = message.strip("\n")
    matched = re.match(
        r"^(?P<header>[^\n]+)\n\n(?P<body>[\s\S]+)\n\n(?P<footer>[^\n][\s\S]*)$",
        text,
    )
    if not matched:
        return [
            "Commit message must match: <type>(<scope>): <subject>\\n\\n<body>\\n\\n<footer>."
        ]

    header = matched.group("header").strip()
    body = matched.group("body").strip()
    footer = matched.group("footer").strip()

    if not HEADER_PATTERN.match(header):
        errors.append("Header must match `<type>(<scope>): <subject>`.")
    if not body:
        errors.append("Body section must not be empty.")
    if not footer:
        errors.append("Footer section must not be empty.")
    return errors


def register(app: typer.Typer) -> None:
    @app.command("commit")
    def commit_command(
        type_: str = typer.Option(
            "gitflow",
            "--type",
            help="Commit header <type> in `<type>(<scope>): <subject>`.",
        ),
        scope: str | None = typer.Option(
            None,
            "--scope",
            help="Commit header <scope>.",
        ),
        subject: str | None = typer.Option(
            None,
            "--subject",
            help="Commit header <subject>.",
        ),
        body: str | None = typer.Option(
            None,
            "--body",
            help="Commit body section (required).",
        ),
        footer: str | None = typer.Option(
            None,
            "--footer",
            help="Commit footer section (required).",
        ),
        root: Path = typer.Option(
            Path("."),
            "--root",
            help="Git repository root (or any path inside it).",
        ),
        allow_empty: bool = typer.Option(
            False, "--allow-empty", help="Allow empty commit when there is no file change."
        ),
        no_verify: bool = typer.Option(
            False, "--no-verify", help="Bypass git commit hooks."
        ),
        dry_run: bool = typer.Option(
            False,
            "--dry-run",
            help="Preview the commit message without creating a commit.",
        ),
    ) -> None:
        repo = root.resolve()
        if not _is_git_repo(repo):
            raise typer.BadParameter(f"Not a git repository: {repo}")

        branch = _current_branch(repo)
        missing: list[str] = []
        if not scope:
            missing.append("--scope")
        if not subject:
            missing.append("--subject")
        if not body:
            missing.append("--body")
        if not footer:
            missing.append("--footer")
        if missing:
            raise typer.BadParameter(
                "Missing required template fields: "
                + ", ".join(missing)
                + ". Expected format: <type>(<scope>): <subject>\\n\\n<body>\\n\\n<footer>."
            )

        message = _build_message(
            commit_type=type_.strip(),
            scope=scope.strip(),
            subject=subject.strip(),
            body=body,
            footer=footer,
        )

        fmt_errors = _validate_commit_message(message)
        if fmt_errors:
            raise typer.BadParameter(" ".join(fmt_errors))

        status = _run_git(repo, "status", "--porcelain", "--untracked-files=all", check=True).stdout
        has_changes = bool(status.strip())
        if not has_changes and not allow_empty:
            typer.echo("No changes detected. Skipped commit.")
            return

        if dry_run:
            typer.echo(f"[dry-run] branch={branch}")
            typer.echo("[dry-run] message:")
            typer.echo(message)
            return

        _run_git(repo, "add", "-A", check=True)
        with NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", delete=False) as tmp:
            tmp.write(message.strip() + "\n")
            msg_file = tmp.name
        args = ["commit", "-F", msg_file]
        if allow_empty:
            args.append("--allow-empty")
        if no_verify:
            args.append("--no-verify")
        try:
            commit_proc = _run_git(repo, *args, check=False)
        finally:
            Path(msg_file).unlink(missing_ok=True)
        if commit_proc.returncode != 0:
            detail = (commit_proc.stderr or commit_proc.stdout).strip() or "git commit failed."
            raise typer.BadParameter(detail)

        short_sha = _run_git(repo, "rev-parse", "--short", "HEAD", check=True).stdout.strip()
        header = message.splitlines()[0]
        typer.echo(f"Committed {short_sha}: {header}")
