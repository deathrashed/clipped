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

import os
import subprocess
from math import gcd
from pathlib import Path
from typing import Any, Optional

import typer
from rich.panel import Panel
from rich.console import Console
from rich.table import Table
from rich import box

from . import __version__
from .audio import process_clip, mark_start, mark_end
from .config import HISTORY_FILE, get_config, get_preset, update_config_key, load_state, update_state
from .config_cmd import config_app
from .doctor import run_diagnostics
from .platforms import list_platforms, suggested_template, PLATFORMS
from .qa import test_app
from .remotion_cmd import remotion_app
from .templates import (
    REGISTRY,
    default_platform_for_template,
    list_templates,
    remotion_template_options,
    template_engine,
)
from .batch import batch_app, watch_directory
from .docsgen import docs_app
from .utils import parse_time
from .video import process_video


# ── Retro/Cyberpunk UI ────────────────────────────────────────────────────────

NAV_BACK = "__nav_back__"
NAV_MAIN = "__nav_main__"
OUTPUT_CANCELLED = object()

_NF_ICONS = {
    "app": "\uf1c7",
    "audio": "\uf001",
    "back": "\uf060",
    "check": "\uf00c",
    "clipboard": "\uf0ea",
    "default": "\uf0c7",
    "dropover": "\uf187",
    "edit": "\uf044",
    "exit": "\uf011",
    "finder": "\uf07c",
    "folder": "\uf07b",
    "home": "\uf015",
    "info": "\uf05a",
    "open": "\uf04b",
    "path": "\uf07b",
    "platform": "\uf135",
    "pointer": "\uf105",
    "prompt": "\uf128",
    "refresh": "\uf021",
    "render": "\uf1c8",
    "settings": "\uf013",
    "template": "\uf1c5",
    "video": "\uf03d",
    "warn": "\uf071",
}

_ASCII_ICONS = {
    "app": "[C]",
    "audio": "[A]",
    "back": "<",
    "check": "+",
    "clipboard": "[clip]",
    "default": "[save]",
    "dropover": "[drop]",
    "edit": "[edit]",
    "exit": "[exit]",
    "finder": "[find]",
    "folder": "[dir]",
    "home": "[home]",
    "info": "[i]",
    "open": "[open]",
    "path": "[path]",
    "platform": "[plat]",
    "pointer": ">",
    "prompt": "?",
    "refresh": "[again]",
    "render": "[render]",
    "settings": "[set]",
    "template": "[tpl]",
    "video": "[V]",
    "warn": "[warn]",
}

_PROMPT_STYLE = None


def _use_ascii_icons() -> bool:
    if os.environ.get("TERM", "").lower() == "dumb":
        return True
    return os.environ.get("CLIPPED_ASCII_ICONS", "").lower() in {"1", "true", "yes", "ascii"}


def icon(name: str) -> str:
    icons = _ASCII_ICONS if _use_ascii_icons() else _NF_ICONS
    return icons.get(name, "")


def _menu_label(icon_name: str, text: str) -> str:
    marker = icon(icon_name)
    return f"{marker}  {text}" if marker else text


def _prompt_style():
    global _PROMPT_STYLE
    if _PROMPT_STYLE is None:
        from questionary import Style
        _PROMPT_STYLE = Style([
            ("qmark", "fg:#00e5ff bold"),
            ("question", "bold"),
            ("answer", "fg:#ffd75f bold"),
            ("pointer", "fg:#00e5ff bold"),
            ("highlighted", "fg:#00e5ff bold"),
            ("selected", "fg:#00ff88 bold"),
            ("separator", "fg:#666666"),
            ("instruction", "fg:#888888"),
            ("text", "fg:#ffffff"),
            ("disabled", "fg:#666666 italic"),
        ])
    return _PROMPT_STYLE


def _ask_select(
    message: str,
    choices: list[Any],
    default: Any = None,
    instruction: str | None = None,
) -> Any:
    import questionary

    try:
        return questionary.select(
            message,
            choices=choices,
            default=default,
            instruction=instruction,
            pointer=icon("pointer"),
            qmark=icon("prompt"),
            style=_prompt_style(),
        ).ask()
    except (KeyboardInterrupt, EOFError):
        return None


def _ask_text(message: str, default: str = "", instruction: str | None = None) -> str | None:
    import questionary

    try:
        return questionary.text(
            message,
            default=default,
            instruction=instruction,
            qmark=icon("prompt"),
            style=_prompt_style(),
        ).ask()
    except (KeyboardInterrupt, EOFError):
        return None


def _ask_path(message: str, default: str = "") -> str | None:
    import questionary

    try:
        return questionary.path(
            message,
            default=default,
            qmark=icon("prompt"),
            style=_prompt_style(),
        ).ask()
    except (KeyboardInterrupt, EOFError):
        return None


def _ask_confirm(message: str, default: bool = True) -> bool | None:
    import questionary

    try:
        return questionary.confirm(
            message,
            default=default,
            qmark=icon("prompt"),
            style=_prompt_style(),
        ).ask()
    except (KeyboardInterrupt, EOFError):
        return None


def _remember_route(history: list[str], label: str) -> None:
    if not history or history[-1] != label:
        history.append(label)
    del history[:-6]


def _route_text(history: list[str]) -> str:
    return " > ".join(history[-4:]) if history else "Main"


def _aspect_label(width: int | None, height: int | None) -> str:
    if not width or not height:
        return "preserve"
    divisor = gcd(width, height)
    return f"{width}x{height} ({width // divisor}:{height // divisor})"


class UI:
    """Standardized terminal UI messages and branding."""

    @staticmethod
    def header():
        """Retro TUI branding."""
        console.print()
        console.print(Panel(
            f"[cyan]{icon('app')}[/cyan] [bold white]CLIPPED[/bold white] "
            f"[dim]v{__version__}[/dim]\n"
            "[cyan]Audio clips, album-art reels, and Swinsian automation[/cyan]",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(1, 3),
        ))

    @staticmethod
    def sys(msg: str):
        console.print(f"[bold cyan]{icon('info')} SYS[/bold cyan] {msg}")

    @staticmethod
    def info(msg: str):
        console.print(f"[bold green]{icon('check')} OK[/bold green] {msg}")

    @staticmethod
    def success(msg: str):
        UI.info(msg)

    @staticmethod
    def warn(msg: str):
        console.print(f"[bold yellow]{icon('warn')} WARN[/bold yellow] {msg}")

    @staticmethod
    def err(msg: str):
        console.print(f"[bold red]! ERR[/bold red] {msg}")

    @staticmethod
    def metadata(summary: str):
        console.print(f"\n[bold cyan]{icon('info')} META[/bold cyan] [white]{summary}[/white]\n")


app     = typer.Typer(help="Clipped — high-leverage audio & video automation.", add_completion=False)
console = Console()

app.add_typer(config_app, name="config")
app.add_typer(test_app, name="test")
app.add_typer(batch_app, name="batch")
app.add_typer(docs_app, name="docs")
app.add_typer(remotion_app, name="remotion")

artist_app = typer.Typer(help="Fetch artist/band images and logos using Last.fm, Spotify, Discogs, Fanart.tv, Metal Archives, and AudioDB.", add_completion=False)

@artist_app.command("fetch")
def artist_fetch(
    artist: str = typer.Argument(..., help="Artist name for lookup"),
    out: Optional[str] = typer.Option(None, "--out", "-o", help="Output directory"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing assets"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose log output"),
):
    """Fetch artist photo & logo for a named artist."""
    from .artist_image_fetcher import ArtistImageFetcher
    fetcher = ArtistImageFetcher(force=force, verbose=verbose)
    out_dir = Path(out).expanduser().resolve() if out else Path.cwd() / fetcher.safe_name(artist)
    fetcher.process_artist(artist_name=artist, out_dir=out_dir)

@artist_app.command("folder")
def artist_folder(
    path: str = typer.Argument(..., help="Path to artist library folder"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing assets"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose log output"),
):
    """Scan and fetch assets directly inside an existing artist directory."""
    from .artist_image_fetcher import ArtistImageFetcher
    fetcher = ArtistImageFetcher(force=force, verbose=verbose)
    folder = Path(path).expanduser().resolve()
    fetcher.process_artist(artist_name=folder.name, out_dir=folder, artist_folder=folder)

@artist_app.command("library")
def artist_library(
    genre: str = typer.Option("Metal", "--genre", "-g", help="Subdirectory genre name"),
    letter: Optional[str] = typer.Option(None, "--letter", "-l", help="Specific alphabet letter to process"),
    all_letters: bool = typer.Option(False, "--all", "-a", help="Process all alphabet letters"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing assets"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose log output"),
):
    """Scan and process multiple letters/genres in the audio library."""
    from .artist_image_fetcher import ArtistImageFetcher
    fetcher = ArtistImageFetcher(force=force, verbose=verbose)
    photo_sources = ["spotify", "discogs", "lastfm", "audiodb", "metallum"]
    logo_sources = ["audiodb", "fanart", "metallum"]
    if letter:
        fetcher.process_letter(letter, genre, photo_sources, logo_sources)
    elif all_letters:
        fetcher.process_all(genre, photo_sources, logo_sources)
    else:
        UI.err("Please specify --letter or --all")

app.add_typer(artist_app, name="artist")


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


def _copy_text_to_clipboard(text: str) -> bool:
    result = subprocess.run(["pbcopy"], input=text, text=True, capture_output=True)
    if result.returncode != 0:
        UI.err("Could not copy to clipboard.")
        return False
    return True


def _run_open_command(cmd: list[str], success: str, failure: str) -> None:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        UI.info(success)
        return
    detail = result.stderr.strip() or result.stdout.strip()
    UI.err(f"{failure}{f': {detail}' if detail else ''}")


def _validate_custom_output_path(raw: str, extension: str) -> Path | None:
    extension = extension.lstrip(".")
    raw = raw.strip()
    if not raw:
        UI.err("No output path provided.")
        return None
    if raw.endswith(("/", "\\")):
        UI.err("Choose a full output file path, not only a folder.")
        return None

    path = Path(raw).expanduser()
    if path.exists() and path.is_dir():
        UI.err("Choose a full output file path, not an existing folder.")
        return None
    if not path.suffix:
        path = path.with_suffix(f".{extension}")

    parent = path.parent
    if not parent.exists():
        create = _ask_confirm(f"Create output folder {parent}?", default=True)
        if not create:
            return None
        parent.mkdir(parents=True, exist_ok=True)
    if not parent.is_dir():
        UI.err(f"Output parent is not a directory: {parent}")
        return None

    if path.exists():
        overwrite = _ask_confirm(f"Overwrite existing file {path.name}?", default=False)
        if not overwrite:
            return None
    return path


def _save_recent_output_path(path_str: str) -> None:
    state = load_state()
    recents = state.get("recent_output_paths", [])
    if path_str in recents:
        recents.remove(path_str)
    recents.insert(0, path_str)
    recents = recents[:5]
    update_state("recent_output_paths", recents)


def _choose_output_path(cfg: dict, kind: str, extension: str) -> Path | None | object:
    import questionary

    dir_key = "audio_dir" if kind == "audio" else "video_dir"
    default_dir = Path(cfg.get(dir_key, "")).expanduser()

    state = load_state()
    recents = state.get("recent_output_paths", [])

    filtered_recents = []
    for r in recents:
        try:
            p = Path(r)
            if p.suffix.lower().lstrip(".") == extension.lower().lstrip("."):
                filtered_recents.append(r)
        except Exception:
            pass

    choices = [
        questionary.Choice(
            title=_menu_label("default", f"Use default output path  -  {_short_path(str(default_dir))}"),
            value="default",
        )
    ]

    if filtered_recents:
        choices.append(questionary.Separator("Recent Output Locations"))
        for r in filtered_recents:
            choices.append(questionary.Choice(
                title=_menu_label("default", f"{_short_path(r)}"),
                value=r,
            ))

    choices.extend([
        questionary.Separator(),
        questionary.Choice(
            title=_menu_label("path", "Choose custom output file path"),
            value="custom",
        ),
        questionary.Separator(),
        questionary.Choice(title=_menu_label("back", "Go Back"), value=NAV_BACK),
    ])

    choice = _ask_select(
        "Output destination:",
        choices=choices,
        instruction="custom paths support tab completion",
    )
    if choice in (None, NAV_BACK):
        return OUTPUT_CANCELLED
    if choice == "default":
        return None
    if choice == "custom":
        raw = _ask_path(
            f"Custom {kind} output file:",
            default=f"{default_dir}/",
        )
        if raw is None:
            return OUTPUT_CANCELLED
        custom = _validate_custom_output_path(raw, extension)
        if custom:
            _save_recent_output_path(str(custom))
            return custom
        return OUTPUT_CANCELLED

    picked_path = Path(choice)
    if picked_path.exists():
        overwrite = _ask_confirm(f"Overwrite existing file {picked_path.name}?", default=False)
        if not overwrite:
            return OUTPUT_CANCELLED
    return picked_path


def _handle_completed_output(path: Path | None, cfg: dict) -> None:
    if not path:
        return

    import questionary

    output_path = Path(path).expanduser()
    if cfg.get("auto_open_output", False):
        _run_open_command(
            ["open", str(output_path)],
            f"Opened {_short_path(str(output_path))}",
            "Could not open output",
        )

    while True:
        choice = _ask_select(
            "Output actions:",
            choices=[
                questionary.Choice(title=_menu_label("finder", "Reveal in Finder"), value="finder"),
                questionary.Choice(title=_menu_label("open", "Play / Open file"), value="open"),
                questionary.Choice(title=_menu_label("dropover", "Put in Dropover shelf"), value="dropover"),
                questionary.Choice(title=_menu_label("clipboard", "Copy path to clipboard"), value="copy"),
                questionary.Separator(),
                questionary.Choice(title=_menu_label("home", "Return to main menu"), value=NAV_MAIN),
            ],
        )
        if not choice or choice == NAV_MAIN:
            return
        if choice == "finder":
            _run_open_command(
                ["open", "-R", str(output_path)],
                "Revealed in Finder.",
                "Could not reveal in Finder",
            )
        elif choice == "open":
            _run_open_command(
                ["open", str(output_path)],
                "Opened output.",
                "Could not open output",
            )
        elif choice == "dropover":
            dropover_app = Path("/Applications/Utilities/Dropover.app")
            if not dropover_app.exists():
                UI.err(f"Dropover not found at {dropover_app}")
                continue
            _run_open_command(
                ["open", "-a", "Dropover", str(output_path)],
                "Sent to Dropover.",
                "Could not send to Dropover",
            )
        elif choice == "copy":
            if _copy_text_to_clipboard(str(output_path)):
                UI.info("Copied output path to clipboard.")


def _process_audio_and_complete(cfg: dict, params: dict) -> Path | None:
    path = process_clip(**params)
    _handle_completed_output(path, cfg)
    return path


def _process_video_and_complete(cfg: dict, params: dict) -> Path | None:
    path = process_video(**params)
    _handle_completed_output(path, cfg)
    return path


def _print_tui_context(cfg: dict, last_action: dict | None, menu_history: list[str] | None = None) -> None:
    table = Table.grid(expand=True)
    table.add_column(ratio=1)
    table.add_column(ratio=1)

    last = _last_source()
    defaults = (
        f"[bold]{icon('render')} Default render[/bold]\n"
        f"Template: [cyan]{cfg.get('default_template', 'spinner')}[/cyan]\n"
        f"Platform: [magenta]{cfg.get('default_platform', 'default')}[/magenta]\n"
        f"Fade: [green]{cfg.get('fade_duration', 0.5)}s[/green]\n"
        f"Auto-open: [white]{'on' if cfg.get('auto_open_output') else 'off'}[/white]"
    )
    recent = (
        f"[bold]{icon('home')} Session[/bold]\n"
        f"Last source: [white]{_source_title(last) if last else 'none'}[/white]\n"
        f"Previous action: [white]{last_action['label'] if last_action else 'none'}[/white]\n"
        f"Video dir: [dim]{_short_path(str(Path(cfg.get('video_dir', '')).expanduser()))}[/dim]\n"
        f"Route: [cyan]{_route_text(menu_history or ['Main'])}[/cyan]"
    )

    table.add_row(
        Panel(defaults, title="Preset", border_style="cyan", box=box.ROUNDED),
        Panel(recent, title="Context", border_style="magenta", box=box.ROUNDED),
    )
    console.print(table)
    console.print()


def _choose_source(prompt: str, allow_url: bool = False, allow_history: bool = True) -> str | None:
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
    choices.extend([
        questionary.Separator(),
        questionary.Choice(title=_menu_label("back", "Go Back"), value=("back", None)),
    ])

    selected = _ask_select(prompt, choices=choices)
    if not selected:
        return None

    method, value = selected
    if method == "back":
        return None
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
        src = _ask_path("Audio file path:") or ""
        src = str(Path(src).expanduser()) if src.startswith("~") else src
        return src if src and _validate_source(src, allow_url=allow_url) else ""
    if method == "url":
        src = _ask_text("YouTube URL:") or ""
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
    table = Table.grid(padding=(0, 2))
    table.add_column(style="cyan", no_wrap=True)
    table.add_column(style="white")
    for key, value in rows:
        table.add_row(key, value)
    console.print(Panel(table, title=title, border_style="green", box=box.ROUNDED))
    return bool(_ask_confirm("Run this workflow?", default=True))


def _confirm_video_plan(cfg: dict, title: str, rows: list[tuple[str, str]], is_remotion: bool = False) -> str:
    import questionary

    table = Table.grid(padding=(0, 2))
    table.add_column(style="cyan", no_wrap=True)
    table.add_column(style="white")
    for key, value in rows:
        table.add_row(key, value)
    console.print(Panel(table, title=title, border_style="green", box=box.ROUNDED))

    p_dur = cfg.get("preview_duration", 3.0)
    choices = [
        questionary.Choice(title="🚀 Run full render", value="full"),
    ]
    if is_remotion:
        choices.append(
            questionary.Choice(title="🔍 Open in Remotion Studio (Live Preview)", value="studio")
        )
    choices.append(
        questionary.Choice(
            title=f"⚡ Render short preview ({p_dur}s)",
            value="preview",
        )
    )
    choices.append(questionary.Separator())
    choices.append(questionary.Choice(title="❌ Cancel", value="cancel"))

    choice = _ask_select("Confirm Action:", choices=choices)
    return choice or "cancel"


def _run_interactive_menu(preset_config: dict | None = None) -> None:
    import questionary

    cfg = preset_config or get_config()
    last_action: dict | None = None
    menu_history = ["Main"]

    while True:
        UI.header()
        _print_tui_context(cfg, last_action, menu_history)

        choices = []
        if last_action:
            choices.append(questionary.Choice(
                title=_menu_label("refresh", f"Rerun previous workflow  -  {last_action['label']}"),
                value="rerun",
            ))
            choices.append(questionary.Separator())

        choices += [
            questionary.Choice(
                title=_menu_label("video", "Generate video reel  -  choose source, template, platform, time range"),
                value="video",
            ),
            questionary.Choice(
                title=_menu_label("video", "Render preview of all templates (contact sheet)"),
                value="test-templates",
            ),
            questionary.Choice(
                title=_menu_label("audio", "Clip audio  -  file, Swinsian, last source, or YouTube URL"),
                value="audio",
            ),
            questionary.Separator(),
            questionary.Choice(title=_menu_label("template", "Browse templates"), value="templates"),
            questionary.Choice(title=_menu_label("platform", "Browse platform profiles"), value="platforms"),
            questionary.Choice(title=_menu_label("settings", "Settings"), value="settings"),
            questionary.Choice(title=_menu_label("exit", "Exit"), value="exit"),
        ]

        choice = _ask_select(
            "Choose a workflow:",
            choices=choices,
        )

        if choice is None:
            if _ask_confirm("Exit Clipped?", default=False):
                break
            continue
        if choice == "exit":
            if _ask_confirm("Exit Clipped?", default=True):
                break
            continue

        if choice == "rerun" and last_action:
            last_action["func"](*last_action["args"], **last_action["kwargs"])
            continue

        if choice == "audio":
            _remember_route(menu_history, "Audio")
            action = _interactive_audio(cfg)
            if action:
                last_action = action
            _remember_route(menu_history, "Main")
        elif choice == "video":
            _remember_route(menu_history, "Video")
            action = _interactive_video(cfg)
            if action:
                last_action = action
            _remember_route(menu_history, "Main")
        elif choice == "test-templates":
            _remember_route(menu_history, "Test Templates")
            action = _interactive_test_templates(cfg)
            if action:
                last_action = action
            _remember_route(menu_history, "Main")
        elif choice == "templates":
            _remember_route(menu_history, "Templates")
            action = _interactive_browse_templates(cfg)
            if action:
                last_action = action
            _remember_route(menu_history, "Main")
        elif choice == "platforms":
            _remember_route(menu_history, "Platforms")
            action = _interactive_browse_platforms(cfg)
            if action:
                last_action = action
            _remember_route(menu_history, "Main")
        elif choice == "settings":
            _remember_route(menu_history, "Settings")
            _interactive_settings(cfg)
            _remember_route(menu_history, "Main")


def _set_config_value(cfg: dict, key: str, value: Any) -> bool:
    try:
        update_config_key(key, value)
    except Exception as exc:
        UI.err(f"Could not persist {key}: {exc}")
        return False
    cfg[key] = value
    UI.info(f"Saved {key} = {value}")
    return True


def _print_template_detail(template) -> None:
    info = template.info
    w, h = info.aspect
    table = Table.grid(padding=(0, 2))
    table.add_column(style="cyan", no_wrap=True)
    table.add_column(style="white")
    table.add_row("Name", f"[bold]{info.name}[/bold]")
    table.add_row("Label", info.label)
    table.add_row("Engine", getattr(info, "engine", "ffmpeg"))
    table.add_row("Category", getattr(info, "category", "Legacy FFmpeg"))
    table.add_row("Resolution", _aspect_label(w, h))
    table.add_row("Ideal usage", ", ".join(info.ideal_for) or "general")
    capabilities = ", ".join(getattr(info, "capabilities", []))
    if capabilities:
        table.add_row("Capabilities", capabilities)
    table.add_row("Description", info.description)
    console.print(Panel(
        table,
        title=f"{icon('template')} Template Detail",
        border_style="cyan",
        box=box.ROUNDED,
    ))


def _interactive_template_detail(cfg: dict, template) -> dict | str | None:
    import questionary

    while True:
        _print_template_detail(template)
        choice = _ask_select(
            "Template actions:",
            choices=[
                questionary.Choice(
                    title=_menu_label("render", "Render video with template"),
                    value="render",
                ),
                questionary.Choice(
                    title=_menu_label("default", "Set as default template"),
                    value="default",
                ),
                questionary.Separator(),
                questionary.Choice(
                    title=_menu_label("back", "Back to templates list"),
                    value=NAV_BACK,
                ),
                questionary.Choice(
                    title=_menu_label("home", "Return to main menu"),
                    value=NAV_MAIN,
                ),
            ],
        )
        if not choice:
            return NAV_BACK
        if choice in (NAV_BACK, NAV_MAIN):
            return choice
        if choice == "default":
            _set_config_value(cfg, "default_template", template.info.name)
            continue
        if choice == "render":
            action = _interactive_video(cfg, template_override=template.info.name)
            return action or NAV_BACK


def _interactive_browse_templates(cfg: dict) -> dict | None:
    import questionary

    while True:
        _print_templates()
        templates = list_templates()
        choices = []
        for group, group_templates in {
            "Remotion Templates": [t for t in templates if getattr(t.info, "engine", "ffmpeg") == "remotion"],
            "Legacy FFmpeg Templates": [t for t in templates if getattr(t.info, "engine", "ffmpeg") != "remotion"],
        }.items():
            if not group_templates:
                continue
            if choices:
                choices.append(questionary.Separator())
            choices.append(questionary.Separator(group))
            for t in group_templates:
                choices.append(questionary.Choice(
                    title=f"{t.info.label}  ({t.info.name})  -  {_aspect_label(*t.info.aspect)}",
                    value=t.info.name,
                ))
        choices.extend([
            questionary.Separator(),
            questionary.Choice(title=_menu_label("back", "Go Back"), value=NAV_BACK),
            questionary.Choice(title=_menu_label("home", "Return to main menu"), value=NAV_MAIN),
        ])
        selected = _ask_select("Choose a template:", choices=choices)
        if selected in (None, NAV_BACK, NAV_MAIN):
            return None

        template = next((t for t in templates if t.info.name == selected), None)
        if not template:
            UI.err(f"Template not found: {selected}")
            continue
        result = _interactive_template_detail(cfg, template)
        if isinstance(result, dict):
            return result
        if result == NAV_MAIN:
            return None


def _print_platform_detail(platform) -> None:
    table = Table.grid(padding=(0, 2))
    table.add_column(style="cyan", no_wrap=True)
    table.add_column(style="white")
    duration = f"{platform.max_duration:.0f}s" if platform.max_duration else "no cap"
    size = _aspect_label(platform.width, platform.height)
    codecs = (
        f"{platform.video_codec} / {platform.audio_codec} "
        f"{platform.audio_bitrate}"
        if platform.output_format != "mp3"
        else f"{platform.audio_codec} {platform.audio_bitrate}"
    )
    table.add_row("Name", f"[bold]{platform.name}[/bold]")
    table.add_row("Label", platform.label)
    table.add_row("Resolution", size)
    table.add_row("Duration cap", duration)
    table.add_row("Format", platform.output_format)
    table.add_row("Codecs", codecs)
    table.add_row("Notes", platform.notes or "none")
    console.print(Panel(
        table,
        title=f"{icon('platform')} Platform Detail",
        border_style="magenta",
        box=box.ROUNDED,
    ))


def _interactive_platform_detail(cfg: dict, platform) -> dict | str | None:
    import questionary

    while True:
        _print_platform_detail(platform)
        choice = _ask_select(
            "Platform actions:",
            choices=[
                questionary.Choice(
                    title=_menu_label("render", "Generate video using platform"),
                    value="render",
                ),
                questionary.Choice(
                    title=_menu_label("default", "Set as default platform"),
                    value="default",
                ),
                questionary.Separator(),
                questionary.Choice(
                    title=_menu_label("back", "Back to platforms list"),
                    value=NAV_BACK,
                ),
                questionary.Choice(
                    title=_menu_label("home", "Return to main menu"),
                    value=NAV_MAIN,
                ),
            ],
        )
        if not choice:
            return NAV_BACK
        if choice in (NAV_BACK, NAV_MAIN):
            return choice
        if choice == "default":
            _set_config_value(cfg, "default_platform", platform.name)
            continue
        if choice == "render":
            action = _interactive_video(cfg, platform_override=platform.name)
            return action or NAV_BACK


def _interactive_browse_platforms(cfg: dict) -> dict | None:
    import questionary

    while True:
        _print_platforms()
        platforms = list_platforms()
        choices = []
        for p in platforms:
            duration = f"{p.max_duration:.0f}s max" if p.max_duration else "no cap"
            choices.append(questionary.Choice(
                title=f"{p.label}  ({p.name})  -  {_aspect_label(p.width, p.height)}; {duration}",
                value=p.name,
            ))
        choices.extend([
            questionary.Separator(),
            questionary.Choice(title=_menu_label("back", "Go Back"), value=NAV_BACK),
            questionary.Choice(title=_menu_label("home", "Return to main menu"), value=NAV_MAIN),
        ])
        selected = _ask_select("Choose a platform:", choices=choices)
        if selected in (None, NAV_BACK, NAV_MAIN):
            return None

        platform = PLATFORMS.get(selected)
        if not platform:
            UI.err(f"Platform not found: {selected}")
            continue
        result = _interactive_platform_detail(cfg, platform)
        if isinstance(result, dict):
            return result
        if result == NAV_MAIN:
            return None


def _print_settings(cfg: dict) -> None:
    table = Table(title=f"{icon('settings')} Settings", box=box.ROUNDED, highlight=True)
    table.add_column("Setting", style="cyan", no_wrap=True)
    table.add_column("Current Value", style="white")
    rows = [
        ("default_template", cfg.get("default_template", "spinner")),
        ("default_platform", cfg.get("default_platform", "default")),
        ("auto_fade", "enabled" if cfg.get("auto_fade", True) else "disabled"),
        ("fade_duration", f"{cfg.get('fade_duration', 0.5)}s"),
        ("copy_to_clipboard", "enabled" if cfg.get("copy_to_clipboard", True) else "disabled"),
        ("auto_open_output", "enabled" if cfg.get("auto_open_output", False) else "disabled"),
        ("preview_duration", f"{cfg.get('preview_duration', 3.0)}s"),
        ("remotion_style", cfg.get("remotion_style", "classic")),
        ("remotion_motion", cfg.get("remotion_motion", "medium")),
        ("remotion_waveform", cfg.get("remotion_waveform", "radial")),
        ("remotion_palette", cfg.get("remotion_palette", "auto")),
        ("audio_dir", _short_path(str(Path(cfg.get("audio_dir", "")).expanduser()))),
        ("video_dir", _short_path(str(Path(cfg.get("video_dir", "")).expanduser()))),
    ]
    for key, value in rows:
        table.add_row(key, f"[bold]{value}[/bold]")
    console.print(table)


def _choose_bool_setting(key: str, current: bool) -> bool | None:
    import questionary

    selected = _ask_select(
        f"{key}:",
        choices=[
            questionary.Choice(title="Enabled", value=True),
            questionary.Choice(title="Disabled", value=False),
            questionary.Separator(),
            questionary.Choice(title=_menu_label("back", "Go Back"), value=NAV_BACK),
        ],
        default=True if current else False,
    )
    if selected in (None, NAV_BACK):
        return None
    return bool(selected)


def _validate_output_dir_setting(raw: str) -> str | None:
    cleaned = raw.strip().rstrip("/") or "/"
    if not cleaned:
        UI.err("No directory provided.")
        return None
    expanded = Path(cleaned).expanduser()
    if expanded.exists() and not expanded.is_dir():
        UI.err(f"Not a directory: {expanded}")
        return None
    if not expanded.exists():
        create = _ask_confirm(f"Create output folder {expanded}?", default=True)
        if not create:
            return None
        expanded.mkdir(parents=True, exist_ok=True)
    return cleaned


def _interactive_settings(cfg: dict) -> None:
    import questionary

    while True:
        _print_settings(cfg)
        choice = _ask_select(
            "Edit setting:",
            choices=[
                questionary.Choice(title="Default template", value="default_template"),
                questionary.Choice(title="Default platform", value="default_platform"),
                questionary.Choice(title="Fade enabled", value="auto_fade"),
                questionary.Choice(title="Fade duration", value="fade_duration"),
                questionary.Choice(title="Clipboard behavior", value="copy_to_clipboard"),
                questionary.Choice(title="Auto-open output", value="auto_open_output"),
                questionary.Choice(title="Preview duration", value="preview_duration"),
                questionary.Choice(title="Remotion style", value="remotion_style"),
                questionary.Choice(title="Remotion motion", value="remotion_motion"),
                questionary.Choice(title="Remotion waveform", value="remotion_waveform"),
                questionary.Choice(title="Remotion palette", value="remotion_palette"),
                questionary.Choice(title="Default audio output directory", value="audio_dir"),
                questionary.Choice(title="Default video output directory", value="video_dir"),
                questionary.Separator(),
                questionary.Choice(title=_menu_label("home", "Return to main menu"), value=NAV_MAIN),
            ],
        )
        if choice in (None, NAV_MAIN):
            return

        if choice == "default_template":
            selected = _pick_template(default=cfg.get("default_template"))
            if selected:
                _set_config_value(cfg, "default_template", selected)
        elif choice == "default_platform":
            selected = _pick_platform(default=cfg.get("default_platform"))
            if selected:
                _set_config_value(cfg, "default_platform", selected)
        elif choice in {"auto_fade", "copy_to_clipboard", "auto_open_output"}:
            selected = _choose_bool_setting(choice, bool(cfg.get(choice, False)))
            if selected is not None:
                _set_config_value(cfg, choice, selected)
        elif choice == "fade_duration":
            raw = _ask_text(
                "Fade duration (seconds):",
                default=str(cfg.get("fade_duration", 0.5)),
            )
            if raw is None:
                continue
            parsed = _parse_optional_float(raw, "Fade duration")
            if parsed is not None:
                _set_config_value(cfg, "fade_duration", parsed)
        elif choice == "preview_duration":
            raw = _ask_text(
                "Preview duration (seconds):",
                default=str(cfg.get("preview_duration", 3.0)),
            )
            if raw is None:
                continue
            parsed = _parse_optional_float(raw, "Preview duration")
            if parsed is not None:
                _set_config_value(cfg, "preview_duration", parsed)
        elif choice in {"remotion_style", "remotion_motion", "remotion_waveform", "remotion_palette"}:
            choices_map = {
                "remotion_style": ["classic", "brutal", "neon", "zine", "cinematic"],
                "remotion_motion": ["low", "medium", "high"],
                "remotion_waveform": ["none", "bars", "radial", "ring"],
                "remotion_palette": ["auto", "cyan", "red", "gold", "mono"],
            }
            selected = _ask_select(
                choice,
                choices=choices_map[choice],
                default=cfg.get(choice),
            )
            if selected:
                _set_config_value(cfg, choice, selected)
        elif choice in {"audio_dir", "video_dir"}:
            raw = _ask_path(
                f"{choice} directory:",
                default=str(Path(cfg.get(choice, "")).expanduser()),
            )
            if raw is None:
                continue
            cleaned = _validate_output_dir_setting(raw)
            if cleaned:
                _set_config_value(cfg, choice, cleaned)


def _interactive_audio(cfg: dict) -> dict | None:
    src = _choose_source("Audio source:", allow_url=True)

    if src is None:
        return
    if not src:
        UI.err("No source provided.")
        return

    _print_source_summary(src)

    start_answer = _ask_text("Start time:", default="0")
    if start_answer is None:
        return None
    start = start_answer or "0"
    end = _ask_text("End time:", instruction="M:SS, H:MM:SS, or seconds")
    if end is None:
        return
    end = end or ""

    if not end:
        UI.err("End time is required.")
        return

    # Fade prompts
    fade_in = _ask_text(
        "Fade in duration (seconds):",
        default=str(cfg.get("fade_duration", 0.5))
    )
    fade_out = _ask_text(
        "Fade out duration (seconds):",
        default=str(cfg.get("fade_duration", 0.5))
    )
    if fade_in is None or fade_out is None:
        return

    is_url = _is_url(src)
    fade_in_value = _parse_optional_float(fade_in, "Fade in duration")
    fade_out_value = _parse_optional_float(fade_out, "Fade out duration")
    if (fade_in and fade_in_value is None) or (fade_out and fade_out_value is None):
        return

    output_path = _choose_output_path(cfg, "audio", "mp3")
    if output_path is OUTPUT_CANCELLED:
        return

    params = {
        "src": src,
        "start": parse_time(start),
        "end": parse_time(end),
        "is_url": is_url,
        "fade_in": fade_in_value,
        "fade_out": fade_out_value,
        "output_path": output_path,
    }
    output_label = (
        _short_path(str(output_path))
        if isinstance(output_path, Path)
        else _short_path(str(Path(cfg.get("audio_dir", "")).expanduser()))
    )

    if not _confirm_plan("Audio Clip", [
        ("Source", _source_title(src)),
        ("Range", f"{start} -> {end}"),
        ("Fade", f"in {fade_in or 'auto'}s / out {fade_out or 'auto'}s"),
        ("Output", output_label),
    ]):
        return

    _process_audio_and_complete(cfg, params)

    return {
        "func": _process_audio_and_complete,
        "args": [cfg, params],
        "kwargs": {},
        "label": f"Audio Clip ({Path(src).name if not is_url else src[:30]})",
    }


def _interactive_video(
    cfg: dict,
    template_override: str | None = None,
    platform_override: str | None = None,
) -> dict | None:
    src = _choose_source("Video source:", allow_url=False)

    if src is None:
        return None
    if not src:
        UI.err("No file selected.")
        return None

    assets = _print_source_summary(src)

    # Asset Overrides
    cover_override = None
    logo_override = None
    background_override = None
    media_override = None
    lyrics_override = None

    if _ask_confirm("Provide custom assets (cover, logo, background, media, lyrics)?", default=False):
        cover_answer = _ask_text("Cover image path/URL:", default="")
        if cover_answer: cover_override = cover_answer
        
        logo_answer = _ask_text("Logo image path/URL:", default="")
        if logo_answer: logo_override = logo_answer
        
        bg_answer = _ask_text("Background image path/URL:", default="")
        if bg_answer: background_override = bg_answer
        
        media_answer = _ask_text("Media (video/image) path/URL:", default="")
        if media_answer: media_override = media_answer
        
        lyrics_answer = _ask_text("Lyrics (.lrc/.srt) path/URL:", default="")
        if lyrics_answer: lyrics_override = lyrics_answer

    # Template picker
    state = load_state()
    default_template = state.get("last_used_template") or cfg.get("default_template")
    template_name = template_override or _pick_template(default=default_template)
    if not template_name:
        return None

    # Platform picker
    default_platform = state.get("last_used_platform") or cfg.get("default_platform")
    platform_name = platform_override or _pick_platform(default=default_platform)
    if not platform_name:
        return None

    # Custom fade sequence
    sequence = _build_fade_sequence(assets) if template_name == "fade" else None

    # Custom waveform options
    waveform_cfg = _build_waveform_config() if template_name == "waveformbar" else {}
    remotion_cfg = (
        _build_remotion_config(template_name, cfg)
        if template_engine(template_name) == "remotion"
        else {}
    )

    start_answer = _ask_text("Start time:", default="0", instruction="optional")
    if start_answer is None:
        return None
    start = start_answer or "0"
    end = _ask_text("End time:", instruction="blank means full file")
    if end is None:
        return None
    end = end or ""
    fade_in = _ask_text(
        "Audio fade in:",
        default=str(cfg.get("fade_duration", 0.5)),
        instruction="seconds; blank = config default",
    )
    fade_out = _ask_text(
        "Audio fade out:",
        default=str(cfg.get("fade_duration", 0.5)),
        instruction="seconds; blank = config default",
    )
    if fade_in is None or fade_out is None:
        return None

    fade_in_value = _parse_optional_float(fade_in, "Audio fade in")
    fade_out_value = _parse_optional_float(fade_out, "Audio fade out")
    if (fade_in and fade_in_value is None) or (fade_out and fade_out_value is None):
        return None

    profile = PLATFORMS.get(platform_name)
    output_kind = "audio" if profile and profile.output_format == "mp3" else "video"
    output_path = _choose_output_path(
        cfg,
        output_kind,
        profile.output_format if profile else "mp4",
    )
    if output_path is OUTPUT_CANCELLED:
        return None

    params = {
        "src": src,
        "template_name": template_name,
        "platform_name": platform_name,
        "start": parse_time(start),
        "end": parse_time(end) if end else None,
        "sequence": sequence,
        "extra_config": {**waveform_cfg, **remotion_cfg} or None,
        "fade_in": fade_in_value,
        "fade_out": fade_out_value,
        "output_path": output_path,
        "cover": cover_override,
        "logo": logo_override,
        "background": background_override,
        "media": media_override,
        "lyrics": lyrics_override,
    }

    # Duration and template warnings
    template_cls = REGISTRY.get(template_name)
    safe_hint = getattr(template_cls.info, "safe_duration_hint", None) if template_cls else None
    
    start_secs = params["start"]
    end_secs = params["end"]
    if end_secs is not None:
        calc_dur = end_secs - start_secs
    else:
        calc_dur = (assets.duration or 30.0) - start_secs

    if safe_hint and calc_dur > safe_hint:
        UI.warn(
            f"Template '{template_name}' is computationally heavy.\n"
            f"  Safe duration is <= {safe_hint}s, but requested render is {calc_dur:.1f}s.\n"
            f"  Full renders may be slow. Consider rendering a short preview first."
        )

    range_label = f"{start} -> {end}" if end else f"{start} -> full file"
    output_dir_key = "audio_dir" if output_kind == "audio" else "video_dir"
    output_label = (
        _short_path(str(output_path))
        if isinstance(output_path, Path)
        else _short_path(str(Path(cfg.get(output_dir_key, "")).expanduser()))
    )
    
    plan_rows = [
        ("Source", _source_title(src)),
        ("Track", (assets.track_title if assets else Path(src).stem) or Path(src).stem),
        ("Template", template_name),
        ("Platform", platform_name),
        ("Range", range_label),
        ("Fade", f"in {fade_in or 'auto'}s / out {fade_out or 'auto'}s"),
        ("Output", output_label),
    ]
    if remotion_cfg:
        plan_rows.append(("Remotion", ", ".join(f"{k}={v}" for k, v in remotion_cfg.items()) or "defaults"))
    action_type = _confirm_video_plan(
        cfg, "Video Render", plan_rows,
        is_remotion=(template_engine(template_name) == "remotion")
    )

    if action_type == "cancel":
        return None

    if action_type == "studio":
        from .video import run_preview
        run_preview(
            src=src,
            template_name=template_name,
            platform_name=platform_name,
            start=parse_time(start),
            end=parse_time(end) if end else None,
            cover=cover_override,
            logo=logo_override,
            background=background_override,
            media=media_override,
            lyrics=lyrics_override,
        )
        return None

    update_state("last_used_template", template_name)
    update_state("last_used_platform", platform_name)

    if action_type == "preview":
        p_dur = cfg.get("preview_duration", 3.0)
        params["end"] = params["start"] + p_dur
        if isinstance(output_path, Path):
            params["output_path"] = output_path.with_name(f"{output_path.stem} [preview]{output_path.suffix}")
        else:
            params["extra_config"] = params.get("extra_config") or {}
            params["extra_config"]["is_preview_render"] = True

    _process_video_and_complete(cfg, params)

    return {
        "func": _process_video_and_complete,
        "args": [cfg, params],
        "kwargs": {},
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
    style:         Optional[str] = typer.Option(None, "--style", help="Remotion style: classic|brutal|neon|zine|cinematic"),
    motion:        Optional[str] = typer.Option(None, "--motion", help="Remotion motion level: low|medium|high"),
    waveform:      Optional[str] = typer.Option(None, "--waveform", help="Remotion waveform: none|bars|radial|ring"),
    palette:       Optional[str] = typer.Option(None, "--palette", help="Remotion palette: auto|cyan|red|gold|mono"),
    scene_pack:    Optional[str] = typer.Option(None, "--scene-pack", help="Remotion scene pack"),
    effects:       Optional[str] = typer.Option(None, "--effects", help="Remotion effects: clean|texture|grain|blur"),
    captions:      Optional[str] = typer.Option(None, "--captions", help="Remotion captions: off|metadata|lyrics|lower_third|impact"),
    seed:          Optional[str] = typer.Option(None, "--seed", help="Remotion deterministic visual seed"),
    fade_in:       Optional[float] = typer.Option(None, "--fade-in",      help="Audio fade-in duration (seconds)"),
    fade_out:      Optional[float] = typer.Option(None, "--fade-out",     help="Audio fade-out duration (seconds)"),
    dry_run:       bool          = typer.Option(False, "--dry-run", help="Print FFmpeg command, don't run"),
    output:        Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    cover:         Optional[str] = typer.Option(None, "--cover", help="Path or URL to cover image"),
    logo:          Optional[str] = typer.Option(None, "--logo", help="Path or URL to logo image"),
    background:    Optional[str] = typer.Option(None, "--background", help="Path or URL to background image"),
    media:         Optional[str] = typer.Option(None, "--media", help="Path or URL to media file"),
    lyrics:        Optional[str] = typer.Option(None, "--lyrics", help="Path or URL to lyrics file"),
    clean_logo:    Optional[bool] = typer.Option(None, "--clean-logo/--no-clean-logo", help="Clean logo background using rmbg"),
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
    if style:          extra["style"]          = style
    if motion:         extra["motion"]         = motion
    if waveform:       extra["waveform"]       = waveform
    if palette:        extra["palette"]        = palette
    if scene_pack:     extra["scene_pack"]     = scene_pack
    if effects:        extra["effects"]        = effects
    if captions:       extra["captions"]       = captions
    if seed:           extra["seed"]           = seed
    if clean_logo is not None: extra["clean_logo"] = clean_logo

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
        cover=cover,
        logo=logo,
        background=background,
        media=media,
        lyrics=lyrics,
        clean_logo=clean_logo,
    )


@app.command("preview")
def preview_cmd(
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
    duration:      Optional[float] = typer.Option(None, "--duration", "-d", help="Preview duration"),
    preset:        Optional[str] = typer.Option(None,          help="Named preset from config.toml"),
    style:         Optional[str] = typer.Option(None, "--style", help="Remotion style"),
    motion:        Optional[str] = typer.Option(None, "--motion", help="Remotion motion level"),
    waveform:      Optional[str] = typer.Option(None, "--waveform", help="Remotion waveform"),
    palette:       Optional[str] = typer.Option(None, "--palette", help="Remotion palette"),
    scene_pack:    Optional[str] = typer.Option(None, "--scene-pack", help="Remotion scene pack"),
    effects:       Optional[str] = typer.Option(None, "--effects", help="Remotion effects"),
    captions:      Optional[str] = typer.Option(None, "--captions", help="Remotion captions"),
    seed:          Optional[str] = typer.Option(None, "--seed", help="Remotion deterministic visual seed"),
    fade_in:       Optional[float] = typer.Option(None, "--fade-in",      help="Audio fade-in duration (seconds)"),
    fade_out:      Optional[float] = typer.Option(None, "--fade-out",     help="Audio fade-out duration (seconds)"),
    cover:         Optional[str] = typer.Option(None, "--cover", help="Path or URL to cover image"),
    logo:          Optional[str] = typer.Option(None, "--logo", help="Path or URL to logo image"),
    background:    Optional[str] = typer.Option(None, "--background", help="Path or URL to background image"),
    media:         Optional[str] = typer.Option(None, "--media", help="Path or URL to media file"),
    lyrics:        Optional[str] = typer.Option(None, "--lyrics", help="Path or URL to lyrics file"),
    clean_logo:    Optional[bool] = typer.Option(None, "--clean-logo/--no-clean-logo", help="Clean logo background using rmbg"),
    port:          int = typer.Option(3000, "--port", "-p", help="Remotion Studio port."),
):
    """
    Stage a visual template and launch the Remotion Studio preview (or render a short FFmpeg preview).
    """
    base_cfg = get_config()

    final_src = src
    final_template = template or base_cfg.get("default_template", "spinner")
    final_platform = platform or base_cfg.get("default_platform", "default")

    if target in REGISTRY and src:
        final_template = target
        final_src = src
    elif not src:
        final_src = target
    else:
        final_src = target

    if preset:
        try:
            cfg = get_preset(preset)
            final_template = cfg.get("default_template", final_template)
            final_platform = cfg.get("default_platform", final_platform)
        except ValueError as e:
            UI.err(str(e)); raise typer.Exit(1)

    if not final_src or not _validate_source(final_src, allow_url=False):
        raise typer.Exit(1)

    from .video import run_preview
    try:
        run_preview(
            src=final_src,
            template_name=final_template,
            platform_name=final_platform,
            start=parse_time(start) if start else 0.0,
            end=parse_time(end) if end else None,
            duration=duration,
            port=port,
            cover=cover,
            logo=logo,
            background=background,
            media=media,
            lyrics=lyrics,
            clean_logo=clean_logo,
        )
    except Exception as e:
        UI.err(f"Preview failed: {e}")
        raise typer.Exit(1)


# ── Browse command ────────────────────────────────────────────────────────────

@app.command("templates")
def templates_cmd():
    """List all available video templates."""
    _print_templates()


# ── UI Helpers ────────────────────────────────────────────────────────────────

def _build_fade_sequence(assets: "MediaAssets") -> list | None:
    """Interactive builder for image sequences."""
    if not assets.all_images:
        return None
    if not _ask_confirm("Build custom image sequence?", default=False):
        return None

    sequence = []
    remaining = assets.all_images.copy()
    while remaining:
        img = _ask_select(
            "Add image (or Done):",
            choices=[str(p.name) for p in remaining] + ["Done"],
        )
        if not img or img == "Done":
            break
        path = next(p for p in remaining if p.name == img)
        dur = _ask_text(f"Duration for {img} (seconds):", default="5.0")
        if dur is None:
            break
        sequence.append((path, float(dur)))
        remaining.remove(path)
        if not _ask_confirm("Add another?", default=True):
            break
    return sequence


def _build_waveform_config() -> dict:
    """Interactive builder for waveformbar options."""
    import re
    cfg = {}
    wf_mode = _ask_select(
        "Waveform style:",
        choices=[
            "line   — smooth continuous line (recommended)",
            "cline  — centered line (mirror up/down)",
            "p2p    — peak-to-peak bars",
            "point  — point scatter",
        ],
    )
    if wf_mode:
        cfg["waveform_mode"] = wf_mode.split()[0]

    color_custom = _ask_select(
        "Waveform colour:",
        choices=[
            "Cyan   (0x00E5FF) — default",
            "White  (0xFFFFFF)",
            "Gold   (0xFFD700)",
            "Red    (0xFF2D55)",
            "Green  (0x00FF88)",
            "Custom (enter hex)",
        ],
    )
    if color_custom:
        if color_custom.startswith("Custom"):
            hex_val = _ask_text("Hex colour (e.g. 0xFF0000):") or "0x00E5FF"
            cfg["waveform_color"] = hex_val
        else:
            m = re.search(r"(0x[0-9A-Fa-f]{6})", color_custom)
            if m:
                cfg["waveform_color"] = m.group(1)
    return cfg


def _build_remotion_config(template_name: str, cfg: dict) -> dict:
    """Interactive builder for Remotion template options from manifest metadata."""
    import questionary

    option_schema, defaults = remotion_template_options(template_name)
    if not option_schema:
        return {}

    values: dict = {}
    key_labels = {
        "style": "Visual style",
        "motion": "Motion intensity",
        "waveform": "Audio visualizer",
        "palette": "Palette",
        "scene_pack": "Scene pack",
        "effects": "Effects",
        "captions": "Captions",
        "seed": "Seed",
    }

    for key, choices in option_schema.items():
        default = (
            cfg.get(f"remotion_{key}")
            or defaults.get(key)
            or (choices[0] if isinstance(choices, list) and choices else "")
        )
        if key == "captions":
            default_toggle = default not in ("off", False, None)
            selected = _ask_confirm(key_labels.get(key, key), default=default_toggle)
            if selected is None:
                continue
            values[key] = "lyrics" if selected else "off"
            continue

        if choices == "text":
            raw = _ask_text(key_labels.get(key, key), default=str(default or ""), instruction="optional")
            if raw is None:
                continue
            if raw:
                values[key] = raw
            continue

        if isinstance(choices, list):
            prompt_choices = [
                questionary.Choice(title=str(choice), value=str(choice))
                for choice in choices
            ]
            selected = _ask_select(
                key_labels.get(key, key),
                choices=prompt_choices,
                default=str(default) if default else None,
            )
            if selected:
                values[key] = selected

    return values


def _pick_template(default: str | None = None) -> str | None:
    import questionary
    templates = list_templates()
    choices = []
    default_choice = None
    grouped = {
        "Remotion Templates": [t for t in templates if getattr(t.info, "engine", "ffmpeg") == "remotion"],
        "Legacy FFmpeg Templates": [t for t in templates if getattr(t.info, "engine", "ffmpeg") != "remotion"],
    }
    for group, group_templates in grouped.items():
        if not group_templates:
            continue
        if choices:
            choices.append(questionary.Separator())
        choices.append(questionary.Separator(group))
        for t in group_templates:
            w, h = t.info.aspect
            engine = getattr(t.info, "engine", "ffmpeg")
            title = (
                f"{t.info.label}  ({t.info.name})  -  "
                f"{engine}; {w}x{h}; {', '.join(t.info.ideal_for) or 'general'}"
            )
            choice = questionary.Choice(title=title, value=t.info.name)
            choices.append(choice)
            if t.info.name == default:
                default_choice = choice
    if not default_choice and templates:
        default_choice = choices[1] if len(choices) > 1 else None
    choices.extend([
        questionary.Separator(),
        questionary.Choice(title=_menu_label("back", "Go Back"), value=NAV_BACK),
    ])
    selected = _ask_select(
        "Template:",
        choices=choices,
        default=default_choice,
        instruction="choose the visual style",
    )
    return None if selected in (None, NAV_BACK) else selected


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
    choices.extend([
        questionary.Separator(),
        questionary.Choice(title=_menu_label("back", "Go Back"), value=NAV_BACK),
    ])
    selected = _ask_select(
        "Platform:",
        choices=choices,
        default=default_choice,
        instruction="sets size, duration cap, and output format",
    )
    return None if selected in (None, NAV_BACK) else selected


def _print_templates():
    table = Table(title=f"{icon('template')} Templates", box=box.ROUNDED, highlight=True)
    table.add_column("Name",        style="cyan",    width=12)
    table.add_column("Engine",      style="magenta", width=10)
    table.add_column("Label",       style="white",   width=30)
    table.add_column("Size",        style="green",   width=12)
    table.add_column("Ideal For",   style="yellow")

    for t in list_templates():
        w, h = t.info.aspect
        table.add_row(
            t.info.name,
            getattr(t.info, "engine", "ffmpeg"),
            t.info.label,
            f"{w}x{h}",
            ", ".join(t.info.ideal_for),
        )
    console.print(table)


# ── Platforms info command ────────────────────────────────────────────────────

@app.command("platforms")
def platforms_cmd():
    """List all available platform export profiles."""
    table = Table(title=f"{icon('platform')} Platform Profiles", box=box.ROUNDED, highlight=True)
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Label", style="white")
    table.add_column("Profile", style="green")
    table.add_column("Best Template", style="dim")

    for p in list_platforms():
        size = f"{p.width}x{p.height}" if p.width else "-"
        dur  = f"{p.max_duration:.0f}s" if p.max_duration else "-"
        table.add_row(
            p.name,
            p.label,
            f"{size} / {dur} / {p.output_format}",
            suggested_template(p.name),
        )
    console.print(table)


def _print_platforms():
    platforms_cmd()


def _interactive_test_templates(cfg: dict) -> dict | None:
    src = _choose_source("Test Templates Source:", allow_url=False)
    if src is None or not src:
        return None

    start_answer = _ask_text("Start time:", default="00:00", instruction="optional")
    if start_answer is None:
        return None
    start = start_answer or "00:00"

    p_dur = cfg.get("preview_duration", 3.0)
    dur_answer = _ask_text("Duration:", default=str(p_dur), instruction="seconds")
    if dur_answer is None:
        return None
    duration = _parse_optional_float(dur_answer, "Duration") or p_dur

    out_dir = Path("~/Music/clipped/_previews").expanduser()
    out_dir_answer = _ask_text("Output directory:", default=str(out_dir))
    if out_dir_answer is None:
        return None
    out_dir_path = Path(out_dir_answer or out_dir).expanduser()
    out_dir_path.mkdir(parents=True, exist_ok=True)

    templates = list_templates()
    start_secs = parse_time(start)
    end_secs = start_secs + duration

    UI.sys(f"Rendering {len(templates)} template previews from {start} ({duration}s duration) into {out_dir_path}...")

    for t in templates:
        name = t.info.name
        platform_name = default_platform_for_template(name)

        profile = PLATFORMS.get(platform_name)
        out_ext = profile.output_format if profile else "mp4"

        audio_stem = Path(src).stem
        out_path = out_dir_path / f"{audio_stem} ({name}) [preview].{out_ext}"

        UI.sys(f"=== Preview rendering: {name} (Platform: {platform_name}) ===")
        try:
            process_video(
                src,
                template_name=name,
                platform_name=platform_name,
                start=start_secs,
                end=end_secs,
                output_path=out_path,
            )
        except Exception as e:
            UI.err(f"Failed to render preview for template '{name}': {e}")

    UI.success(f"All template previews rendered successfully in {out_dir_path}!")

    if _ask_confirm("Open previews directory in Finder?", default=True):
        subprocess.run(["open", str(out_dir_path)])

    if _ask_confirm("Send previews to Dropover shelf?", default=False):
        for t in templates:
            name = t.info.name
            p_name = default_platform_for_template(name)
            prof = PLATFORMS.get(p_name)
            ext = prof.output_format if prof else "mp4"
            p_file = out_dir_path / f"{Path(src).stem} ({name}) [preview].{ext}"
            if p_file.exists():
                subprocess.run(["open", "-a", "Dropover", str(p_file)])

    return {
        "func": _interactive_test_templates,
        "args": [cfg],
        "kwargs": {},
        "label": f"Test Templates: {Path(src).name}",
    }


@app.command("test-templates")
@app.command("preview-templates", hidden=True)
def test_templates_cmd(
    src: str = typer.Argument(
        ...,
        help="Path to audio file to render previews with."
    ),
    start: str = typer.Option(
        "00:00",
        "--start", "-s",
        help="Start time offset (e.g. 01:00 or 60)."
    ),
    duration: Optional[float] = typer.Option(
        None,
        "--duration", "-d",
        help="Duration of the preview clips (seconds)."
    ),
    output_dir: Optional[str] = typer.Option(
        None,
        "--output-dir", "-o",
        help="Output directory for the preview clips (defaults to ~/Music/clipped/_previews)."
    ),
):
    """
    Render a short preview clip of every template using the given audio file.
    Creates a suite of reference preview videos inside the previews folder.
    """
    is_url = _is_url(src)
    if not _validate_source(src, allow_url=is_url):
        raise typer.Exit(1)

    cfg = get_config()
    out_dir = Path(output_dir or "~/Music/clipped/_previews").expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    dur = duration if duration is not None else cfg.get("preview_duration", 3.0)
    start_secs = parse_time(start) if start else 0.0
    end_secs = start_secs + dur

    templates = list_templates()

    UI.sys(f"Rendering {len(templates)} template previews from {start} ({dur}s duration) into {out_dir}...")

    for t in templates:
        name = t.info.name
        platform_name = default_platform_for_template(name)

        profile = PLATFORMS.get(platform_name)
        out_ext = profile.output_format if profile else "mp4"

        audio_stem = Path(src).stem
        out_path = out_dir / f"{audio_stem} ({name}) [preview].{out_ext}"

        UI.sys(f"=== Preview rendering: {name} (Platform: {platform_name}) ===")
        try:
            process_video(
                src,
                template_name=name,
                platform_name=platform_name,
                start=start_secs,
                end=end_secs,
                output_path=out_path,
            )
        except Exception as e:
            UI.err(f"Failed to render preview for template '{name}': {e}")

    UI.success(f"All template previews rendered successfully in {out_dir}!")


if __name__ == "__main__":
    app()
