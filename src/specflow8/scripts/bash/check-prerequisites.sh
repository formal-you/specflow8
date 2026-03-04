#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"
require_specflow8

ROOT="."
FEATURE_ID=""
INCLUDE_TASKS="false"
REQUIRE_TASKS="false"
JSON="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root) ROOT="$2"; shift 2 ;;
    --feature-id) FEATURE_ID="$2"; shift 2 ;;
    --include-tasks) INCLUDE_TASKS="true"; shift ;;
    --require-tasks) REQUIRE_TASKS="true"; shift ;;
    --json) JSON="true"; shift ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

pushd "$ROOT" >/dev/null
run_specflow8 check >/dev/null

if [[ -z "$FEATURE_ID" ]]; then
  FEATURE_ID="$(latest_feature_from_readme README.md)"
fi

RESULT_JSON="$(python - "$FEATURE_ID" "$INCLUDE_TASKS" "$REQUIRE_TASKS" "$(repo_root)" <<'PY'
import json
import re
import sys
from pathlib import Path

feature_id = sys.argv[1].strip()
include_tasks = sys.argv[2].lower() == "true"
require_tasks = sys.argv[3].lower() == "true"
root = Path(sys.argv[4])

core_docs = [
    "AGENTS.md",
    "README.md",
    "ARCHITECTURE.md",
    "DOMAIN.md",
    "STATE.md",
    "PLAN.md",
    "TASKS.md",
    "DECISIONS.md",
]
missing_docs = [d for d in core_docs if not (root / d).exists()]
available_docs = [d for d in core_docs if (root / d).exists()]

errors: list[str] = []
warnings: list[str] = []

if feature_id:
    readme = (root / "README.md").read_text(encoding="utf-8") if (root / "README.md").exists() else ""
    marker = f"<!-- specflow8:feature:{feature_id}:start -->"
    if marker not in readme:
        errors.append(f"Feature block not found in README.md: {feature_id}")
else:
    warnings.append("No feature id resolved from README.md.")

task_stats = {"total": 0, "done": 0, "pending": 0}
if (include_tasks or require_tasks) and feature_id and (root / "TASKS.md").exists():
    tasks_text = (root / "TASKS.md").read_text(encoding="utf-8")
    block_re = re.compile(
        rf"<!-- specflow8:feature:{re.escape(feature_id)}:start -->\n(.*?)\n<!-- specflow8:feature:{re.escape(feature_id)}:end -->",
        re.S,
    )
    block_m = block_re.search(tasks_text)
    if block_m:
        row_re = re.compile(
            r"^\|\s*T-\d{3}\s*\|\s*(?:.*?\|\s*){1,2}P[0-2]\s*\|\s*(todo|in_progress|done|blocked)\s*\|\s*.*?\|",
            re.M,
        )
        statuses = row_re.findall(block_m.group(1))
        task_stats["total"] = len(statuses)
        task_stats["done"] = len([s for s in statuses if s == "done"])
        task_stats["pending"] = task_stats["total"] - task_stats["done"]
    elif require_tasks:
        errors.append(f"Task block not found in TASKS.md: {feature_id}")

if require_tasks and task_stats["total"] == 0:
    errors.append("No tasks found while --require-tasks is set.")

if missing_docs:
    errors.append(f"Missing core docs: {', '.join(missing_docs)}")

payload = {
    "ROOT": str(root),
    "FEATURE_ID": feature_id or None,
    "AVAILABLE_DOCS": available_docs,
    "MISSING_DOCS": missing_docs,
    "TASKS": task_stats,
    "INCLUDE_TASKS": include_tasks,
    "REQUIRE_TASKS": require_tasks,
    "WARNINGS": warnings,
    "ERRORS": errors,
    "OK": len(errors) == 0,
}
print(json.dumps(payload, ensure_ascii=False))
PY
)"

if [[ "$JSON" == "true" ]]; then
  printf '%s\n' "$RESULT_JSON"
else
  python - "$RESULT_JSON" <<'PY'
import json
import sys

payload = json.loads(sys.argv[1])
print(f"Root: {payload['ROOT']}")
print(f"Feature: {payload['FEATURE_ID'] or 'N/A'}")
print(f"Core docs missing: {len(payload['MISSING_DOCS'])}")
if payload["INCLUDE_TASKS"] or payload["REQUIRE_TASKS"]:
    t = payload["TASKS"]
    print(f"Tasks: total={t['total']} done={t['done']} pending={t['pending']}")
for warning in payload["WARNINGS"]:
    print(f"WARNING: {warning}")
for err in payload["ERRORS"]:
    print(f"ERROR: {err}")
print(f"OK: {payload['OK']}")
PY
fi

ok="$(python - "$RESULT_JSON" <<'PY'
import json
import sys
print("true" if json.loads(sys.argv[1])["OK"] else "false")
PY
)"

popd >/dev/null
if [[ "$ok" != "true" ]]; then
  exit 1
fi
