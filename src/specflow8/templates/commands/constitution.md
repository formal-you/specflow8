---
description: Update project constitution/governance guardrails.
scripts:
  sh: scripts/specflow8/bash/check-prerequisites.sh --json --paths-only
  ps: scripts/specflow8/powershell/check-prerequisites.ps1 -Json -PathsOnly
---

Update governance blocks in `AGENTS.md` and ensure consistency with the 8-document index.

After governance edits are complete, run:
`specflow8 commit --type gitflow --scope constitution --subject "constitution [N/A] 本轮对话完成内容" --body "stage: constitution; feature: N/A" --footer "Refs: N/A"`.
