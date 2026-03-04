#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"
require_specflow8

DESCRIPTION=""
TECH=""
WITH_TESTS="false"
FEATURE_ID=""
JSON="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --description) DESCRIPTION="$2"; shift 2 ;;
    --tech) TECH="$2"; shift 2 ;;
    --with-tests) WITH_TESTS="true"; shift ;;
    --feature-id) FEATURE_ID="$2"; shift 2 ;;
    --json) JSON="true"; shift ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [[ -z "$DESCRIPTION" ]]; then
  echo "ERROR: --description is required." >&2
  exit 1
fi

if [[ -n "$FEATURE_ID" ]]; then
  SPEC_OUT="$(run_specflow8 specify "$DESCRIPTION" --id "$FEATURE_ID")"
else
  SPEC_OUT="$(run_specflow8 specify "$DESCRIPTION")"
fi
printf '%s\n' "$SPEC_OUT"

EFFECTIVE_ID="$FEATURE_ID"
if [[ -z "$EFFECTIVE_ID" ]]; then
  EFFECTIVE_ID="$(printf '%s\n' "$SPEC_OUT" | sed -nE 's/^Feature specified:[[:space:]]*(F-[0-9]{3})$/\1/p' | head -n1)"
fi
if [[ -z "$EFFECTIVE_ID" ]]; then
  EFFECTIVE_ID="$(latest_feature_from_readme README.md)"
fi
if [[ -z "$EFFECTIVE_ID" ]]; then
  echo "ERROR: Unable to resolve feature id." >&2
  exit 1
fi

if [[ -n "$TECH" ]]; then
  run_specflow8 plan --feature "$EFFECTIVE_ID" "$TECH"
  if [[ "$WITH_TESTS" == "true" ]]; then
    run_specflow8 tasks --feature "$EFFECTIVE_ID" --with-tests
  else
    run_specflow8 tasks --feature "$EFFECTIVE_ID"
  fi
fi

if [[ "$JSON" == "true" ]]; then
  printf '{"FEATURE_ID":"%s","ROOT":"%s","UPDATED":["README.md","DOMAIN.md","PLAN.md"],"WITH_PLAN":%s,"WITH_TASKS":%s}\n' \
    "$EFFECTIVE_ID" "$(repo_root)" "$([[ -n "$TECH" ]] && echo true || echo false)" "$([[ -n "$TECH" ]] && echo true || echo false)"
fi
