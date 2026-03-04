---
description: Resolve requirement ambiguity markers before deep planning.
scripts:
  sh: scripts/specflow8/bash/check-prerequisites.sh --json
  ps: scripts/specflow8/powershell/check-prerequisites.ps1 -Json
---

Read `NEEDS CLARIFICATION` items from the target feature and resolve top-priority gaps first:

1. Scope
2. Security/compliance
3. UX-impacting behaviors

After clarification updates are written, run:
`specflow8 commit --type gitflow --scope clarify --subject "clarify [<FEATURE_ID>] 本轮对话完成内容" --body "stage: clarify; feature: <FEATURE_ID>" --footer "Refs: <FEATURE_ID>"`.
