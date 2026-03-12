from __future__ import annotations

import json
from pathlib import Path

import typer

from specflow8.config import Specflow8Config, load_config, save_config
from specflow8.constants import SCALES, PROJECT_TYPES
from specflow8.profiles import resolve_profile
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
        # ── NEW: Profile options ──────────────────────────────────────
        scale: str | None = typer.Option(
            None,
            "--scale",
            help="Project scale: small (3-5 people) | medium (10-20) | large (20+).",
        ),
        project_type: str | None = typer.Option(
            None,
            "--type",
            help="Project type: monolith | distributed | multi-team.",
        ),
        profile: str | None = typer.Option(
            None,
            "--profile",
            help="Profile shorthand: e.g. 'small-monolith'. Overrides --scale/--type.",
        ),
        # ── Existing options (unchanged) ─────────────────────────────
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
        json_output: bool = typer.Option(
            False, "--json", help="Emit structured JSON output (AI Agent friendly)."
        ),
    ) -> None:
        root = root.resolve()
        normalized = normalize_language(lang)
        if normalized != lang:
            raise typer.BadParameter(
                "Invalid --lang. Allowed values: zh | en | bilingual."
            )

        # Resolve profile from --profile shorthand or --scale/--type pair
        if profile:
            parts = profile.split("-", 1)
            if len(parts) != 2:
                raise typer.BadParameter(
                    "Invalid --profile. Expected 'scale-type', e.g. 'small-monolith'."
                )
            _scale, _type = parts
        else:
            _scale = scale or "medium"
            _type = project_type or "monolith"

        if _scale not in SCALES:
            raise typer.BadParameter(
                f"Invalid --scale `{_scale}`. Allowed: {' | '.join(SCALES)}."
            )
        if _type not in PROJECT_TYPES:
            raise typer.BadParameter(
                f"Invalid --type `{_type}`. Allowed: {' | '.join(PROJECT_TYPES)}."
            )

        preset = resolve_profile(_scale, _type)

        # Load (or create) config, then apply profile defaults
        cfg = load_config(root)
        cfg.language = normalized
        cfg.version = "0.2"
        cfg.project.scale = preset.scale
        cfg.project.type = preset.project_type
        cfg.governance_mode = preset.governance_mode
        cfg.docs_core = list(preset.docs_core)
        cfg.clarification_limit = preset.clarification_limit
        cfg.analyze.enforce_commit_trace = preset.enforce_commit_trace
        cfg.governance_chain.required_links = list(preset.chain_required)
        cfg.governance_chain.optional_links = list(preset.chain_optional)
        if with_optional_docs:
            cfg.docs_optional_enabled = True
        save_config(root, cfg)

        created, skipped = ensure_docs(
            root=root,
            cfg=cfg,
            language=cfg.language,
            with_optional_docs=with_optional_docs,
            include_meta_docs=True,
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

        next_steps = [
            f'Run `specflow8 specify "<feature description>"` to create the first feature.',
            f"Run `specflow8 analyze --mode {preset.governance_mode} --all` to validate governance.",
        ]

        if json_output:
            typer.echo(
                json.dumps(
                    {
                        "profile": preset.profile_id,
                        "scale": preset.scale,
                        "type": preset.project_type,
                        "governance_mode": preset.governance_mode,
                        "created_docs": created,
                        "skipped_docs": skipped,
                        "created_agent_kit": kit_created,
                        "governance_chain": {
                            "required": preset.chain_required,
                            "optional": preset.chain_optional,
                        },
                        "next_steps": next_steps,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            typer.echo(f"Initialized specflow8 in: {root}")
            typer.echo(f"Profile:      {preset.profile_id}")
            typer.echo(f"Mode:         {preset.governance_mode}")
            typer.echo(f"Created docs: {', '.join(created) if created else 'None'}")
            typer.echo(f"Skipped:      {', '.join(skipped) if skipped else 'None'}")
            if with_agent_kit:
                typer.echo(
                    f"Created agent-kit: {', '.join(kit_created) if kit_created else 'None'}"
                )
                typer.echo(
                    f"Skipped agent-kit: {', '.join(kit_skipped) if kit_skipped else 'None'}"
                )
            typer.echo("\nNext steps:")
            for step in next_steps:
                typer.echo(f"  • {step}")
