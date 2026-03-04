#!/usr/bin/env bash
set -euo pipefail

require_specflow8() {
  if ! command -v specflow8 >/dev/null 2>&1 && ! command -v specflow8.exe >/dev/null 2>&1; then
    echo "ERROR: specflow8 command not found in PATH." >&2
    exit 1
  fi
}

run_specflow8() {
  if command -v specflow8 >/dev/null 2>&1; then
    specflow8 "$@"
    return
  fi
  if command -v specflow8.exe >/dev/null 2>&1; then
    specflow8.exe "$@"
    return
  fi
  echo "ERROR: specflow8 command not found in PATH." >&2
  exit 1
}

repo_root() {
  pwd
}

latest_feature_from_readme() {
  local readme="${1:-README.md}"
  if [[ ! -f "$readme" ]]; then
    return 0
  fi
  grep -oE '<!-- specflow8:feature:(F-[0-9]{3}):start -->' "$readme" \
    | sed -E 's/.*feature:(F-[0-9]{3}):start.*/\1/' \
    | tail -n1
}
