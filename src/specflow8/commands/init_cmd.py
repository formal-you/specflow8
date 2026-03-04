from __future__ import annotations

from pathlib import Path

import typer

from specflow8.config import Specflow8Config, load_config, save_config
from specflow8.workflow import ensure_agent_kit, ensure_docs, normalize_language


def register(app: typer.Typer) -> None:
    @app.command("init")
    def init_command(
        root: Path = typer.Option(
            Path("."), "--root", help="Project root where docs/config are managed."
        ),
        lang: str = typer.Option(
            "bilingual", "--lang", help="Template language: zh | en | bilingual."
        ),
        with_optional_docs: bool = typer.Option(
            False,
            "--with-optional-docs",
            help="Generate optional docs (RUNBOOK.md, INTERFACES.md).",
        ),
        force: bool = typer.Option(
            False,
            "--force",
            help="Overwrite existing managed docs using selected language templates.",
        ),
        with_agent_kit: bool = typer.Option(
            True,
            "--with-agent-kit/--no-agent-kit",
            help="Scaffold command templates and shell scripts for subagent orchestration.",
        ),
        script_variant: str = typer.Option(
            "both",
            "--script-variant",
            help="Script variant to scaffold: bash | powershell | both.",
        ),
    ) -> None:
        root = root.resolve()
        normalized = normalize_language(lang)
        if normalized != lang:
            raise typer.BadParameter(
                "Invalid --lang. Allowed values: zh | en | bilingual."
            )
        cfg = load_config(root)
        cfg.language = normalized
        if with_optional_docs:
            cfg.docs_optional_enabled = True
        save_config(root, cfg)

        created, skipped = ensure_docs(
            root=root,
            cfg=cfg,
            language=cfg.language,
            with_optional_docs=with_optional_docs,
            force=force,
        )
        kit_created: list[str] = []
        kit_skipped: list[str] = []
        if with_agent_kit:
            if script_variant not in {"bash", "powershell", "both"}:
                raise typer.BadParameter(
                    "Invalid --script-variant. Allowed values: bash | powershell | both."
                )
            kit_created, kit_skipped = ensure_agent_kit(
                root=root, force=force, script_variant=script_variant
            )
        typer.echo(f"Initialized specflow8 in: {root}")
        typer.echo(f"Created docs: {', '.join(created) if created else 'None'}")
        typer.echo(f"Skipped existing: {', '.join(skipped) if skipped else 'None'}")
        if with_agent_kit:
            typer.echo(
                f"Created agent-kit: {', '.join(kit_created) if kit_created else 'None'}"
            )
            typer.echo(
                f"Skipped agent-kit: {', '.join(kit_skipped) if kit_skipped else 'None'}"
            )
