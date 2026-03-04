from __future__ import annotations

import re
from pathlib import Path

from .constants import FEATURE_END_FMT, FEATURE_START_FMT, MANUAL_END, MANUAL_START


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def feature_block_regex(feature_id: str) -> re.Pattern[str]:
    start = re.escape(FEATURE_START_FMT.format(feature_id=feature_id))
    end = re.escape(FEATURE_END_FMT.format(feature_id=feature_id))
    return re.compile(rf"{start}\n(.*?)\n{end}", re.S)


def find_feature_ids(content: str) -> list[str]:
    return sorted(set(re.findall(r"<!-- specflow8:feature:(F-\d{3}):start -->", content)))


def extract_feature_block(content: str, feature_id: str) -> str | None:
    m = feature_block_regex(feature_id).search(content)
    if not m:
        return None
    return m.group(1)


def extract_manual_section(block_body: str) -> str | None:
    pattern = re.compile(
        rf"{re.escape(MANUAL_START)}\n(.*?)\n{re.escape(MANUAL_END)}", re.S
    )
    m = pattern.search(block_body)
    if not m:
        return None
    return f"{MANUAL_START}\n{m.group(1)}\n{MANUAL_END}"


def build_feature_block(feature_id: str, title: str, body: str) -> str:
    start = FEATURE_START_FMT.format(feature_id=feature_id)
    end = FEATURE_END_FMT.format(feature_id=feature_id)
    normalized_body = body.strip()
    return f"{start}\n## [{feature_id}] {title}\n{normalized_body}\n{end}"


def upsert_feature_block(content: str, feature_id: str, title: str, body: str) -> str:
    existing = extract_feature_block(content, feature_id)
    manual = extract_manual_section(existing or "")
    final_body = body.strip()
    if manual and MANUAL_START not in final_body:
        final_body = f"{final_body}\n\n{manual}"

    block = build_feature_block(feature_id, title, final_body)
    pattern = feature_block_regex(feature_id)
    if pattern.search(content):
        updated = pattern.sub(block, content)
        return _normalize_spacing(updated)

    if content.strip():
        return _normalize_spacing(f"{content.rstrip()}\n\n{block}\n")
    return f"{block}\n"


def upsert_named_section(content: str, key: str, section_body: str) -> str:
    start = f"<!-- specflow8:{key}:start -->"
    end = f"<!-- specflow8:{key}:end -->"
    replacement = f"{start}\n{section_body.strip()}\n{end}"
    pattern = re.compile(rf"{re.escape(start)}\n(.*?)\n{re.escape(end)}", re.S)
    if pattern.search(content):
        return _normalize_spacing(pattern.sub(replacement, content))
    if content.strip():
        return _normalize_spacing(f"{content.rstrip()}\n\n{replacement}\n")
    return f"{replacement}\n"


def _normalize_spacing(content: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", content.strip()) + "\n"
