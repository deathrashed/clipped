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
from pathlib import Path
from typing import Optional

import typer
from rich.panel import Panel
from rich.console import Console
from rich.table import Table
from rich import box

from . import __version__
from .audio import process_clip, mark_start, mark_end
from .config import HISTORY_FILE, get_config, get_preset
from .config_cmd import config_app
from .doctor import run_diagnostics
from .platforms import list_platforms, suggested_template, PLATFORMS
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
        console.print()
        console.print(Panel(
            "[bold white]CLIPPED[/bold white] "
            f"[dim]v{__version__}[/dim]\n"
            "[cyan]Audio clips, album-art reels, and Swinsian automation[/cyan]",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(1, 3),
        ))

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

def _format_duration(seconds: float | None) -> str:
    if not seconds:
        return "unknown"
    mins, secs = divmod(int(seconds), 60)
    hours, mins = divmod(mins, 60)
    if hours:
        return f"{hours}:{mins:02d}:{secs:02d}"
    return f"{mins}:{secs:02d}"


def _short_path(path: str, max_len: int = 58) -> str:
    if not path:
        return ""
    display = path.replace(str(Path.home()), "~")
    if len(display) <= max_len:
        return display
    return f"...{display[-(max_len - 3):]}"


def _last_source() -> str:
    if not HISTORY_FILE.exists():
        return ""
    return HISTORY_FILE.read_text().strip()


def _source_title(src: str) -> str:
    if not src:
        return "No source"
    if src.startswith("http"):
        return _short_path(src, max_len=70)
    return Path(src).name


def _is_url(src: str) -> bool:
    return src.startswith(("http://", "https://"))


def _validate_source(src: str, allow_url: bool = False) -> bool:
    if _is_url(src):
        if allow_url:
            return True
        UI.err("This workflow expects a local audio file, not a URL.")
        return False
    path = Path(src).expanduser()
    if path.exists() and path.is_file():
        return True
    UI.err(f"Audio file not found: {src}")
    return False


def _parse_optional_float(value: str | None, label: str) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        UI.err(f"{label} must be a number of seconds.")
        return None


def _print_tui_context(cfg: dict, last_action: dict | None) -> None:
    table = Table.grid(expand=True)
    table.add_column(ratio=1)
    table.add_column(ratio=1)

    last = _last_source()
    defaults = (
        f"[bold]Default render[/bold]\n"
        f"Template: [cyan]{cfg.get('default_template', 'spinner')}[/cyan]\n"
        f"Platform: [magenta]{cfg.get('default_platform', 'default')}[/magenta]\n"
        f"Fade: [green]{cfg.get('fade_duration', 0.5)}s[/green]"
    )
    recent = (
        "[bold]Session[/bold]\n"
        f"Last source: [white]{_source_title(last) if last else 'none'}[/white]\n"
        f"Previous action: [white]{last_action['label'] if last_action else 'none'}[/white]\n"
        f"Video dir: [dim]{_short_path(str(Path(cfg.get('video_dir', '')).expanduser()))}[/dim]"
    )

    table.add_row(
        Panel(defaults, title="Preset", border_style="cyan", box=box.ROUNDED),
        Panel(recent, title="Context", border_style="magenta", box=box.ROUNDED),
    )
    console.print(table)
    console.print()


def _choose_source(prompt: str, allow_url: bool = False, allow_history: bool = True) -> str:
    import questionary

    choices = []
    last = _last_source()
    if allow_history and last and (allow_url or not last.startswith("http")):
        choices.append(questionary.Choice(
            title=f"Last source  —  {_source_title(last)}",
            value=("history", last),
        ))
        choices.append(questionary.Separator())

    choices.extend([
        questionary.Choice(title="Current track in Swinsian", value=("swinsian", None)),
        questionary.Choice(title="Choose audio file", value=("file", None)),
        questionary.Choice(title="Enter file path manually", value=("manual", None)),
    ])
    if allow_url:
        choices.append(questionary.Choice(title="YouTube URL", value=("url", None)))

    selected = questionary.select(prompt, choices=choices).ask()
    if not selected:
        return ""

    method, value = selected
    if method == "history":
        src = value or ""
        return src if _validate_source(src, allow_url=allow_url) else ""
    if method == "file":
        script = (
            'tell application (path to frontmost application as text) '
            'to POSIX path of (choose file with prompt "Select audio file:" of type {"public.audio"})'
        )
        res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
        src = res.stdout.strip()
        return src if src and _validate_source(src, allow_url=allow_url) else ""
    if method == "swinsian":
        from .audio import _swinsian_current_track
        src = _swinsian_current_track()
        if not src:
            UI.err("Swinsian is not playing a track.")
            return ""
        return src if _validate_source(src, allow_url=allow_url) else ""
    if method == "manual":
        src = questionary.path("Audio file path:").ask() or ""
        src = str(Path(src).expanduser()) if src.startswith("~") else src
        return src if src and _validate_source(src, allow_url=allow_url) else ""
    if method == "url":
        src = questionary.text("YouTube URL:").ask() or ""
        return src if src and _validate_source(src, allow_url=allow_url) else ""
    return ""


def _print_source_summary(src: str):
    if src.startswith("http"):
        console.print(Panel(
            f"[bold]YouTube URL[/bold]\n[white]{src}[/white]",
            title="Source",
            border_style="cyan",
            box=box.ROUNDED,
        ))
        return None

    from .utils import resolve_assets
    assets = resolve_assets(src)
    table = Table.grid(padding=(0, 2))
    table.add_column(style="cyan", no_wrap=True)
    table.add_column(style="white")
    table.add_row("Track", assets.track_title or Path(src).stem)
    table.add_row("Artist", assets.artist_name or "unknown")
    table.add_row("Album", assets.album_name or "unknown")
    table.add_row("Duration", _format_duration(assets.duration))
    table.add_row("Cover", "yes" if assets.cover else "missing")
    table.add_row("Logo", "yes" if assets.logo else "missing")
    console.print(Panel(table, title="Source", border_style="cyan", box=box.ROUNDED))
    return assets


def _confirm_plan(title: str, rows: list[tuple[str, str]]) -> bool:
    import questionary

    table = Table.grid(padding=(0, 2))
    table.add_column(style="cyan", no_wrap=True)
    table.add_column(style="white")
    for key, value in rows:
        table.add_row(key, value)
    console.print(Panel(table, title=title, border_style="green", box=box.ROUNDED))
    return bool(questionary.confirm("Run this workflow?", default=True).ask())


def _run_interactive_menu(preset_config: dict | None = None) -> None:
    import questionary

    cfg = preset_config or get_config()
    last_action: dict | None = None

    while True:
        UI.header()
        _print_tui_context(cfg, last_action)

        choices = []
        if last_action:
            choices.append(questionary.Choice(
                title=f"Rerun previous workflow  —  {last_action['label']}",
                value="rerun",
            ))
            choices.append(questionary.Separator())

        choices += [
            questionary.Choice(
                title="Generate video reel  —  choose source, template, platform, time range",
                value="video",
            ),
            questionary.Choice(
                title="Clip audio  —  file, Swinsian, last source, or YouTube URL",
                value="audio",
            ),
            questionary.Separator(),
            questionary.Choice(title="Browse templates", value="templates"),
            questionary.Choice(title="Browse platform profiles", value="platforms"),
            questionary.Choice(title="Exit", value="exit"),
        ]

        choice = questionary.select(
            "Choose a workflow:",
            choices=choices,
        ).ask()

        if not choice or choice == "exit":
            break

        if choice == "rerun" and last_action:
            last_action["func"](*last_action["args"], **last_action["kwargs"])
            continue

        if choice == "audio":
            action = _interactive_audio(cfg)
            if action:
                last_action = action
        elif choice == "video":
            action = _interactive_video(cfg)
            if action:
                last_action = action
        elif choice == "templates":
            _print_templates()
        elif choice == "platforms":
            platforms_cmd()


def _interactive_audio(cfg: dict) -> None:
    import questionary

    src = _choose_source("Audio source:", allow_url=True)

    if not src:
        UI.err("No source provided.")
        return

    _print_source_summary(src)

    start = questionary.text("Start time:", default="0").ask() or "0"
    end   = questionary.text("End time:", instruction="M:SS, H:MM:SS, or seconds").ask() or ""

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

    is_url = _is_url(src)
    fade_in_value = _parse_optional_float(fade_in, "Fade in duration")
    fade_out_value = _parse_optional_float(fade_out, "Fade out duration")
    if (fade_in and fade_in_value is None) or (fade_out and fade_out_value is None):
        return

    params = {
        "src": src,
        "start": parse_time(start),
        "end": parse_time(end),
        "is_url": is_url,
        "fade_in": fade_in_value,
        "fade_out": fade_out_value,
    }

    if not _confirm_plan("Audio Clip", [
        ("Source", _source_title(src)),
        ("Range", f"{start} -> {end}"),
        ("Fade", f"in {fade_in or 'auto'}s / out {fade_out or 'auto'}s"),
        ("Output", _short_path(str(Path(cfg.get("audio_dir", "")).expanduser()))),
    ]):
        return

    process_clip(**params)

    return {
        "func": process_clip,
        "args": [],
        "kwargs": params,
        "label": f"Audio Clip ({Path(src).name if not is_url else src[:30]})",
    }


def _interactive_video(cfg: dict) -> None:
    import questionary

    src = _choose_source("Video source:", allow_url=False)

    if not src:
        UI.err("No file selected.")
        return

    assets = _print_source_summary(src)

    # Template picker
    template_name = _pick_template(default=cfg.get("default_template"))
    if not template_name:
        return

    # Platform picker
    platform_name = _pick_platform(default=cfg.get("default_platform"))
    if not platform_name:
        return

    # Custom fade sequence
    sequence = _build_fade_sequence(assets) if template_name == "fade" else None

    # Custom waveform options
    waveform_cfg = _build_waveform_config() if template_name == "waveformbar" else {}

    start = questionary.text("Start time:", default="0", instruction="optional").ask() or "0"
    end   = questionary.text("End time:", instruction="blank means full file").ask() or ""
    fade_in = questionary.text(
        "Audio fade in:",
        default=str(cfg.get("fade_duration", 0.5)),
        instruction="seconds; blank = config default",
    ).ask()
    fade_out = questionary.text(
        "Audio fade out:",
        default=str(cfg.get("fade_duration", 0.5)),
        instruction="seconds; blank = config default",
    ).ask()

    fade_in_value = _parse_optional_float(fade_in, "Audio fade in")
    fade_out_value = _parse_optional_float(fade_out, "Audio fade out")
    if (fade_in and fade_in_value is None) or (fade_out and fade_out_value is None):
        return

    params = {
        "src": src,
        "template_name": template_name,
        "platform_name": platform_name,
        "start": parse_time(start),
        "end": parse_time(end) if end else None,
        "sequence": sequence,
        "extra_config": waveform_cfg or None,
        "fade_in": fade_in_value,
        "fade_out": fade_out_value,
    }

    range_label = f"{start} -> {end}" if end else f"{start} -> full file"
    if not _confirm_plan("Video Render", [
        ("Source", _source_title(src)),
        ("Track", (assets.track_title if assets else Path(src).stem) or Path(src).stem),
        ("Template", template_name),
        ("Platform", platform_name),
        ("Range", range_label),
        ("Fade", f"in {fade_in or 'auto'}s / out {fade_out or 'auto'}s"),
        ("Output", _short_path(str(Path(cfg.get("video_dir", "")).expanduser()))),
    ]):
        return

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
    fade_in: Optional[float] = typer.Option(None, "--fade-in", help="Fade-in duration in seconds"),
    fade_out: Optional[float] = typer.Option(None, "--fade-out", help="Fade-out duration in seconds"),
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

    is_url = _is_url(src)
    if not _validate_source(src, allow_url=True):
        raise typer.Exit(1)

    out_path = Path(output) if output else None
    process_clip(
        src, parse_time(start), parse_time(end),
        is_url=is_url, dry_run=dry_run,
        fade_in=fade_in, fade_out=fade_out,
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
    platform:      Optional[str] = typer.Option(None,          help=f"Platform: {', '.join(PLATFORMS.keys())}"),
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
    base_cfg = get_config()

    # Logic to handle 'clipped video template src' vs 'clipped video src'
    final_src = src
    final_template = template or base_cfg.get("default_template", "spinner")
    final_platform = platform or base_cfg.get("default_platform", "default")

    # If target matches a template name, and src is provided, it's shorthand
    if target in REGISTRY and src:
        final_template = target
        final_src = src
    elif not src:
        # Standard usage: target is the src file
        final_src = target
    else:
        # ambiguous? assume target is src and ignore src unless it's a known conflict
        final_src = target

    if preset:
        try:
            cfg = get_preset(preset)
            final_template = cfg.get("default_template", final_template)
            final_platform = cfg.get("default_platform", final_platform)
        except ValueError as e:
            UI.err(str(e)); raise typer.Exit(1)

    extra: dict = {}
    if waveform_mode:  extra["waveform_mode"]  = waveform_mode
    if waveform_color: extra["waveform_color"] = waveform_color

    out_path = Path(output) if output else None
    if not final_src or not _validate_source(final_src, allow_url=False):
        raise typer.Exit(1)

    process_video(
        final_src,
        template_name=final_template,
        platform_name=final_platform,
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


def _pick_template(default: str | None = None) -> str | None:
    import questionary
    templates = list_templates()
    choices = []
    default_choice = None
    for t in templates:
        w, h = t.info.aspect
        title = (
            f"{t.info.label}  ({t.info.name})  —  "
            f"{w}x{h}; {', '.join(t.info.ideal_for) or 'general'}"
        )
        choice = questionary.Choice(title=title, value=t.info.name)
        choices.append(choice)
        if t.info.name == default:
            default_choice = choice
    return questionary.select(
        "Template:",
        choices=choices,
        default=default_choice,
        instruction="choose the visual style",
    ).ask()


def _pick_platform(default: str | None = None) -> str | None:
    import questionary
    platforms = list_platforms()
    choices = []
    default_choice = None
    for p in platforms:
        size = f"{p.width}x{p.height}" if p.width and p.height else p.output_format.upper()
        duration = f"{int(p.max_duration)}s max" if p.max_duration else "no cap"
        title = f"{p.label}  ({p.name})  —  {size}; {duration}"
        choice = questionary.Choice(title=title, value=p.name)
        choices.append(choice)
        if p.name == default:
            default_choice = choice
    return questionary.select(
        "Platform:",
        choices=choices,
        default=default_choice,
        instruction="sets size, duration cap, and output format",
    ).ask()


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
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Label", style="white")
    table.add_column("Profile", style="green")
    table.add_column("Best Template", style="dim")

    for p in list_platforms():
        size = f"{p.width}×{p.height}" if p.width else "—"
        dur  = f"{p.max_duration:.0f}s" if p.max_duration else "—"
        table.add_row(
            p.name,
            p.label,
            f"{size} / {dur} / {p.output_format}",
            suggested_template(p.name),
        )
    console.print(table)


def _print_platforms():
    platforms_cmd()


if __name__ == "__main__":
    app()
