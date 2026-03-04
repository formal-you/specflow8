#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"
require_specflow8

ROOT="."
FEATURE_ID=""
JSON="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root) ROOT="$2"; shift 2 ;;
    --feature-id) FEATURE_ID="$2"; shift 2 ;;
    --json) JSON="true"; shift ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

pushd "$ROOT" >/dev/null
run_specflow8 check >/dev/null

if [[ -z "$FEATURE_ID" ]]; then
  FEATURE_ID="$(latest_feature_from_readme README.md)"
fi

if [[ -z "$FEATURE_ID" ]]; then
  echo "ERROR: No feature id found. Run `specflow8 specify` first or pass --feature-id." >&2
  popd >/dev/null
  exit 1
fi

declare -a required=("README.md" "DOMAIN.md" "PLAN.md" "ARCHITECTURE.md")
missing=()
for doc in "${required[@]}"; do
  [[ -f "$doc" ]] || missing+=("$doc")
done

if [[ "${#missing[@]}" -gt 0 ]]; then
  echo "ERROR: Missing required docs: ${missing[*]}" >&2
  popd >/dev/null
  exit 1
fi

if [[ "$JSON" == "true" ]]; then
  python - "$FEATURE_ID" "$(repo_root)" <<'PY'
import json
import sys

feature_id = sys.argv[1]
root = sys.argv[2]
payload = {
    "FEATURE_ID": feature_id,
    "ROOT": root,
    "AVAILABLE_DOCS": ["README.md", "DOMAIN.md", "PLAN.md", "ARCHITECTURE.md"],
    "UPDATED_TARGETS": ["ARCHITECTURE.md", "PLAN.md"],
}
print(json.dumps(payload, ensure_ascii=False))
PY
else
  echo "Feature: $FEATURE_ID"
  echo "Plan context ready: README.md, DOMAIN.md, PLAN.md, ARCHITECTURE.md"
fi

popd >/dev/null
