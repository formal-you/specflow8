# DECISIONS.md

## Document Meta / 文档元信息
- Owner: Engineering / Owner: 工程团队
- Last Updated: 2026-03-05
- Source of Truth: ADR-style decision records / Source of Truth: ADR 风格决策记录
- Review Cadence: Per major decision / Review Cadence: 每次关键决策
- Upstream/Downstream:
  - Upstream: PLAN.md, ARCHITECTURE.md
  - Downstream: TASKS.md, STATE.md

## ADR Trigger Policy / ADR 触发策略
- API/schema contract change.
- Data model/migration strategy change.
- Security/compliance posture change.
- Governance gate behavior change.

<!-- specflow8:feature:F-001:start -->
## [F-001] Governance Engine Foundation Decisions
| ADR-ID | Feature | Date | Context | Decision | Alternatives | Consequences | RelatedTasks | Status | Supersedes | Verification |
|---|---|---|---|---|---|---|---|---|---|---|
| ADR-001 | F-001 | 2026-03-05 | Governance checks must be configurable without code rewrites | Adopt YAML rule files + schema validation + stage-aware rule engine | Hardcoded checks in Python modules | Rules become auditable and evolvable; schema discipline required | T-001,T-002 | accepted | None | tests: `uv run pytest` + commit:11cb7e7 |
| ADR-002 | F-001 | 2026-03-05 | Governance needs machine-checkable commit evidence | Enforce Conventional Commit with `stage`, `feature`, and `Refs` fields | Keep free-form commits and rely on manual review | Commit history becomes queryable for governance audits | T-003 | accepted | None | commit:03c0b2b + `specflow8 analyze --enforce-commit-trace` |
<!-- specflow8:feature:F-001:end -->

<!-- specflow8:feature:F-000:start -->
## [F-000] PR Gate and Root Governance Hardening Decisions
| ADR-ID | Feature | Date | Context | Decision | Alternatives | Consequences | RelatedTasks | Status | Supersedes | Verification |
|---|---|---|---|---|---|---|---|---|---|---|
| ADR-003 | F-000 | 2026-03-05 | Commit trace chain still lacked PR-layer enforcement | Introduce PR template checks (`PR_TEMPLATE_MISSING`, `PR_TEMPLATE_FIELD_MISSING`) | Depend only on human review and PR etiquette | PR quality gate becomes rule-driven and enforceable by analyzer | T-004,T-005 | accepted | None | commit:518468f, commit:0a9258e |
| ADR-004 | F-000 | 2026-03-05 | Root docs were template-heavy and not operational | Convert root docs to project self-governance records backed by git evidence | Keep generic templates and rely on verbal process | Team can use specflow8 to govern specflow8 itself with concrete baseline | T-006 | accepted | None | commit:3ab43bd |
<!-- specflow8:feature:F-000:end -->
