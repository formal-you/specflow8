---
description: Create technical plan sections from feature requirements.
handoffs:
  - label: Generate Tasks
    agent: specflow8.tasks
    prompt: Break down this plan into executable tasks.
scripts:
  sh: scripts/specflow8/bash/setup-plan.sh --json
  ps: scripts/specflow8/powershell/setup-plan.ps1 -Json
---

## Outline

1. Run setup script and parse JSON (`FEATURE_ID`, `AVAILABLE_DOCS`).
2. Read feature sections in `README.md`, `DOMAIN.md`, and `PLAN.md`.
3. Update:
   - `ARCHITECTURE.md` feature block
   - `PLAN.md` feature block (technical plan)
4. Report unresolved unknowns and next command.
5. After updating files, run `specflow8 commit --type docs --scope plan --subject "plan [<FEATURE_ID>] 本轮对话完成内容" --body "stage: plan; feature: <FEATURE_ID>" --footer "Refs: <FEATURE_ID>"`.

