from __future__ import annotations

import re
import shutil
from datetime import date, timedelta
from pathlib import Path

from jinja2 import Template

from .config import Specflow8Config
from .constants import CORE_DOCS, OPTIONAL_DOCS, PR_TEMPLATE_DOC
from .io_markdown import (
    find_feature_ids,
    read_text,
    upsert_feature_block,
    upsert_named_section,
    write_text,
)

TEMPLATE_MAP = {
    "AGENTS.md": "core/AGENTS.md.j2",
    "README.md": "core/README.md.j2",
    "ARCHITECTURE.md": "core/ARCHITECTURE.md.j2",
    "DOMAIN.md": "core/DOMAIN.md.j2",
    "STATE.md": "core/STATE.md.j2",
    "PLAN.md": "core/PLAN.md.j2",
    "TASKS.md": "core/TASKS.md.j2",
    "DECISIONS.md": "core/DECISIONS.md.j2",
    "RUNBOOK.md": "optional/RUNBOOK.md.j2",
    "INTERFACES.md": "optional/INTERFACES.md.j2",
    PR_TEMPLATE_DOC: "meta/PULL_REQUEST_TEMPLATE.md.j2",
}


def today() -> str:
    return date.today().isoformat()


def template_root() -> Path:
    return Path(__file__).resolve().parent / "templates"


def rule_root() -> Path:
    return Path(__file__).resolve().parent / "rules"


def commands_template_root() -> Path:
    return template_root() / "commands"


def scripts_asset_root() -> Path:
    return Path(__file__).resolve().parent / "scripts"


def render_template(rel_path: str, context: dict[str, object]) -> str:
    source_path = template_root() / rel_path
    source = source_path.read_text(encoding="utf-8")
    return Template(source).render(**context)


def normalize_language(language: str) -> str:
    lang = (language or "").strip().lower()
    if lang in {"zh", "en", "bilingual"}:
        return lang
    return "bilingual"


def make_translator(language: str):
    lang = normalize_language(language)

    def tr(zh: str, en: str) -> str:
        if lang == "zh":
            return zh
        if lang == "en":
            return en
        return f"{en} / {zh}"

    return tr


def ensure_docs(
    root: Path,
    cfg: Specflow8Config,
    language: str,
    with_optional_docs: bool,
    include_meta_docs: bool = False,
    force: bool = False,
) -> tuple[list[str], list[str]]:
    created: list[str] = []
    skipped: list[str] = []

    lang = normalize_language(language)
    context = {"today": today(), "language": lang, "tr": make_translator(lang)}
    required_docs = list(cfg.docs_core)
    if include_meta_docs:
        required_docs.append(PR_TEMPLATE_DOC)
    if with_optional_docs or cfg.docs_optional_enabled:
        required_docs.extend(OPTIONAL_DOCS)

    for doc in required_docs:
        target = root / doc
        if target.exists() and not force:
            skipped.append(doc)
            continue
        rel = TEMPLATE_MAP[doc]
        write_text(target, render_template(rel, context))
        created.append(doc)
    return created, skipped


def ensure_agent_kit(
    root: Path,
    force: bool = False,
    script_variant: str = "both",
) -> tuple[list[str], list[str]]:
    created: list[str] = []
    skipped: list[str] = []

    command_dst = root / ".specflow8" / "templates" / "commands"
    command_src = commands_template_root()
    for src in sorted(command_src.glob("*.md")):
        rel = str(Path(".specflow8") / "templates" / "commands" / src.name)
        dst = command_dst / src.name
        if dst.exists() and not force:
            skipped.append(rel)
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        created.append(rel)

    variants = ["bash", "powershell"] if script_variant == "both" else [script_variant]
    scripts_src_root = scripts_asset_root()
    for variant in variants:
        src_dir = scripts_src_root / variant
        if not src_dir.exists():
            continue
        dst_dir = root / "scripts" / "specflow8" / variant
        ext = "*.sh" if variant == "bash" else "*.ps1"
        for src in sorted(src_dir.glob(ext)):
            rel = str(Path("scripts") / "specflow8" / variant / src.name)
            dst = dst_dir / src.name
            if dst.exists() and not force:
                skipped.append(rel)
                continue
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
            created.append(rel)

    return created, skipped


def all_feature_ids(root: Path) -> list[str]:
    ids: set[str] = set()
    for doc in CORE_DOCS + OPTIONAL_DOCS:
        path = root / doc
        if not path.exists():
            continue
        ids.update(find_feature_ids(read_text(path)))
    return sorted(ids)


def next_feature_id(root: Path) -> str:
    ids = all_feature_ids(root)
    if not ids:
        return "F-001"
    n = max(int(fid.split("-")[1]) for fid in ids)
    return f"F-{n + 1:03d}"


def latest_feature_id(root: Path) -> str | None:
    ids = all_feature_ids(root)
    if not ids:
        return None
    return ids[-1]


def slug_title(text: str, max_words: int = 6) -> str:
    words = re.findall(r"[A-Za-z0-9\u4e00-\u9fff_-]+", text)
    if not words:
        return "Untitled Feature"
    return " ".join(words[:max_words])


def clarification_candidates(description: str, limit: int) -> list[str]:
    desc = description.lower()
    candidates: list[str] = []
    if "user" not in desc and "role" not in desc and "permission" not in desc:
        candidates.append(
            "[NEEDS CLARIFICATION: 主要用户角色和权限边界 / primary user roles and permissions?]"
        )
    if "performance" not in desc and "p95" not in desc and "latency" not in desc:
        candidates.append(
            "[NEEDS CLARIFICATION: 性能目标（例如 p95 延迟）/ performance targets (e.g. p95 latency)?]"
        )
    if "security" not in desc and "compliance" not in desc and "privacy" not in desc:
        candidates.append(
            "[NEEDS CLARIFICATION: 安全与合规要求 / security and compliance constraints?]"
        )
    if "scope" not in desc and "mvp" not in desc:
        candidates.append(
            "[NEEDS CLARIFICATION: MVP 范围边界 / MVP scope boundaries?]"
        )
    return candidates[:limit]


def upsert_doc_feature(
    root: Path,
    doc_name: str,
    feature_id: str,
    title: str,
    body: str,
) -> None:
    path = root / doc_name
    current = read_text(path)
    updated = upsert_feature_block(current, feature_id=feature_id, title=title, body=body)
    write_text(path, updated)


def upsert_constitution(root: Path, principles: str, strict: bool) -> None:
    path = root / "AGENTS.md"
    current = read_text(path)
    mode = "Strict mode enabled: constitutional checks are blocking." if strict else "Strict mode disabled: constitutional checks are advisory."
    body = (
        "## Constitutional Principles\n"
        f"- Updated: {today()}\n"
        f"- Enforcement: {mode}\n\n"
        "### Principles\n"
        f"{principles.strip()}\n"
    )
    updated = upsert_named_section(current, key="constitution", section_body=body)
    write_text(path, updated)


def next_adr_id(root: Path) -> str:
    content = read_text(root / "DECISIONS.md")
    found = [int(x) for x in re.findall(r"ADR-(\d{3})", content)]
    n = max(found) + 1 if found else 1
    return f"ADR-{n:03d}"


def next_task_id(existing_rows: list[dict[str, str]]) -> int:
    if not existing_rows:
        return 1
    return max(int(r["id"].split("-")[1]) for r in existing_rows) + 1


def default_due(days: int = 7) -> date:
    return date.today() + timedelta(days=days)
