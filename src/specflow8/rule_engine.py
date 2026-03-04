from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from specflow8.constants import CORE_DOCS, PR_TEMPLATE_DOC
from specflow8.git_trace import (
    commit_matches_template,
    has_uncommitted_doc_changes,
    is_git_repo,
    recent_doc_commits,
)
from specflow8.io_markdown import extract_feature_block, find_feature_ids, read_text
from specflow8.models import GovernanceMode, QualityFinding
from specflow8.rule_schema import ExecutableRule, STAGES
from specflow8.validators import (
    dependency_cycle,
    detect_decisions_table_schema,
    detect_tasks_table_schema,
    parse_decision_rows,
    parse_task_rows,
)
from specflow8.workflow import all_feature_ids, latest_feature_id

STAGE_ORDER = {name: idx for idx, name in enumerate(STAGES)}
NONE_VALUES = {"", "none", "n/a", "na", "-"}


@dataclass(slots=True)
class AnalyzeContext:
    root: Path
    mode: GovernanceMode
    run_all: bool
    feature: str | None
    enforce_commit_trace: bool
    git_log_depth: int
    clarification_limit: int
    docs: dict[str, str] = field(default_factory=dict)
    all_features: list[str] = field(default_factory=list)
    target_features: list[str] = field(default_factory=list)
    tasks_schema: str = "missing"
    decisions_schema: str = "missing"
    tasks_by_feature: dict[str, list[dict[str, str]]] = field(default_factory=dict)
    decisions_by_feature: dict[str, list[dict[str, str]]] = field(default_factory=dict)
    _cache: dict[str, Any] = field(default_factory=dict)


Checker = Callable[[ExecutableRule, AnalyzeContext], list[dict[str, Any]]]


def checker_registry() -> dict[str, Checker]:
    return {
        "doc_existence": _check_doc_existence,
        "marker_balance": _check_marker_balance,
        "trace_link_integrity": _check_trace_link_integrity,
        "coverage_checks": _check_coverage,
        "quality_gates": _check_quality_gates,
        "clarification_limit": _check_clarification_limit,
        "dependency_cycle": _check_dependency_cycle,
        "commit_trace": _check_commit_trace,
        "boundary_violation": _check_boundary_violation,
        "pr_template": _check_pr_template,
    }


def build_context(
    root: Path,
    mode: GovernanceMode,
    feature: str | None,
    run_all: bool,
    enforce_commit_trace: bool,
    git_log_depth: int,
    clarification_limit: int,
) -> AnalyzeContext:
    docs = {doc: read_text(root / doc) for doc in CORE_DOCS}
    all_ids = all_feature_ids(root)
    if run_all:
        target = list(all_ids)
    elif feature:
        target = [feature]
    else:
        latest = latest_feature_id(root)
        target = [latest] if latest else []

    tasks_text = docs.get("TASKS.md", "")
    decisions_text = docs.get("DECISIONS.md", "")
    tasks_schema = detect_tasks_table_schema(tasks_text)
    decisions_schema = detect_decisions_table_schema(decisions_text)

    tasks_by_feature: dict[str, list[dict[str, str]]] = {}
    decisions_by_feature: dict[str, list[dict[str, str]]] = {}
    for fid in all_ids:
        task_block = _feature_body(tasks_text, fid)
        decision_block = _feature_body(decisions_text, fid)
        task_rows = parse_task_rows(task_block)
        decision_rows = parse_decision_rows(decision_block)
        for row in task_rows:
            if not row.get("feature_id"):
                row["feature_id"] = fid
        for row in decision_rows:
            if not row.get("feature_id"):
                row["feature_id"] = fid
        tasks_by_feature[fid] = task_rows
        decisions_by_feature[fid] = decision_rows

    return AnalyzeContext(
        root=root,
        mode=mode,
        run_all=run_all,
        feature=feature,
        enforce_commit_trace=enforce_commit_trace,
        git_log_depth=git_log_depth,
        clarification_limit=clarification_limit,
        docs=docs,
        all_features=all_ids,
        target_features=target,
        tasks_schema=tasks_schema,
        decisions_schema=decisions_schema,
        tasks_by_feature=tasks_by_feature,
        decisions_by_feature=decisions_by_feature,
    )


class RuleEngine:
    def __init__(self, rules: list[ExecutableRule]) -> None:
        self._rules = sorted(
            rules,
            key=lambda item: (STAGE_ORDER.get(item.stage, 999), item.check_id),
        )
        self._registry = checker_registry()

    @property
    def rules(self) -> list[ExecutableRule]:
        return list(self._rules)

    def run(self, ctx: AnalyzeContext) -> list[QualityFinding]:
        findings: list[QualityFinding] = []
        for rule in self._rules:
            checker = self._registry.get(rule.checker)
            if checker is None:
                continue
            severity = _severity_for_mode(rule, ctx.mode)
            if severity == "off":
                continue
            for issue in checker(rule, ctx):
                payload = dict(issue)
                payload.setdefault("doc", "*")
                payload.setdefault("feature_id", None)
                message = _format_text(rule.message, payload)
                suggestion = _format_text(rule.suggestion, payload)
                findings.append(
                    QualityFinding(
                        code=rule.check_id,
                        severity=severity,  # type: ignore[arg-type]
                        doc=str(payload["doc"]),
                        feature_id=payload.get("feature_id"),
                        message=message,
                        suggestion=suggestion,
                        stage=rule.stage,
                        rule_id=rule.source_file,
                    )
                )
        return findings


def _feature_body(content: str, feature_id: str) -> str:
    block = extract_feature_block(content, feature_id) or ""
    if block.startswith("## ["):
        return "\n".join(block.splitlines()[1:]).strip()
    return block


def _severity_for_mode(rule: ExecutableRule, mode: GovernanceMode) -> str:
    return rule.severity_by_mode.get(mode, "off")


class _SafeDict(dict[str, Any]):
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def _format_text(template: str, payload: dict[str, Any]) -> str:
    return template.format_map(_SafeDict(payload))


def _is_empty(value: str | None) -> bool:
    if value is None:
        return True
    return value.strip().lower() in NONE_VALUES


def _parse_ids(value: str, pattern: str) -> list[str]:
    return re.findall(pattern, value)


def _plan_has_waiver(ctx: AnalyzeContext, feature_id: str) -> bool:
    plan_block = _feature_body(ctx.docs.get("PLAN.md", ""), feature_id)
    if not plan_block:
        return False
    return re.search(r"\b(waiver|waiverreason|exception|exempt)\b", plan_block, re.I) is not None


def _check_doc_existence(rule: ExecutableRule, ctx: AnalyzeContext) -> list[dict[str, Any]]:
    kind = str(rule.params.get("kind", "")).strip().lower()
    if kind == "feature_not_found":
        if ctx.feature and ctx.feature not in ctx.all_features:
            return [{"doc": "*", "feature_id": ctx.feature}]
        return []

    issues: list[dict[str, Any]] = []
    for doc in CORE_DOCS:
        if not (ctx.root / doc).exists():
            issues.append({"doc": doc, "feature_id": ctx.feature})
    return issues


def _check_marker_balance(rule: ExecutableRule, ctx: AnalyzeContext) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for doc, text in ctx.docs.items():
        starts = re.findall(r"<!-- specflow8:feature:(F-\d{3}):start -->", text)
        ends = re.findall(r"<!-- specflow8:feature:(F-\d{3}):end -->", text)
        for fid in sorted(set(starts + ends)):
            if starts.count(fid) != ends.count(fid):
                issues.append({"doc": doc, "feature_id": fid})
    return issues


def _check_trace_link_integrity(rule: ExecutableRule, ctx: AnalyzeContext) -> list[dict[str, Any]]:
    kind = str(rule.params.get("kind", "missing")).strip().lower()
    issues: list[dict[str, Any]] = []
    plan_features = set(find_feature_ids(ctx.docs.get("PLAN.md", "")))
    all_task_ids = {row["id"] for rows in ctx.tasks_by_feature.values() for row in rows}
    all_adr_ids = {
        row["adr_id"] for rows in ctx.decisions_by_feature.values() for row in rows
    }
    for fid in ctx.target_features:
        task_rows = ctx.tasks_by_feature.get(fid, [])
        decision_rows = ctx.decisions_by_feature.get(fid, [])
        for row in task_rows:
            if row.get("schema") != "new":
                continue
            related_plan = row.get("related_plan", "")
            related_adr = row.get("related_adr", "")
            if kind == "missing":
                if _is_empty(related_plan):
                    issues.append(
                        {
                            "doc": "TASKS.md",
                            "feature_id": fid,
                            "id": row.get("id", ""),
                            "field": "RelatedPlan",
                        }
                    )
                elif not _parse_ids(related_plan, r"F-\d{3}"):
                    issues.append(
                        {
                            "doc": "TASKS.md",
                            "feature_id": fid,
                            "id": row.get("id", ""),
                            "field": "RelatedPlan",
                        }
                    )
                if not _is_empty(related_adr) and not _parse_ids(related_adr, r"ADR-\d{3}"):
                    issues.append(
                        {
                            "doc": "TASKS.md",
                            "feature_id": fid,
                            "id": row.get("id", ""),
                            "field": "RelatedADR",
                        }
                    )
                related_tasks = row.get("depends_on", "")
                if not _is_empty(related_tasks) and not _parse_ids(related_tasks, r"T-\d{3}"):
                    issues.append(
                        {
                            "doc": "TASKS.md",
                            "feature_id": fid,
                            "id": row.get("id", ""),
                            "field": "DependsOn",
                        }
                    )
            if kind == "target_not_found":
                for plan_ref in _parse_ids(related_plan, r"F-\d{3}"):
                    if plan_ref not in plan_features:
                        issues.append(
                            {
                                "doc": "TASKS.md",
                                "feature_id": fid,
                                "id": row.get("id", ""),
                                "target": plan_ref,
                                "field": "RelatedPlan",
                            }
                        )
                for adr_ref in _parse_ids(related_adr, r"ADR-\d{3}"):
                    if adr_ref not in all_adr_ids:
                        issues.append(
                            {
                                "doc": "TASKS.md",
                                "feature_id": fid,
                                "id": row.get("id", ""),
                                "target": adr_ref,
                                "field": "RelatedADR",
                            }
                        )
        for row in decision_rows:
            if row.get("schema") != "new":
                continue
            related_tasks = row.get("related_tasks", "")
            if kind == "missing":
                if _is_empty(related_tasks):
                    issues.append(
                        {
                            "doc": "DECISIONS.md",
                            "feature_id": fid,
                            "id": row.get("adr_id", ""),
                            "field": "RelatedTasks",
                        }
                    )
                elif not _parse_ids(related_tasks, r"T-\d{3}"):
                    issues.append(
                        {
                            "doc": "DECISIONS.md",
                            "feature_id": fid,
                            "id": row.get("adr_id", ""),
                            "field": "RelatedTasks",
                        }
                    )
            if kind == "target_not_found":
                for task_ref in _parse_ids(related_tasks, r"T-\d{3}"):
                    if task_ref not in all_task_ids:
                        issues.append(
                            {
                                "doc": "DECISIONS.md",
                                "feature_id": fid,
                                "id": row.get("adr_id", ""),
                                "target": task_ref,
                                "field": "RelatedTasks",
                            }
                        )
    return issues


def _check_coverage(rule: ExecutableRule, ctx: AnalyzeContext) -> list[dict[str, Any]]:
    kind = str(rule.params.get("kind", "")).strip().lower()
    issues: list[dict[str, Any]] = []
    for fid in ctx.target_features:
        task_rows = ctx.tasks_by_feature.get(fid, [])
        decision_rows = ctx.decisions_by_feature.get(fid, [])
        if kind == "feature_no_task_or_reason" and not task_rows and not _plan_has_waiver(ctx, fid):
            issues.append({"doc": "TASKS.md", "feature_id": fid})
        if kind == "feature_no_adr_or_reason" and not decision_rows and not _plan_has_waiver(ctx, fid):
            issues.append({"doc": "DECISIONS.md", "feature_id": fid})
    return issues


def _check_quality_gates(rule: ExecutableRule, ctx: AnalyzeContext) -> list[dict[str, Any]]:
    kind = str(rule.params.get("kind", "")).strip().lower()
    issues: list[dict[str, Any]] = []
    if kind == "legacy_schema":
        if ctx.tasks_schema == "legacy":
            issues.append({"doc": "TASKS.md", "feature_id": None, "schema": "legacy"})
        if ctx.decisions_schema == "legacy":
            issues.append({"doc": "DECISIONS.md", "feature_id": None, "schema": "legacy"})
        return issues
    if kind == "task_no_adr_or_waiver":
        for fid in ctx.target_features:
            for row in ctx.tasks_by_feature.get(fid, []):
                if row.get("schema") != "new":
                    continue
                if _is_empty(row.get("related_adr")) and _is_empty(row.get("waiver_reason")):
                    issues.append(
                        {
                            "doc": "TASKS.md",
                            "feature_id": fid,
                            "id": row.get("id", ""),
                        }
                    )
    return issues


def _check_clarification_limit(rule: ExecutableRule, ctx: AnalyzeContext) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for fid in ctx.target_features:
        block = _feature_body(ctx.docs.get("README.md", ""), fid)
        count = block.count("NEEDS CLARIFICATION")
        if count > ctx.clarification_limit:
            issues.append(
                {
                    "doc": "README.md",
                    "feature_id": fid,
                    "count": count,
                    "limit": ctx.clarification_limit,
                }
            )
    return issues


def _check_dependency_cycle(rule: ExecutableRule, ctx: AnalyzeContext) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for fid in ctx.target_features:
        rows = ctx.tasks_by_feature.get(fid, [])
        if not rows:
            continue
        cycle = dependency_cycle(rows)
        if cycle:
            issues.append(
                {
                    "doc": "TASKS.md",
                    "feature_id": fid,
                    "cycle": ", ".join(cycle),
                }
            )
    return issues


def _check_boundary_violation(rule: ExecutableRule, ctx: AnalyzeContext) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    boundaries = list(rule.params.get("boundaries", []))
    for item in boundaries:
        doc = str(item.get("doc", "")).strip()
        if not doc:
            continue
        text = ctx.docs.get(doc, "")
        for pattern in item.get("forbidden_patterns", []):
            if re.search(pattern, text, re.I):
                issues.append(
                    {
                        "doc": doc,
                        "feature_id": None,
                        "pattern": pattern,
                    }
                )
                break
    return issues


def _check_commit_trace(rule: ExecutableRule, ctx: AnalyzeContext) -> list[dict[str, Any]]:
    if not ctx.enforce_commit_trace:
        return []
    kind = str(rule.params.get("kind", "missing")).strip().lower()
    issues: list[dict[str, Any]] = []
    if not is_git_repo(ctx.root):
        if kind == "missing":
            candidates = [fid for fid in (ctx.target_features or [ctx.feature]) if fid]
            for fid in candidates:
                issues.append(
                    {
                        "doc": ".git",
                        "feature_id": fid,
                        "reason": "git repository is unavailable",
                    }
                )
        return issues

    commits = ctx._cache.get("doc_commits")
    if commits is None:
        commits = recent_doc_commits(ctx.root, CORE_DOCS, ctx.git_log_depth)
        ctx._cache["doc_commits"] = commits

    dirty = ctx._cache.get("doc_dirty")
    if dirty is None:
        dirty = has_uncommitted_doc_changes(ctx.root, CORE_DOCS)
        ctx._cache["doc_dirty"] = dirty

    if kind == "dirty_worktree" and dirty:
        issues.append(
            {
                "doc": "*",
                "feature_id": None,
                "reason": "uncommitted core docs detected",
            }
        )
        return issues

    for fid in ctx.target_features:
        feature_commits = [c for c in commits if c.mentions_feature(fid)]
        if kind == "missing" and not feature_commits:
            issues.append({"doc": "git log", "feature_id": fid, "depth": ctx.git_log_depth})
        if kind == "template_invalid":
            if feature_commits and not any(
                commit_matches_template(commit, fid) for commit in feature_commits
            ):
                issues.append({"doc": "git log", "feature_id": fid})
    return issues


def _check_pr_template(rule: ExecutableRule, ctx: AnalyzeContext) -> list[dict[str, Any]]:
    kind = str(rule.params.get("kind", "missing")).strip().lower()
    issues: list[dict[str, Any]] = []
    path = ctx.root / PR_TEMPLATE_DOC
    if kind == "missing":
        if not path.exists():
            issues.append({"doc": PR_TEMPLATE_DOC, "feature_id": ctx.feature})
        return issues

    if not path.exists():
        return [{"doc": PR_TEMPLATE_DOC, "feature_id": ctx.feature}]

    text = ctx._cache.get("pr_template_text")
    if text is None:
        text = read_text(path)
        ctx._cache["pr_template_text"] = text

    if kind == "required_tokens":
        for token in rule.params.get("required_tokens", []):
            if token not in text:
                issues.append(
                    {
                        "doc": PR_TEMPLATE_DOC,
                        "feature_id": ctx.feature,
                        "token": token,
                    }
                )
    if kind == "required_patterns":
        for pattern in rule.params.get("required_patterns", []):
            if re.search(pattern, text, re.MULTILINE) is None:
                issues.append(
                    {
                        "doc": PR_TEMPLATE_DOC,
                        "feature_id": ctx.feature,
                        "pattern": pattern,
                    }
                )
    return issues
