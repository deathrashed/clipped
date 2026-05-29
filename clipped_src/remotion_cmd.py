from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from .remotion_engine import REMOTION_DIR

remotion_app = typer.Typer(help="Remotion Studio and renderer tooling.")
console = Console()


def _ensure_remotion_app() -> None:
    if not (REMOTION_DIR / "package.json").exists():
        console.print(f"[red]Remotion app missing:[/red] {REMOTION_DIR}")
        raise typer.Exit(1)


@remotion_app.command("preview")
def preview(
    target: str = typer.Argument(
        ...,
        help="Path to audio file OR template name (if followed by path)."
    ),
    src: Optional[str] = typer.Argument(
        None,
        help="Path to audio file (only if template name was provided first)."
    ),
    template: str = typer.Option(
        None,
        "--template", "-t",
        help="Template name"
    ),
    platform: Optional[str] = typer.Option(None, help="Platform name"),
    start: Optional[str] = typer.Option(None, help="Start time"),
    end: Optional[str] = typer.Option(None, help="End time"),
    duration: Optional[float] = typer.Option(None, "--duration", "-d", help="Preview duration"),
    cover: Optional[str] = typer.Option(None, help="Cover override"),
    logo: Optional[str] = typer.Option(None, help="Logo override"),
    background: Optional[str] = typer.Option(None, help="Background override"),
    media: Optional[str] = typer.Option(None, help="Media override"),
    lyrics: Optional[str] = typer.Option(None, help="Lyrics override"),
    port: int = typer.Option(3000, "--port", "-p", help="Remotion Studio port."),
) -> None:
    """Stage a preview and launch the Remotion Studio."""
    from .utils import parse_time
    from .templates import REGISTRY
    
    _ensure_remotion_app()

    final_src = src
    final_template = template

    if target in REGISTRY and src:
        final_template = target
        final_src = src
    elif not src:
        final_src = target
    else:
        final_src = target

    p = Path(final_src).expanduser()
    if not p.exists() or not p.is_file():
        console.print(f"[red]Error: file not found:[/red] {final_src}")
        raise typer.Exit(1)

    from .video import run_preview
    run_preview(
        src=final_src,
        template_name=final_template or "gallery_square",
        platform_name=platform or "default",
        start=parse_time(start) if start else 0.0,
        end=parse_time(end) if end else None,
        duration=duration,
        port=port,
        cover=cover,
        logo=logo,
        background=background,
        media=media,
        lyrics=lyrics,
    )


@remotion_app.command("studio")
def studio(
    port: int = typer.Option(3000, "--port", "-p", help="Remotion Studio port."),
) -> None:
    """Open Remotion Studio for Clipped templates."""
    _ensure_remotion_app()
    cmd = ["npx", "--no-install", "remotion", "studio", "src/index.ts", "--port", str(port)]
    raise typer.Exit(subprocess.call(cmd, cwd=REMOTION_DIR))


@remotion_app.command("install")
def install() -> None:
    """Install Remotion app dependencies."""
    _ensure_remotion_app()
    raise typer.Exit(subprocess.call(["npm", "install"], cwd=REMOTION_DIR))


@remotion_app.command("doctor")
def doctor() -> None:
    """Run Remotion typecheck and still-render smoke checks."""
    _ensure_remotion_app()
    checks = [
        ["npm", "run", "typecheck"],
        ["npm", "run", "compositions"],
        ["npm", "run", "still:smoke"],
    ]
    for cmd in checks:
        console.print(f"[cyan]$ {' '.join(cmd)}[/cyan]")
        code = subprocess.call(cmd, cwd=REMOTION_DIR)
        if code != 0:
            raise typer.Exit(code)
    console.print(f"[green]Remotion checks passed.[/green] Smoke still: {Path('../.cache/remotion-smoke/gallery_square.png')}")
