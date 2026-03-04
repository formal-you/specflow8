from __future__ import annotations

from pathlib import Path

import typer

from specflow8.config import load_config
from specflow8.workflow import (
    ensure_docs,
    latest_feature_id,
    slug_title,
    today,
    upsert_doc_feature,
)


def register(app: typer.Typer) -> None:
    @app.command("plan")
    def plan_command(
        tech_and_constraints: str = typer.Argument(
            ..., help="Technical approach, stack and constraints."
        ),
        feature: str | None = typer.Option(
            None, "--feature", help="Feature ID (defaults to latest)."
        ),
    ) -> None:
        root = Path(".").resolve()
        cfg = load_config(root)
        ensure_docs(root, cfg, cfg.language, cfg.docs_optional_enabled)

        feature_id = feature or latest_feature_id(root)
        if not feature_id:
            raise typer.BadParameter("No feature found. Run `specflow8 specify` first.")

        title = slug_title(tech_and_constraints)

        architecture_body = f"""### Technical Context / 技术上下文
- Date: {today()}
- Input: {tech_and_constraints}

### Structure Decision / 结构决策
- Root-doc model with feature sections (`{feature_id}`) is retained.
- 根文档 + Feature 分节模型继续保持。

### Constraints / 约束
- Keep architecture notes high-level.
- 详细契约与执行拆解由 `tasks` 和 `decide` 补充。"""

        plan_body = f"""### Technical Plan / 技术计划
- Feature: {feature_id}
- Proposed stack and constraints:
  - {tech_and_constraints}

### Deliverables / 交付物
- Update `ARCHITECTURE.md` feature section
- Create tasks via `specflow8 tasks --feature {feature_id}`
- Record tradeoffs via `specflow8 decide --feature {feature_id} ...`
"""

        upsert_doc_feature(root, "ARCHITECTURE.md", feature_id, title, architecture_body)
        upsert_doc_feature(root, "PLAN.md", feature_id, title, plan_body)
        typer.echo(f"Planning completed for {feature_id}")
        typer.echo("Updated docs: ARCHITECTURE.md, PLAN.md")
