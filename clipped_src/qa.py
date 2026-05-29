from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from .templates import REGISTRY, default_platform_for_template
from .video import process_video

test_app = typer.Typer(help="Quality assurance and smoke test commands.")
console = Console()


def _default_platform_for_template(template: str) -> str:
    return default_platform_for_template(template)


@test_app.command("templates")
def test_templates(
    sample: str = typer.Argument(..., help="Sample audio file path."),
    templates: Optional[str] = typer.Option(None, "--templates", help="Comma-separated list of templates to test."),
    platform: Optional[str] = typer.Option(None, "--platform", help="Platform to test against."),
    dry_run: bool = typer.Option(True, "--dry-run", help="Only print FFmpeg commands."),
    execute: bool = typer.Option(False, "--execute", help="Run the actual render instead of dry-run."),
) -> None:
    """Run a template smoke test against a sample audio file."""
    audio_path = Path(sample).expanduser()
    if not audio_path.exists():
        console.print(f"[red]Sample audio not found:[/red] {audio_path}")
        raise typer.Exit(1)

    selected = []
    if templates:
        selected = [t.strip() for t in templates.split(",") if t.strip()]
    else:
        selected = list(REGISTRY.keys())

    for template in selected:
        if template not in REGISTRY:
            console.print(f"[yellow]Skipping unknown template:[/yellow] {template}")
            continue
        platform_name = platform or _default_platform_for_template(template)
        console.print(f"\n[bold]Testing {template} on {platform_name}[/bold]")
        try:
            process_video(
                str(audio_path),
                template_name=template,
                platform_name=platform_name,
                dry_run=dry_run and not execute,
            )
        except Exception as exc:
            console.print(f"[red]Error for {template}:[/red] {exc}")
            raise typer.Exit(1)

    console.print("\n[green]Template QA completed.[/green]")
