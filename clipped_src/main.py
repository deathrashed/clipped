"""
Clipped — main TUI / CLI entrypoint.

Commands:
  clipped               → interactive TUI (default)
  clipped audio         → clip audio
  clipped video         → generate video
  clipped browse        → browse / search clip library
  clipped templates     → list available video templates
  clipped platforms     → list available platform profiles
  clipped --preset NAME → load a named preset
  clipped --version     → show version
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich import box

from . import __version__
from .audio import process_clip, mark_start, mark_end
from .config import HISTORY_FILE, get_config, get_preset
from .library import Library
from .platforms import list_platforms, get_profile, suggested_template, PLATFORMS
from .templates import list_templates, REGISTRY
from .utils import parse_time
from .video import process_video

app     = typer.Typer(help="Clipped — high-leverage audio & video automation.", add_completion=False)
console = Console()


# ── Version ───────────────────────────────────────────────────────────────────

def _version_callback(value: bool):
    if value:
        console.print(f"[bold cyan]Clipped[/bold cyan] v{__version__}")
        raise typer.Exit()


# ── Main callback ─────────────────────────────────────────────────────────────

@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    preset: Optional[str] = typer.Option(
        None, "--preset", "-p",
        help="Load a named preset from config.toml (e.g. --preset instagram).",
    ),
    version: Optional[bool] = typer.Option(
        None, "--version", "-V",
        callback=_version_callback, is_eager=True,
        help="Show version and exit.",
    ),
):
    """Entrypoint: launches TUI if no sub-command is given."""
    if ctx.invoked_subcommand is None:
        preset_config = None
        if preset:
            try:
                preset_config = get_preset(preset)
                console.print(f"[dim]Loaded preset:[/dim] [bold]{preset}[/bold]")
            except ValueError as e:
                console.print(f"[red]{e}[/red]")
                raise typer.Exit(1)
        _run_interactive_menu(preset_config=preset_config)


# ── Interactive TUI ───────────────────────────────────────────────────────────

def _run_interactive_menu(preset_config: dict | None = None) -> None:
    import questionary

    cfg = preset_config or get_config()

    console.print(
        f"\n[bold cyan]📀 CLIPPED[/bold cyan] [dim]v{__version__}[/dim]\n"
    )

    choice = questionary.select(
        "What would you like to do?",
        choices=[
            "✂️  Clip Audio (File or URL)",
            "🎬 Generate Video",
            "📚 Browse Clip Library",
            "ℹ️  List Templates",
            "🚪 Exit",
        ],
    ).ask()

    if choice and choice.startswith("✂️"):
        _interactive_audio(cfg)
    elif choice and choice.startswith("🎬"):
        _interactive_video(cfg)
    elif choice and choice.startswith("📚"):
        _browse_library()
    elif choice and choice.startswith("ℹ️"):
        _print_templates()
    else:
        sys.exit(0)


def _interactive_audio(cfg: dict) -> None:
    import questionary

    # Source
    use_history = False
    if HISTORY_FILE.exists():
        last = HISTORY_FILE.read_text().strip()
        if last:
            use_history = questionary.confirm(
                f"Use last source? [{Path(last).name if not last.startswith('http') else last[:60]}]"
            ).ask()

    if use_history:
        src = last
    else:
        method = questionary.select(
            "Source:",
            choices=["📁 Pick file", "🔗 Enter YouTube URL"],
        ).ask()
        if method and method.startswith("📁"):
            script = 'tell app "System Events" to POSIX path of (choose file with prompt "Select audio:")'
            res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
            src = res.stdout.strip()
        else:
            src = questionary.text("YouTube URL:").ask() or ""

    if not src:
        console.print("[red]No source provided.[/red]")
        return

    start = questionary.text("Start time (M:SS or seconds):", default="0").ask() or "0"
    end   = questionary.text("End time   (M:SS or seconds):").ask() or ""

    if not end:
        console.print("[red]End time is required.[/red]")
        return

    # Metadata summary
    from .utils import resolve_assets
    if not src.startswith("http"):
        assets = resolve_assets(src)
        console.print(f"\n[bold cyan]Metadata:[/bold cyan] {assets.summary()}\n")

    # Fade prompts
    fade_in = questionary.text(
        "Fade in duration (seconds):",
        default=str(cfg.get("fade_duration", 0.5))
    ).ask()
    fade_out = questionary.text(
        "Fade out duration (seconds):",
        default=str(cfg.get("fade_duration", 0.5))
    ).ask()

    is_url = src.startswith("http")
    process_clip(
        src,
        parse_time(start),
        parse_time(end),
        is_url=is_url,
        fade_in=float(fade_in) if fade_in else None,
        fade_out=float(fade_out) if fade_out else None,
    )


def _interactive_video(cfg: dict) -> None:
    import questionary

    # Pick audio source
    script = 'tell app "System Events" to POSIX path of (choose file with prompt "Select audio file:" of type {"public.audio"})'
    res    = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    src    = res.stdout.strip()
    if not src:
        console.print("[red]No file selected.[/red]")
        return

    # Metadata summary
    from .utils import resolve_assets
    assets = resolve_assets(src)
    console.print(f"\n[bold cyan]Metadata:[/bold cyan] {assets.summary()}\n")

    # Template picker (with descriptions)
    templates = list_templates()
    template_choices = [
        f"{t.info.label}  [dim]— {t.info.description}[/dim]"
        for t in templates
    ]
    t_choice = questionary.select("Video template:", choices=template_choices).ask()
    if not t_choice:
        return
    template_name = templates[template_choices.index(t_choice)].info.name

    # Platform picker
    platform_choices = [
        f"{p.label}" + (f"  [dim]{p.notes}[/dim]" if p.notes else "")
        for p in list_platforms()
    ]
    p_names = [p.name for p in list_platforms()]
    p_choice = questionary.select("Platform:", choices=platform_choices).ask()
    if not p_choice:
        return
    platform_name = p_names[platform_choices.index(p_choice)]

    # Custom fade sequence
    sequence = None
    if template_name == "fade":
        from .utils import resolve_assets
        assets = resolve_assets(src)
        if assets.all_images:
            if questionary.confirm("Build custom image sequence?").ask():
                sequence = []
                remaining = assets.all_images.copy()
                while remaining:
                    img = questionary.select(
                        "Add image (or Done):",
                        choices=[str(p.name) for p in remaining] + ["Done"],
                    ).ask()
                    if img == "Done":
                        break
                    path = next(p for p in remaining if p.name == img)
                    dur  = questionary.text(f"Duration for {img} (seconds):", default="5.0").ask()
                    sequence.append((path, float(dur)))
                    remaining.remove(path)
                    if not questionary.confirm("Add another?").ask():
                        break

    # Custom waveform options (only shown when waveformbar is chosen)
    waveform_cfg = {}
    if template_name == "waveformbar":
        wf_mode = questionary.select(
            "Waveform style:",
            choices=[
                "line   — smooth continuous line (recommended)",
                "cline  — centered line (mirror up/down)",
                "p2p    — peak-to-peak bars",
                "point  — point scatter",
            ],
        ).ask()
        if wf_mode:
            waveform_cfg["waveform_mode"] = wf_mode.split()[0]
        color_custom = questionary.select(
            "Waveform colour:",
            choices=[
                "Cyan   (0x00E5FF) — default",
                "White  (0xFFFFFF)",
                "Gold   (0xFFD700)",
                "Red    (0xFF2D55)",
                "Green  (0x00FF88)",
                "Custom (enter hex)",
            ],
        ).ask()
        if color_custom:
            if color_custom.startswith("Custom"):
                hex_val = questionary.text("Hex colour (e.g. 0xFF0000):").ask() or "0x00E5FF"
                waveform_cfg["waveform_color"] = hex_val
            else:
                # Extract hex from choice string  e.g. "Cyan   (0x00E5FF) — default"
                import re
                m = re.search(r"(0x[0-9A-Fa-f]{6})", color_custom)
                if m:
                    waveform_cfg["waveform_color"] = m.group(1)

    start = questionary.text("Start time (optional):", default="0").ask() or "0"
    end   = questionary.text("End time (optional, leave blank for full file):").ask() or ""

    process_video(
        src,
        template_name=template_name,
        platform_name=platform_name,
        start=parse_time(start),
        end=parse_time(end) if end else None,
        sequence=sequence,
        extra_config=waveform_cfg or None,
    )


# ── Audio command ─────────────────────────────────────────────────────────────

@app.command("audio")
def audio_cmd(
    src: str   = typer.Argument(None, help="Audio file path or YouTube URL"),
    start: str = typer.Argument(None, help="Start time (M:SS or seconds)"),
    end: str   = typer.Argument(None, help="End time   (M:SS or seconds)"),
    mark_s:  bool = typer.Option(False, "--mark-start",  help="Mark start in Swinsian"),
    mark_e:  bool = typer.Option(False, "--mark-end",    help="Mark end in Swinsian and clip"),
    history: bool = typer.Option(False, "--history",     help="Use last source"),
    dry_run: bool = typer.Option(False, "--dry-run",     help="Print command, don't run"),
):
    """Clip an audio file or YouTube URL."""
    if mark_s:
        mark_start(); return
    if mark_e:
        mark_end();   return

    if history:
        if HISTORY_FILE.exists():
            src = HISTORY_FILE.read_text().strip()
            console.print(f"[dim]Using history:[/dim] {src}")
        else:
            console.print("[red]No history found.[/red]")
            raise typer.Exit(1)

    if not src:
        script = 'tell app "System Events" to POSIX path of (choose file with prompt "Select audio:")'
        res    = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
        src    = res.stdout.strip()
        if not src:
            console.print("[red]No source provided.[/red]")
            raise typer.Exit(1)

    import questionary
    if not start:
        start = questionary.text("Start time (M:SS or seconds):").ask() or ""
    if not end:
        end = questionary.text("End time   (M:SS or seconds):").ask() or ""

    if not start or not end:
        console.print("[red]Start and end times are required.[/red]")
        raise typer.Exit(1)

    is_url = src.startswith("http")
    process_clip(src, parse_time(start), parse_time(end), is_url=is_url, dry_run=dry_run)


# ── Video command ─────────────────────────────────────────────────────────────

@app.command("video")
def video_cmd(
    src:           str           = typer.Argument(...,         help="Path to audio file"),
    template:      str           = typer.Option("spinner",    help=f"Template: {', '.join(REGISTRY.keys())}"),
    platform:      str           = typer.Option("default",    help=f"Platform: {', '.join(PLATFORMS.keys())}"),
    start:         Optional[str] = typer.Option(None,          help="Start time"),
    end:           Optional[str] = typer.Option(None,          help="End time"),
    preset:        Optional[str] = typer.Option(None,          help="Named preset from config.toml"),
    waveform_mode: Optional[str] = typer.Option(None, "--waveform-mode",
                                                help="Waveform style: line|cline|p2p|point"),
    waveform_color:Optional[str] = typer.Option(None, "--waveform-color",
                                                help="Waveform hex colour, e.g. 0xFF0000"),
    fade_in:       Optional[float] = typer.Option(None, "--fade-in",      help="Audio fade-in duration (seconds)"),
    fade_out:      Optional[float] = typer.Option(None, "--fade-out",     help="Audio fade-out duration (seconds)"),
    dry_run:       bool          = typer.Option(False, "--dry-run", help="Print FFmpeg command, don't run"),
):
    """Generate a video from an audio file."""
    if preset:
        try:
            cfg = get_preset(preset)
            template = cfg.get("default_template", template)
            platform = cfg.get("default_platform", platform)
        except ValueError as e:
            console.print(f"[red]{e}[/red]"); raise typer.Exit(1)

    extra: dict = {}
    if waveform_mode:  extra["waveform_mode"]  = waveform_mode
    if waveform_color: extra["waveform_color"] = waveform_color

    process_video(
        src,
        template_name=template,
        platform_name=platform,
        start=parse_time(start) if start else 0,
        end=parse_time(end)   if end   else None,
        dry_run=dry_run,
        extra_config=extra or None,
        fade_in=fade_in,
        fade_out=fade_out,
    )


# ── Browse command ────────────────────────────────────────────────────────────

@app.command("browse")
def browse_cmd(
    query: Optional[str] = typer.Argument(None, help="Search query (artist, title, album)"),
    limit: int           = typer.Option(20, "--limit", "-n", help="Max results to show"),
):
    """Browse or search the clip library."""
    lib = Library()
    entries = lib.search(query) if query else lib.all()

    if not entries:
        msg = f"No clips found for '{query}'." if query else "No clips yet. Make some!"
        console.print(f"[dim]{msg}[/dim]")
        return

    entries = entries[:limit]

    table = Table(
        title=f"📚 Clip Library{f' — "{query}"' if query else ''} "
              f"({len(entries)} result{'s' if len(entries) != 1 else ''})",
        box=box.ROUNDED,
        highlight=True,
    )
    table.add_column("#",       style="dim",   width=4,  no_wrap=True)
    table.add_column("Artist",  style="cyan",  width=20, no_wrap=True)
    table.add_column("Title",   style="white", width=28, no_wrap=True)
    table.add_column("Dur",     style="green", width=7,  no_wrap=True)
    table.add_column("Tmpl",    style="magenta", width=10, no_wrap=True)
    table.add_column("Platform",style="yellow", width=12, no_wrap=True)
    table.add_column("Date",    style="dim",   width=12, no_wrap=True)

    for i, e in enumerate(entries, 1):
        date = e.created_at[:10] if e.created_at else ""
        table.add_row(
            str(i),
            e.artist[:18] or "—",
            e.title[:26]  or Path(e.source).stem[:26],
            f"{e.duration:.0f}s",
            e.template,
            e.platform,
            date,
        )

    console.print(table)

    # Interactive re-render prompt
    import questionary
    if questionary.confirm("Re-render a clip as video?", default=False).ask():
        idx = questionary.text(f"Entry # (1–{len(entries)}):").ask()
        try:
            entry = entries[int(idx) - 1]
        except (ValueError, IndexError):
            console.print("[red]Invalid selection.[/red]"); return

        src_path = entry.output_audio or entry.source
        t_choices = [f"{t.info.label}" for t in list_templates()]
        t_names   = [t.info.name for t in list_templates()]
        t_choice  = questionary.select("Template:", choices=t_choices).ask()
        p_choices = [p.label for p in list_platforms()]
        p_names   = [p.name  for p in list_platforms()]
        p_choice  = questionary.select("Platform:", choices=p_choices).ask()

        process_video(
            src_path,
            template_name=t_names[t_choices.index(t_choice)],
            platform_name=p_names[p_choices.index(p_choice)],
        )


# ── Templates info command ────────────────────────────────────────────────────

@app.command("templates")
def templates_cmd():
    """List all available video templates."""
    _print_templates()


def _print_templates():
    table = Table(title="🎬 Available Templates", box=box.ROUNDED, highlight=True)
    table.add_column("Name",        style="cyan",    width=12)
    table.add_column("Label",       style="white",   width=30)
    table.add_column("Size",        style="green",   width=12)
    table.add_column("Ideal For",   style="yellow")

    for t in list_templates():
        w, h = t.info.aspect
        table.add_row(
            t.info.name,
            t.info.label,
            f"{w}×{h}",
            ", ".join(t.info.ideal_for),
        )
    console.print(table)


# ── Platforms info command ────────────────────────────────────────────────────

@app.command("platforms")
def platforms_cmd():
    """List all available platform export profiles."""
    table = Table(title="📤 Platform Profiles", box=box.ROUNDED, highlight=True)
    table.add_column("Name",        style="cyan",    width=16)
    table.add_column("Label",       style="white",   width=26)
    table.add_column("Size",        style="green",   width=12)
    table.add_column("Max Duration",style="magenta", width=14)
    table.add_column("Format",      style="yellow",  width=8)
    table.add_column("Ideal Template", style="dim")

    for p in list_platforms():
        size = f"{p.width}×{p.height}" if p.width else "—"
        dur  = f"{p.max_duration:.0f}s" if p.max_duration else "—"
        table.add_row(
            p.name, p.label, size, dur, p.output_format,
            suggested_template(p.name),
        )
    console.print(table)


if __name__ == "__main__":
    app()
