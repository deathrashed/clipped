from __future__ import annotations

import time
from pathlib import Path
from typing import Iterable

import typer
from rich.console import Console

from .audio import process_clip
from .utils import parse_time
from .video import process_video

batch_app = typer.Typer(help="Batch and watch workflows for Clipped.")
console = Console()


def _iter_files(directory: Path, pattern: str, recursive: bool) -> Iterable[Path]:
    if recursive:
        yield from sorted(directory.rglob(pattern))
    else:
        yield from sorted(directory.glob(pattern))


@batch_app.command("audio")
def batch_audio(
    input_dir: Path = typer.Option(..., exists=True, file_okay=False, dir_okay=True, help="Directory containing audio files."),
    pattern: str = typer.Option("*.mp3", help="Glob pattern for audio files."),
    recursive: bool = typer.Option(False, "--recursive", help="Search subdirectories."),
    start: str = typer.Option(..., help="Start time for all clips."),
    end: str = typer.Option(..., help="End time for all clips."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print commands without running."),
) -> None:
    """Batch clip audio files from a directory."""
    start_secs = parse_time(start)
    end_secs = parse_time(end)
    files = list(_iter_files(input_dir, pattern, recursive))
    if not files:
        console.print(f"[yellow]No files found for pattern {pattern} in {input_dir}[/yellow]")
        raise typer.Exit(1)

    for path in files:
        console.print(f"\n[bold]Processing audio:[/bold] {path.name}")
        process_clip(str(path), start_secs, end_secs, dry_run=dry_run)

    console.print("\n[green]Batch audio processing complete.[/green]")


@batch_app.command("video")
def batch_video(
    input_dir: Path = typer.Option(..., exists=True, file_okay=False, dir_okay=True, help="Directory containing audio files."),
    pattern: str = typer.Option("*.mp3", help="Glob pattern for audio files."),
    recursive: bool = typer.Option(False, "--recursive", help="Search subdirectories."),
    template: str = typer.Option("spinner", "--template", "-t", help="Template to use for all files."),
    platform: str = typer.Option("default", help="Platform profile to use."),
    style: str | None = typer.Option(None, "--style", help="Remotion style."),
    motion: str | None = typer.Option(None, "--motion", help="Remotion motion level."),
    waveform: str | None = typer.Option(None, "--waveform", help="Remotion waveform."),
    palette: str | None = typer.Option(None, "--palette", help="Remotion palette."),
    start: str = typer.Option("0", help="Start time for all clips."),
    end: str = typer.Option(None, help="End time for all clips."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print commands without running."),
) -> None:
    """Batch render video for audio files in a directory."""
    start_secs = parse_time(start)
    end_secs = parse_time(end) if end else None
    extra_config = {
        key: value
        for key, value in {
            "style": style,
            "motion": motion,
            "waveform": waveform,
            "palette": palette,
        }.items()
        if value
    } or None
    files = list(_iter_files(input_dir, pattern, recursive))
    if not files:
        console.print(f"[yellow]No files found for pattern {pattern} in {input_dir}[/yellow]")
        raise typer.Exit(1)

    for path in files:
        console.print(f"\n[bold]Processing video:[/bold] {path.name}")
        process_video(
            str(path),
            template_name=template,
            platform_name=platform,
            start=start_secs,
            end=end_secs,
            dry_run=dry_run,
            extra_config=extra_config,
        )

    console.print("\n[green]Batch video processing complete.[/green]")


@batch_app.command("watch")
def watch_directory(
    input_dir: Path = typer.Option(..., exists=True, file_okay=False, dir_okay=True, help="Directory to watch for new audio files."),
    pattern: str = typer.Option("*.mp3", help="Glob pattern for new audio files."),
    recursive: bool = typer.Option(False, "--recursive", help="Search subdirectories."),
    mode: str = typer.Option("video", "--type", help="Processing mode: audio or video."),
    template: str = typer.Option("spinner", help="Template to use for video mode."),
    platform: str = typer.Option("default", help="Platform profile to use for video mode."),
    style: str | None = typer.Option(None, "--style", help="Remotion style."),
    motion: str | None = typer.Option(None, "--motion", help="Remotion motion level."),
    waveform: str | None = typer.Option(None, "--waveform", help="Remotion waveform."),
    palette: str | None = typer.Option(None, "--palette", help="Remotion palette."),
    start: str = typer.Option("0", help="Start time for all clips."),
    end: str = typer.Option(None, help="End time for all clips."),
    interval: float = typer.Option(5.0, help="Polling interval in seconds."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print commands without running."),
) -> None:
    """Watch a directory and process new audio files as they appear."""
    start_secs = parse_time(start)
    end_secs = parse_time(end) if end else None
    extra_config = {
        key: value
        for key, value in {
            "style": style,
            "motion": motion,
            "waveform": waveform,
            "palette": palette,
        }.items()
        if value
    } or None
    seen = set()

    console.print(f"[cyan]Watching {input_dir} for new audio files...[/cyan]")
    try:
        while True:
            files = list(_iter_files(input_dir, pattern, recursive))
            for path in files:
                if path in seen:
                    continue
                seen.add(path)
                console.print(f"\n[bold]New file detected:[/bold] {path.name}")
                if mode == "audio":
                    if end_secs is None:
                        console.print("[red]Audio watch mode requires --end to be provided.[/red]")
                        raise typer.Exit(1)
                    process_clip(str(path), start_secs, end_secs, dry_run=dry_run)
                else:
                    process_video(
                        str(path),
                        template_name=template,
                        platform_name=platform,
                        start=start_secs,
                        end=end_secs,
                        dry_run=dry_run,
                        extra_config=extra_config,
                    )
            time.sleep(interval)
    except KeyboardInterrupt:
        console.print("\n[green]Watch mode stopped.[/green]")
