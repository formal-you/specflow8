---
description: Produce stage checklist artifacts for requirements/readiness/ops.
scripts:
  sh: scripts/specflow8/bash/check-prerequisites.sh --json
  ps: scripts/specflow8/powershell/check-prerequisites.ps1 -Json
---

Generate checklist and link it to the target feature id.

After writing checklist artifacts, run:
`specflow8 commit --type docs --scope checklist --subject "checklist [<FEATURE_ID>] 本轮对话完成内容" --body "stage: checklist; feature: <FEATURE_ID>" --footer "Refs: <FEATURE_ID>"`.

