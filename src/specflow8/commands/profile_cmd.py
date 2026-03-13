from __future__ import annotations

import json
from pathlib import Path

import typer

from specflow8.config import load_config, save_config
from specflow8.constants import PROJECT_TYPES, SCALES
from specflow8.profiles import (
    list_profiles,
    resolve_profile,
    resolve_profile_from_id,
    upgrade_profile,
)
from specflow8.workflow import ensure_docs, normalize_language


def register(app: typer.Typer) -> None:
    profile_app = typer.Typer(help="Manage project governance profile (scale × type).")
    app.add_typer(profile_app, name="profile")

    @profile_app.command("show")
    def profile_show(
        root: Path = typer.Option(
            Path("."), "--root", help="Project root directory."
        ),
        json_output: bool = typer.Option(
            False, "--json", help="Emit structured JSON output."
        ),
    ) -> None:
        """Show the current governance profile and its settings."""
        root = root.resolve()
        cfg = load_config(root)
        preset = resolve_profile(cfg.project.scale, cfg.project.type)

        if json_output:
            _emit_json({
                "profile": preset.profile_id,
                "scale": preset.scale,
                "type": preset.project_type,
                "governance_mode": preset.governance_mode,
                "docs_core": preset.docs_core,
                "enforce_commit_trace": preset.enforce_commit_trace,
                "clarification_limit": preset.clarification_limit,
                "chain_required": preset.chain_required,
                "chain_optional": preset.chain_optional,
                "rule_overrides": preset.rule_overrides,
            })
        else:
            typer.echo(f"Profile:           {preset.profile_id}")
            typer.echo(f"Scale:             {preset.scale}")
            typer.echo(f"Type:              {preset.project_type}")
            typer.echo(f"Governance mode:   {preset.governance_mode}")
            typer.echo(f"Enforce commit:    {preset.enforce_commit_trace}")
            typer.echo(f"Clarif. limit:     {preset.clarification_limit}")
            typer.echo(f"Docs required:     {', '.join(preset.docs_core)}")
            typer.echo(f"Chain (required):  {', '.join(preset.chain_required)}")
            typer.echo(f"Chain (optional):  {', '.join(preset.chain_optional)}")
            if preset.rule_overrides:
                typer.echo("Rule overrides:")
                for rule_id, sev_map in preset.rule_overrides.items():
                    typer.echo(f"  {rule_id}: {sev_map}")

    @profile_app.command("list")
    def profile_list(
        root: Path = typer.Option(
            Path("."), "--root", help="Project root directory."
        ),
        json_output: bool = typer.Option(
            False, "--json", help="Emit structured JSON output."
        ),
    ) -> None:
        """List all available governance profiles."""
        _root = root.resolve()  # noqa: F841 — reserved for future use
        profiles = list_profiles()
        if json_output:
            items = []
            for pid in profiles:
                p = resolve_profile_from_id(pid)
                items.append(
                    {
                        "profile": p.profile_id,
                        "scale": p.scale,
                        "type": p.project_type,
                        "governance_mode": p.governance_mode,
                        "doc_count": len(p.docs_core),
                    }
                )
            _emit_json(items)
        else:
            typer.echo(f"{'Profile':<25} {'Mode':<12} {'Docs'}")
            typer.echo("-" * 55)
            for pid in profiles:
                p = resolve_profile_from_id(pid)
                typer.echo(f"{p.profile_id:<25} {p.governance_mode:<12} {len(p.docs_core)} docs")

    @profile_app.command("upgrade")
    def profile_upgrade(
        root: Path = typer.Option(
            Path("."), "--root", help="Project root directory."
        ),
        scale: str | None = typer.Option(
            None, "--scale", help="New scale: small | medium | large."
        ),
        project_type: str | None = typer.Option(
            None, "--type", help="New project type: monolith | distributed | multi-team."
        ),
        lang: str | None = typer.Option(
            None, "--lang", help="Language for newly generated docs: zh | en | bilingual."
        ),
        json_output: bool = typer.Option(
            False, "--json", help="Emit structured JSON output."
        ),
        dry_run: bool = typer.Option(
            False, "--dry-run", help="Preview changes without applying them."
        ),
        allow_downgrade: bool = typer.Option(
            False, "--allow-downgrade", help="Allow downgrading to a lower tier."
        ),
    ) -> None:
        """Upgrade the project governance profile to a higher tier."""
        root = root.resolve()
        cfg = load_config(root)
        current = resolve_profile(cfg.project.scale, cfg.project.type)
        if scale is not None and scale not in SCALES:
            raise typer.BadParameter(
                f"Invalid --scale `{scale}`. Allowed: {' | '.join(SCALES)}."
            )
        if project_type is not None and project_type not in PROJECT_TYPES:
            raise typer.BadParameter(
                f"Invalid --type `{project_type}`. Allowed: {' | '.join(PROJECT_TYPES)}."
            )
        try:
            new_preset, new_docs = upgrade_profile(
                current,
                new_scale=scale,
                new_type=project_type,
                allow_downgrade=allow_downgrade,
            )
        except ValueError as exc:
            raise typer.BadParameter(str(exc)) from exc

        if new_preset.profile_id == current.profile_id:
            typer.echo("Profile is already at the requested tier. No changes needed.")
            return

        if json_output:
            _emit_json({
                "old_profile": current.profile_id,
                "new_profile": new_preset.profile_id,
                "new_docs": new_docs,
                "applied": not dry_run,
            })
        else:
            typer.echo(f"Upgrading: {current.profile_id} → {new_preset.profile_id}")
            if new_docs:
                typer.echo(f"New documents to create: {', '.join(new_docs)}")
            else:
                typer.echo("No new documents required.")
            if dry_run:
                typer.echo("Dry-run mode: no changes applied.")
                return

        if dry_run:
            return

        # Apply: update config
        cfg.project.scale = new_preset.scale
        cfg.project.type = new_preset.project_type
        cfg.governance_mode = new_preset.governance_mode
        cfg.docs_core = new_preset.docs_core
        cfg.clarification_limit = new_preset.clarification_limit
        cfg.analyze.enforce_commit_trace = new_preset.enforce_commit_trace
        save_config(root, cfg)

        # Generate missing docs
        language = normalize_language(lang or cfg.language)
        created, skipped = ensure_docs(
            root=root,
            cfg=cfg,
            language=language,
            with_optional_docs=cfg.docs_optional_enabled,
            include_meta_docs=True,
        )
        if not json_output:
            typer.echo(f"Created: {', '.join(created) if created else 'None'}")
            typer.echo(f"Skipped: {', '.join(skipped) if skipped else 'None'}")
            typer.echo("Profile upgrade complete.")


def _emit_json(data: object) -> None:
    """Emit JSON to stdout — shared helper to reduce duplication."""
    typer.echo(json.dumps(data, ensure_ascii=False, indent=2))
