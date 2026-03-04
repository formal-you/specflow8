---
description: Execute workflow from tasks with dependency ordering.
scripts:
  sh: scripts/specflow8/bash/check-prerequisites.sh --json --require-tasks --include-tasks
  ps: scripts/specflow8/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks
---

## Outline

1. Run prerequisite script and verify required artifacts exist.
2. Parse `TASKS.md` for selected feature.
3. Respect `DependsOn` order.
4. Update task status and write execution snapshot to `STATE.md`.
5. After updating files, run `specflow8 commit --type docs --scope implement --subject "implement [<FEATURE_ID>] 本轮对话完成内容" --body "stage: implement; feature: <FEATURE_ID>" --footer "Refs: <FEATURE_ID>"`.

