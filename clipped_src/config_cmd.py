from __future__ import annotations

import os
import subprocess

import typer
from rich.console import Console

from .config import CONFIG_FILE, load_config, _DEFAULT_TOML

config_app = typer.Typer(help="Manage Clipped configuration.")
console = Console()


@config_app.command("show")
def show(full: bool = typer.Option(False, "--full", help="Show raw config file contents.")) -> None:
    """Show the current Clipped configuration."""
    if full:
        if CONFIG_FILE.exists():
            console.print(CONFIG_FILE.read_text())
        else:
            console.print("[yellow]No config file found.[/yellow]")
        return

    config = load_config()
    console.print("[bold]General settings[/bold]")
    for key, value in config.get("general", {}).items():
        console.print(f"- {key}: {value}")

    presets = config.get("preset", {})
    console.print("\n[bold]Presets[/bold]")
    if presets:
        for name, data in presets.items():
            console.print(f"- {name}: {data}")
    else:
        console.print("- none")


@config_app.command("edit")
def edit() -> None:
    """Open the user config file in the default editor."""
    editor = os.environ.get("EDITOR", "vi")
    config_dir = CONFIG_FILE.parent
    config_dir.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(_DEFAULT_TOML)
    subprocess.run([editor, str(CONFIG_FILE)])


@config_app.command("init")
def init() -> None:
    """Initialize a default Clipped config file if one does not exist."""
    config_dir = CONFIG_FILE.parent
    config_dir.mkdir(parents=True, exist_ok=True)
    if CONFIG_FILE.exists():
        console.print(f"[yellow]Config already exists at {CONFIG_FILE}[/yellow]")
        raise typer.Exit(1)
    CONFIG_FILE.write_text(_DEFAULT_TOML)
    console.print(f"[green]Created config at {CONFIG_FILE}[/green]")


@config_app.command("reset")
def reset(force: bool = typer.Option(False, "--force", help="Reset without prompt.")) -> None:
    """Reset the Clipped config file to defaults."""
    if CONFIG_FILE.exists() and not force:
        if not typer.confirm(f"Overwrite {CONFIG_FILE} with default settings?"):
            raise typer.Exit()
    CONFIG_FILE.write_text(_DEFAULT_TOML)
    console.print(f"[green]Reset config at {CONFIG_FILE}[/green]")
