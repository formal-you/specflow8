from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

HEADER_PATTERN = re.compile(r"^[a-z][a-z0-9_-]*\([^)]+?\): .+\S$")


@dataclass(slots=True)
class GitCommit:
    sha: str
    message: str

    @property
    def header(self) -> str:
        return self.message.splitlines()[0].strip() if self.message.strip() else ""

    def mentions_feature(self, feature_id: str) -> bool:
        return feature_id in self.message


def _run_git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError("git command timed out after 30s")
    if check and proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip() or "git command failed."
        raise RuntimeError(detail)
    return proc


def is_git_repo(root: Path) -> bool:
    try:
        out = _run_git(root, "rev-parse", "--is-inside-work-tree", check=True).stdout
    except RuntimeError:
        return False
    return out.strip() == "true"


def recent_doc_commits(root: Path, docs: list[str], depth: int) -> list[GitCommit]:
    if depth <= 0:
        return []
    proc = _run_git(
        root,
        "log",
        f"-n{depth}",
        "--pretty=format:%H%x1f%B%x1e",
        "--",
        *docs,
        check=False,
    )
    if proc.returncode != 0:
        return []
    chunks = proc.stdout.split("\x1e")
    commits: list[GitCommit] = []
    for chunk in chunks:
        text = chunk.strip()
        if not text:
            continue
        parts = text.split("\x1f", 1)
        if len(parts) != 2:
            continue
        sha = parts[0].strip()
        message = parts[1].strip()
        if not sha or not message:
            continue
        commits.append(GitCommit(sha=sha, message=message))
    return commits


def has_uncommitted_doc_changes(root: Path, docs: list[str]) -> bool:
    proc = _run_git(root, "status", "--porcelain", "--", *docs, check=False)
    if proc.returncode != 0:
        return False
    return bool(proc.stdout.strip())


def commit_matches_template(commit: GitCommit, feature_id: str) -> bool:
    text = commit.message.strip()
    if not text:
        return False
    lines = text.splitlines()
    header = lines[0].strip()
    if not HEADER_PATTERN.match(header):
        return False
    has_stage = re.search(r"\bstage\s*:\s*[\w-]+", text, re.IGNORECASE) is not None
    has_feature_field = (
        re.search(rf"\bfeature\s*:\s*{re.escape(feature_id)}\b", text, re.IGNORECASE)
        is not None
    )
    has_refs = (
        re.search(rf"\brefs\s*:\s*{re.escape(feature_id)}\b", text, re.IGNORECASE)
        is not None
    )
    linked_in_subject = feature_id in header
    return has_stage and has_feature_field and (has_refs or linked_in_subject)
