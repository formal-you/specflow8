---
description: Create or update a feature specification from a short natural-language request.
handoffs:
  - label: Build Technical Plan
    agent: specflow8.plan
    prompt: Create a plan for this feature.
  - label: Clarify Requirement Gaps
    agent: specflow8.clarify
    prompt: Clarify unresolved requirement markers.
scripts:
  sh: scripts/specflow8/bash/create-new-feature.sh --json --description "{ARGS}"
  ps: scripts/specflow8/powershell/create-new-feature.ps1 -Json -Description "{ARGS}"
---

## User Input

```text
$ARGUMENTS
```

Run the stage script first, parse JSON output, then fill/update feature blocks in:

- `README.md`
- `DOMAIN.md`
- `PLAN.md`

Rules:

1. Keep at most 3 `NEEDS CLARIFICATION` markers.
2. Focus on WHAT/WHY, avoid implementation details.
3. Return feature id and next-stage command in the final message.
4. After updating files, run `specflow8 commit --type gitflow --scope specify --subject "specify [<FEATURE_ID>] 本轮对话完成内容" --body "stage: specify; feature: <FEATURE_ID>" --footer "Refs: <FEATURE_ID>"`.
