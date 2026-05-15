"""
Clipped — main TUI / CLI entrypoint.

Commands:
  clipped audio         → clip audio
  clipped video         → generate video
  clipped templates     → list available video templates
  clipped platforms     → list available platform profiles
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
from .config_cmd import config_app
from .doctor import run_diagnostics
from .platforms import list_platforms, get_profile, suggested_template, PLATFORMS
from .qa import test_app
from .templates import list_templates, REGISTRY
from .batch import batch_app, watch_directory
from .docsgen import docs_app
from .utils import parse_time
from .video import process_video


# ── Retro/Cyberpunk UI ────────────────────────────────────────────────────────

class UI:
    """Standardized terminal UI messages and branding."""

    @staticmethod
    def header():
        """Retro TUI branding."""
        console.print(f"\n[bold cyan]┌──────────────────────────────┐[/bold cyan]")
        console.print(f"[bold cyan]│[/bold cyan] [bold white]📀 CLIPPED[/bold white] [dim]v{__version__}[/dim]             [bold cyan]│[/bold cyan]")
        console.print(f"[bold cyan]└──────────────────────────────┘[/bold cyan]\n")

    @staticmethod
    def sys(msg: str):
        console.print(f"[bold cyan][SYS][/bold cyan] {msg}")

    @staticmethod
    def info(msg: str):
        console.print(f"[bold green][INF][/bold green] {msg}")

    @staticmethod
    def warn(msg: str):
        console.print(f"[bold yellow][WRN][/bold yellow] {msg}")

    @staticmethod
    def err(msg: str):
        console.print(f"[bold red][ERR][/bold red] {msg}")

    @staticmethod
    def metadata(summary: str):
        console.print(f"\n[bold cyan][META][/bold cyan] [white]{summary}[/white]\n")


app     = typer.Typer(help="Clipped — high-leverage audio & video automation.", add_completion=False)
console = Console()

app.add_typer(config_app, name="config")
app.add_typer(test_app, name="test")
app.add_typer(batch_app, name="batch")
app.add_typer(docs_app, name="docs")


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


@app.command("doctor")
def doctor_cmd() -> None:
    """Run diagnostics on the Clipped environment and configuration."""
    run_diagnostics()


@app.command("watch")
def watch_cmd(
    input_dir: str = typer.Option(..., "--input-dir", help="Directory to watch for new audio files."),
    pattern: str = typer.Option("*.mp3", help="Glob pattern for new audio files."),
    recursive: bool = typer.Option(False, "--recursive", help="Search subdirectories."),
    mode: str = typer.Option("video", "--type", help="Processing mode: audio or video."),
    template: str = typer.Option("spinner", help="Template to use for video mode."),
    platform: str = typer.Option("default", help="Platform profile to use for video mode."),
    start: str = typer.Option("0", help="Start time for all clips."),
    end: str = typer.Option(None, help="End time for all clips."),
    interval: float = typer.Option(5.0, help="Polling interval in seconds."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print commands without running."),
) -> None:
    """Watch a directory and process new audio files as they appear."""
    watch_directory(
        Path(input_dir),
        pattern=pattern,
        recursive=recursive,
        mode=mode,
        template=template,
        platform=platform,
        start=start,
        end=end,
        interval=interval,
        dry_run=dry_run,
    )


# ── Interactive TUI ───────────────────────────────────────────────────────────

def _run_interactive_menu(preset_config: dict | None = None) -> None:
    import questionary

    cfg = preset_config or get_config()
    last_action: dict | None = None

    while True:
        UI.header()

        choices = []
        if last_action:
            choices.append(f"🔄 Rerun: {last_action['label']}")
            choices.append(questionary.Separator())

        choices += [
            "🎬 Generate Video",
            "✂️  Clip Audio (File or URL)",
            "ℹ️  List Templates",
            "📤 List Platforms",
            "🚪 Exit",
        ]

        choice = questionary.select(
            "What would you like to do?",
            choices=choices,
        ).ask()

        if not choice or "Exit" in choice:
            break

        if "Rerun" in choice and last_action:
            last_action["func"](*last_action["args"], **last_action["kwargs"])
            continue

        if choice.startswith("✂️"):
            action = _interactive_audio(cfg)
            if action:
                last_action = action
        elif choice.startswith("🎬"):
            action = _interactive_video(cfg)
            if action:
                last_action = action
        elif choice.startswith("ℹ️"):
            _print_templates()
        elif choice.startswith("📤"):
            platforms_cmd()


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
            choices=[
                "📁 Pick file (Finder)",
                "🎵 Current song in Swinsian",
                "⌨️  Enter path manually",
                "🔗 Enter YouTube URL"
            ],
        ).ask()

        if not method:
            return

        if method.startswith("📁"):
            script = 'tell application (path to frontmost application as text) to POSIX path of (choose file with prompt "Select audio:")'
            res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
            src = res.stdout.strip()
        elif method.startswith("🎵"):
            script = 'tell application "Swinsian" to POSIX path of (get location of current track)'
            res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
            src = res.stdout.strip()
        elif method.startswith("⌨️"):
            src = questionary.text("File path:").ask() or ""
            if src.startswith("~"):
                src = str(Path(src).expanduser())
        elif method.startswith("🔗"):
            src = questionary.text("YouTube URL:").ask() or ""
        else:
            return

    if not src:
        UI.err("No source provided.")
        return

    # Metadata summary
    from .utils import resolve_assets
    if not src.startswith("http"):
        assets = resolve_assets(src)
        UI.metadata(assets.summary())

    start = questionary.text("Start time (M:SS or seconds):", default="0").ask() or "0"
    end   = questionary.text("End time   (M:SS or seconds):").ask() or ""

    if not end:
        UI.err("End time is required.")
        return

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
    params = {
        "src": src,
        "start": parse_time(start),
        "end": parse_time(end),
        "is_url": is_url,
        "fade_in": float(fade_in) if fade_in else None,
        "fade_out": float(fade_out) if fade_out else None,
    }

    process_clip(**params)

    return {
        "func": process_clip,
        "args": [],
        "kwargs": params,
        "label": f"Audio Clip ({Path(src).name if not is_url else src[:30]})",
    }


def _interactive_video(cfg: dict) -> None:
    import questionary

    method = questionary.select(
        "Source:",
        choices=[
            "📁 Pick file (Finder)",
            "🎵 Current song in Swinsian",
            "⌨️  Enter path manually",
        ],
    ).ask()

    if not method:
        return

    if method.startswith("📁"):
        script = 'tell application (path to frontmost application as text) to POSIX path of (choose file with prompt "Select audio file:" of type {"public.audio"})'
        res    = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
        src    = res.stdout.strip()
    elif method.startswith("🎵"):
        from .audio import _swinsian_current_track
        src = _swinsian_current_track()
        if not src:
            UI.err("Swinsian is not playing a track.")
            return
    elif method.startswith("⌨️"):
        src = questionary.text("File path:").ask() or ""
        if src.startswith("~"):
            src = str(Path(src).expanduser())
    else:
        return

    if not src:
        UI.err("No file selected.")
        return

    # Metadata summary
    from .utils import resolve_assets
    assets = resolve_assets(src)
    UI.metadata(assets.summary())

    # Template picker
    template_name = _pick_template()
    if not template_name:
        return

    # Platform picker
    platform_name = _pick_platform()
    if not platform_name:
        return

    # Custom fade sequence
    sequence = _build_fade_sequence(assets) if template_name == "fade" else None

    # Custom waveform options
    waveform_cfg = _build_waveform_config() if template_name == "waveformbar" else {}

    start = questionary.text("Start time (optional):", default="0").ask() or "0"
    end   = questionary.text("End time (optional, leave blank for full file):").ask() or ""

    params = {
        "src": src,
        "template_name": template_name,
        "platform_name": platform_name,
        "start": parse_time(start),
        "end": parse_time(end) if end else None,
        "sequence": sequence,
        "extra_config": waveform_cfg or None,
    }

    process_video(**params)

    return {
        "func": process_video,
        "args": [],
        "kwargs": params,
        "label": f"Video: {template_name} ({platform_name})",
    }


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
    output:  Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
):
    """Clip an audio file or YouTube URL."""
    if mark_s:
        mark_start(); return
    if mark_e:
        mark_end();   return

    if history:
        if HISTORY_FILE.exists():
            src = HISTORY_FILE.read_text().strip()
            UI.info(f"Using history: [dim]{src}[/dim]")
        else:
            UI.err("No history found.")
            raise typer.Exit(1)

    if not src:
        script = 'tell application (path to frontmost application as text) to POSIX path of (choose file with prompt "Select audio:")'
        res    = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
        src    = res.stdout.strip()
        if not src:
            UI.err("No source provided.")
            raise typer.Exit(1)

    import questionary
    if not start:
        start = questionary.text("Start time (M:SS or seconds):").ask() or ""
    if not end:
        end = questionary.text("End time   (M:SS or seconds):").ask() or ""

    if not start or not end:
        UI.err("Start and end times are required.")
        raise typer.Exit(1)

    is_url = src.startswith("http")
    out_path = Path(output) if output else None
    process_clip(
        src, parse_time(start), parse_time(end),
        is_url=is_url, dry_run=dry_run,
        output_path=out_path,
    )


# ── Video command ─────────────────────────────────────────────────────────────

@app.command("video")
def video_cmd(
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
        help=f"Template: {', '.join(REGISTRY.keys())}"
    ),
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
    output:        Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
):
    """
    Generate a video from an audio file.

    Examples:
      clipped video myaudio.mp3
      clipped video vertical myaudio.mp3  (shorthand)
      clipped video --template reel myaudio.mp3
    """
    # Logic to handle 'clipped video template src' vs 'clipped video src'
    final_src = src
    final_template = template

    # If target matches a template name, and src is provided, it's shorthand
    if target in REGISTRY and src:
        final_template = target
        final_src = src
    elif not src:
        # Standard usage: target is the src file
        final_src = target
        if not final_template:
            final_template = "spinner" # Default
    else:
        # ambiguous? assume target is src and ignore src unless it's a known conflict
        final_src = target

    if preset:
        try:
            cfg = get_preset(preset)
            final_template = cfg.get("default_template", final_template)
            platform = cfg.get("default_platform", platform)
        except ValueError as e:
            UI.err(str(e)); raise typer.Exit(1)

    extra: dict = {}
    if waveform_mode:  extra["waveform_mode"]  = waveform_mode
    if waveform_color: extra["waveform_color"] = waveform_color

    out_path = Path(output) if output else None

    process_video(
        final_src,
        template_name=final_template,
        platform_name=platform,
        start=parse_time(start) if start else 0,
        end=parse_time(end)   if end   else None,
        dry_run=dry_run,
        extra_config=extra or None,
        fade_in=fade_in,
        fade_out=fade_out,
        output_path=out_path,
    )


# ── Browse command ────────────────────────────────────────────────────────────

@app.command("templates")
def templates_cmd():
    """List all available video templates."""
    _print_templates()


# ── UI Helpers ────────────────────────────────────────────────────────────────

def _build_fade_sequence(assets: "MediaAssets") -> list | None:
    """Interactive builder for image sequences."""
    import questionary
    if not assets.all_images:
        return None
    if not questionary.confirm("Build custom image sequence?").ask():
        return None

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
    return sequence


def _build_waveform_config() -> dict:
    """Interactive builder for waveformbar options."""
    import questionary
    import re
    cfg = {}
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
        cfg["waveform_mode"] = wf_mode.split()[0]

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
            cfg["waveform_color"] = hex_val
        else:
            m = re.search(r"(0x[0-9A-Fa-f]{6})", color_custom)
            if m:
                cfg["waveform_color"] = m.group(1)
    return cfg


def _pick_template() -> str | None:
    import questionary
    templates = list_templates()
    choices = [f"{t.info.label} [dim]({t.info.name})[/dim]" for t in templates]
    res = questionary.select("Select template:", choices=choices).ask()
    return templates[choices.index(res)].info.name if res else None


def _pick_platform() -> str | None:
    import questionary
    platforms = list_platforms()
    choices = [f"{p.label} [dim]({p.name})[/dim]" for p in platforms]
    res = questionary.select("Select platform:", choices=choices).ask()
    return platforms[choices.index(res)].name if res else None


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


def _print_platforms():
    platforms_cmd()


if __name__ == "__main__":
    app()
