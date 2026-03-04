---
description: Generate dependency-aware, executable tasks for a feature.
handoffs:
  - label: Analyze Context
    agent: specflow8.analyze
    prompt: Analyze consistency before implementation.
  - label: Start Implementation
    agent: specflow8.implement
    prompt: Execute tasks in dependency order.
scripts:
  sh: scripts/specflow8/bash/check-prerequisites.sh --json --include-tasks
  ps: scripts/specflow8/powershell/check-prerequisites.ps1 -Json -IncludeTasks
---

## Outline

1. Run prerequisite script and parse JSON context.
2. Load feature requirements and plan sections.
3. Generate tasks with fields:
   `ID/Title/Priority/Status/Owner/Due/DependsOn/DoD`
4. Ensure no dependency cycles.
5. After updating files, run `specflow8 commit --type gitflow --scope tasks --subject "tasks [<FEATURE_ID>] 本轮对话完成内容" --body "stage: tasks; feature: <FEATURE_ID>" --footer "Refs: <FEATURE_ID>"`.
