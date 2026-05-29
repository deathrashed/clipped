"""
FFmpeg progress bar for Clipped.

Wraps a subprocess.Popen call with a Rich Progress bar that reads
FFmpeg's '-progress pipe:1' output to display real-time encoding progress.

Usage:
    from .progress import run_ffmpeg_with_progress

    run_ffmpeg_with_progress(cmd, duration_secs=30.0, label="Generating spinner video")
"""
from __future__ import annotations

import subprocess
import sys

from rich.console import Console
from rich.markup import escape
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

console = Console()


def _notify(title: str, message: str) -> None:
    subprocess.run(
        ["osascript", "-e", f'display notification "{message}" with title "{title}"'],
        capture_output=True,
    )


def run_ffmpeg_with_progress(
    cmd: list[str],
    duration_secs: float,
    label: str = "Encoding",
    dry_run: bool = False,
) -> None:
    """
    Run an FFmpeg command and show a Rich progress bar.

    The command must NOT already contain '-progress'. This function injects
    '-progress pipe:1 -nostats' before the output path.

    Raises subprocess.CalledProcessError on non-zero exit.
    """
    if dry_run:
        console.print("\n[bold cyan]── Dry Run: FFmpeg Command ──[/bold cyan]")
        command = " ".join(f'"{a}"' if " " in a else a for a in cmd)
        console.print(escape(command))
        console.print("[bold cyan]────────────────────────────[/bold cyan]\n")
        return

    # Inject progress reporting before the final output path
    output_path = cmd[-1]
    base_cmd = cmd[:-1]
    full_cmd = base_cmd + ["-progress", "pipe:1", "-nostats", output_path]

    duration_ms = int(duration_secs * 1_000_000)  # microseconds for FFmpeg

    import time
    t_start = time.monotonic()

    with Progress(
        SpinnerColumn(),
        TextColumn(f"[bold cyan]{label}"),
        BarColumn(bar_width=40),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        console=console,
        transient=False,   # keep bar visible after completion
    ) as progress:
        task = progress.add_task(label, total=duration_ms)

        proc = subprocess.Popen(
            full_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        output_lines: list[str] = []

        try:
            for line in proc.stdout:  # type: ignore[union-attr]
                line = line.strip()
                if line.startswith("out_time_us="):
                    try:
                        us = int(line.split("=", 1)[1])
                        progress.update(task, completed=min(us, duration_ms))
                    except ValueError:
                        pass
                elif line.startswith("progress=end"):
                    progress.update(task, completed=duration_ms)
                elif line:
                    output_lines.append(line)
            proc.wait()
        except KeyboardInterrupt:
            proc.kill()
            proc.wait()
            raise

        if proc.returncode != 0:
            console.print(f"\n[bold red]FFmpeg Error (exit {proc.returncode}):[/bold red]")
            for ln in output_lines[-20:]:
                console.print(f"  [dim]{ln}[/dim]")
            sys.exit(1)

    elapsed = time.monotonic() - t_start
    console.print(f"[dim]  encode: {elapsed:.1f}s[/dim]")
    _notify("Clipped", "FFmpeg encoding complete")
