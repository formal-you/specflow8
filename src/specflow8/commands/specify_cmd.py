from __future__ import annotations

from pathlib import Path

import typer

from specflow8.config import load_config
from specflow8.validators import validate_feature_id
from specflow8.workflow import (
    clarification_candidates,
    ensure_docs,
    next_feature_id,
    slug_title,
    today,
    upsert_doc_feature,
)


def register(app: typer.Typer) -> None:
    @app.command("specify")
    def specify_command(
        feature_description: str = typer.Argument(
            ..., help="Natural-language feature description."
        ),
        id: str | None = typer.Option(
            None, "--id", help="Feature ID (default auto-generated, e.g. F-001)."
        ),
        max_clarifications: int | None = typer.Option(
            None, "--max-clarifications", min=0, max=10
        ),
    ) -> None:
        root = Path(".").resolve()
        cfg = load_config(root)
        ensure_docs(root, cfg, cfg.language, cfg.docs_optional_enabled)

        feature_id = id or next_feature_id(root)
        if not validate_feature_id(feature_id):
            raise typer.BadParameter("Feature ID must match F-XXX.")

        limit = (
            max_clarifications
            if max_clarifications is not None
            else cfg.clarification_limit
        )
        clarifications = clarification_candidates(feature_description, limit=limit)
        title = slug_title(feature_description)

        clar_lines = (
            "\n".join(f"- {item}" for item in clarifications)
            if clarifications
            else "- None / 无"
        )

        readme_body = f"""### Summary / 概述
- Created: {today()}
- Input: {feature_description}

### Scope / 范围
- This block captures WHAT/WHY for `{feature_id}`.
- 此分节记录 `{feature_id}` 的需求目标与价值，不包含实现细节。

### Clarifications / 待澄清
{clar_lines}

### Success Signals / 成功信号
- Users can validate MVP outcomes independently.
- 该特性可在不依赖后续阶段时进行独立演示。"""

        domain_body = f"""### Domain Intent / 领域意图
- Feature: {title}
- Business Value: 明确业务目标、角色边界、关键约束。

### Actors / 参与者
- Primary actor(s): [To refine in follow-up planning]
- Secondary actor(s): [To refine in follow-up planning]

### Rules / 规则
- Use this section for domain rules only (non-implementation).
- 仅记录业务规则，不记录技术实现。"""

        plan_body = f"""### Phase Intent / 阶段意图
- Feature: {title}
- Status: draft
- Next: run `specflow8 plan --feature {feature_id} "<tech and constraints>"`

### Requirement Highlights / 需求重点
- {feature_description}

### Open Questions / 开放问题
{clar_lines}"""

        upsert_doc_feature(root, "README.md", feature_id, title, readme_body)
        upsert_doc_feature(root, "DOMAIN.md", feature_id, title, domain_body)
        upsert_doc_feature(root, "PLAN.md", feature_id, title, plan_body)

        typer.echo(f"Feature specified: {feature_id}")
        typer.echo("Updated docs: README.md, DOMAIN.md, PLAN.md")
