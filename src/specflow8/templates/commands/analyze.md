---
description: Run cross-document consistency analysis for one feature or all features.
scripts:
  sh: scripts/specflow8/bash/check-prerequisites.sh --json
  ps: scripts/specflow8/powershell/check-prerequisites.ps1 -Json
---

## Checks

- Core docs existence
- Feature marker balance
- Traceability links (Feature-Task-ADR)
- Clarification limit
- Task dependency cycles
- Commit trace validation (`--mode`, `--enforce-commit-trace`, `--json`)
- After analysis notes are updated, run `specflow8 commit --type gitflow --scope analyze --subject "analyze [<FEATURE_ID>] 本轮对话完成内容" --body "stage: analyze; feature: <FEATURE_ID>" --footer "Refs: <FEATURE_ID>"`.
