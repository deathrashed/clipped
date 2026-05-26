from __future__ import annotations

import shutil
from pathlib import Path

from rich.console import Console

from .config import get_config, load_config, validate_output_dirs
from .platforms import list_platforms
from .templates import REGISTRY

console = Console()


def _check_tool(name: str) -> bool:
    path = shutil.which(name)
    console.print(f"- {name}: [green]found[/green]" if path else f"- {name}: [red]missing[/red]")
    return bool(path)


def _check_python_package(name: str) -> bool:
    try:
        __import__(name)
        console.print(f"- Python package {name}: [green]import OK[/green]")
        return True
    except ImportError:
        console.print(f"- Python package {name}: [red]missing[/red]")
        return False


def _check_templates() -> bool:
    success = True
    console.print("\nTemplate registry:")
    for name, cls in REGISTRY.items():
        try:
            instance = cls()
            size = instance.get_output_size()
            console.print(f"- {name}: [green]OK[/green] ({size[0]}x{size[1]})")
        except Exception as exc:
            console.print(f"- {name}: [red]ERROR[/red] {exc}")
            success = False
    return success


def _check_platforms() -> bool:
    success = True
    console.print("\nPlatform profiles:")
    for profile in list_platforms():
        try:
            assert profile.name
            console.print(f"- {profile.name}: [green]OK[/green] ({profile.label})")
        except AssertionError:
            console.print(f"- {profile.name}: [red]invalid[/red]")
            success = False
    return success


def run_diagnostics() -> None:
    console.print("[bold cyan]Clipped diagnostics[/bold cyan]\n")

    config = load_config()
    general = config.get("general", {})

    console.print("[bold]Config file[/bold]")
    console.print(f"- Path: {Path.home() / '.config' / 'clipped' / 'config.toml'}")
    console.print(f"- Presets: {', '.join(sorted(config.get('preset', {}).keys())) or 'none'}")
    console.print("\n[bold]Required tools[/bold]")

    tools = ["python3", "ffmpeg", "ffprobe", "yt-dlp", "osascript"]
    tool_results = [_check_tool(tool) for tool in tools]

    console.print("\n[bold]Python dependencies[/bold]")
    pkg_results = [_check_python_package(name) for name in ["mutagen"]]

    console.print("\n[bold]Output directories[/bold]")
    validate_output_dirs(get_config())

    template_ok = _check_templates()
    platforms_ok = _check_platforms()

    console.print("\n[bold]Summary[/bold]")
    overall = all(tool_results + pkg_results + [template_ok, platforms_ok])
    console.print(
        "[green]All checks passed[/green]" if overall else "[red]Some checks failed[/red]"
    )

    if not overall:
        raise SystemExit(1)
