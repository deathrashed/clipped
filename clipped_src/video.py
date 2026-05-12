"""
Video engine for Clipped.

Thin coordinator: resolves assets → delegates to a VideoTemplate → applies
PlatformProfile (size, duration limit) → runs FFmpeg with a progress bar →
records to the clip library.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from rich.console import Console

from .config import get_config, validate_output_dirs
from .library import Library, ClipEntry
from .platforms import PlatformProfile, get_profile
from .progress import run_ffmpeg_with_progress
from .templates import get_template
from .utils import resolve_assets

console = Console()


def process_video(
    src: str,
    template_name: str = "spinner",
    platform_name: str = "default",
    start: float = 0,
    end: float | None = None,
    sequence: list | None = None,
    dry_run: bool = False,
    extra_config: dict | None = None,
    fade_in: float | None = None,
    fade_out: float | None = None,
) -> Path | None:
    """
    Generate a video from an audio file.

    Args:
        src           : Path to the audio file.
        template_name : Key in the template registry (e.g. "spinner", "vertical").
        platform_name : Key in the platform registry (e.g. "instagram", "discord").
        start         : Start offset in seconds.
        end           : End offset in seconds (None = full file).
        sequence      : Optional [(path, duration)] for FadeTemplate.
        dry_run       : Print the FFmpeg command but don't run it.
        extra_config  : Optional config overrides merged into the base config
                        (e.g. {"waveform_mode": "p2p", "waveform_color": "0xFF0000"}).
    """
    assets  = resolve_assets(src)
    config  = get_config()
    if extra_config:
        config = {**config, **extra_config}
    profile = get_profile(platform_name)

    validate_output_dirs(config)

    # ── Duration ──────────────────────────────────────────────────────────────
    if end is not None and start is not None:
        calc_dur = end - start
    else:
        try:
            probe = [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(assets.audio_path),
            ]
            calc_dur = float(
                subprocess.run(probe, capture_output=True, text=True).stdout.strip()
            )
            if start:
                calc_dur -= start
        except Exception:
            calc_dur = 30.0

    # Clamp to platform max duration
    if profile.max_duration and calc_dur > profile.max_duration:
        console.print(
            f"[yellow]⚠  Clip ({calc_dur:.0f}s) exceeds {profile.label} max "
            f"({profile.max_duration:.0f}s). Trimming.[/yellow]"
        )
        calc_dur = profile.max_duration

    # ── Discord: audio-only fast path ─────────────────────────────────────────
    if profile.output_format == "mp3":
        return _export_audio_only(src, assets, config, profile, start, calc_dur, dry_run)

    # ── Template instantiation ────────────────────────────────────────────────
    extra_kwargs: dict = {}
    if template_name == "fade" and sequence:
        extra_kwargs["sequence"] = sequence

    template = get_template(template_name, config=config, **extra_kwargs)
    w, h = template.get_output_size()

    # ── Override dimensions from platform profile if set ──────────────────────
    if profile.width and profile.height:
        # The template may have a different native size — let the platform win
        # by injecting a scale step. We do this via a post-filter in the command
        # rather than modifying the template.
        scale_out = (profile.width, profile.height)
    else:
        scale_out = None

    # ── Output path ───────────────────────────────────────────────────────────
    video_dir = Path(config["video_dir"]).expanduser()
    video_dir.mkdir(parents=True, exist_ok=True)
    output_path = video_dir / f"{assets.audio_path.stem}_{template_name}_{platform_name}.mp4"

    # ── Build FFmpeg command ──────────────────────────────────────────────────
    inputs         = template.get_inputs(assets)
    filter_graph   = template.get_filter_graph(assets, calc_dur)

    # If platform needs a different size, append a scale step
    if scale_out and scale_out != template.get_output_size():
        filter_graph += f";[v]scale={scale_out[0]}:{scale_out[1]}[vout]"
        video_map = "[vout]"
    else:
        video_map = "[v]"

    cmd = ["ffmpeg", "-y"]

    # Input 0: audio (seeked)
    if start:
        cmd += ["-ss", str(start)]
    cmd += ["-i", inputs[0]]

    # Remaining inputs (images): looped
    for img in inputs[1:]:
        cmd += ["-loop", "1", "-i", img]

    # Audio fades
    audio_map = "0:a"
    fi = fade_in
    fo = fade_out
    if fi is None and fo is None and config.get("auto_fade", True):
        fd = config.get("fade_duration", 0.5)
        fi = fo = fd

    afiles = []
    if fi and fi > 0: afiles.append(f"afade=t=in:st=0:d={fi}")
    if fo and fo > 0: afiles.append(f"afade=t=out:st={max(0, calc_dur - fo)}:d={fo}")

    if afiles:
        filter_graph += f";[0:a]{','.join(afiles)}[aout]"
        audio_map = "[aout]"

    cmd += ["-filter_complex", filter_graph]
    cmd += ["-map", video_map, "-map", audio_map]
    cmd += ["-c:v", profile.video_codec, "-pix_fmt", "yuv420p", "-crf", str(profile.crf)]
    cmd += ["-t", str(calc_dur)]
    cmd += ["-c:a", profile.audio_codec, "-b:a", profile.audio_bitrate]
    cmd.append(str(output_path))

    # ── Run ───────────────────────────────────────────────────────────────────
    console.print(
        f"🎬 [bold]Generating [cyan]{template.info.label}[/cyan] "
        f"for [magenta]{profile.label}[/magenta]…[/bold]"
    )

    run_ffmpeg_with_progress(
        cmd,
        duration_secs=calc_dur,
        label=f"{template.info.label} → {profile.label}",
        dry_run=dry_run,
    )

    if dry_run:
        return None

    console.print(f"✅ [green]Video saved:[/green] {output_path}")

    # Clipboard copy
    if config.get("copy_to_clipboard", True):
        subprocess.run(
            ["osascript", "-e", f'set the clipboard to (POSIX file "{output_path}")']
        )
        console.print("[dim]📋 Copied to clipboard.[/dim]")

    # Library record
    lib = Library()
    lib.record(ClipEntry(
        source=src,
        start=start,
        end=start + calc_dur,
        output_video=str(output_path),
        artist=assets.artist_name,
        album=assets.album_name,
        title=assets.track_title,
        platform=platform_name,
        template=template_name,
    ))

    return output_path


def _export_audio_only(
    src: str,
    assets,
    config: dict,
    profile: PlatformProfile,
    start: float,
    duration: float,
    dry_run: bool,
) -> Path | None:
    """Fast-path for audio-only platforms (Discord)."""
    audio_dir  = Path(config["audio_dir"]).expanduser()
    audio_dir.mkdir(parents=True, exist_ok=True)
    output_path = audio_dir / f"{assets.audio_path.stem}_{profile.name}.mp3"

    cmd = ["ffmpeg", "-y"]
    if start:
        cmd += ["-ss", str(start)]
    cmd += ["-i", src, "-t", str(duration), "-c:a", "libmp3lame", "-q:a", "4"]
    cmd.append(str(output_path))

    console.print(f"🎵 [bold]Exporting audio for [magenta]{profile.label}[/magenta]…[/bold]")
    run_ffmpeg_with_progress(cmd, duration_secs=duration, label=profile.label, dry_run=dry_run)

    if dry_run:
        return None

    # Size check
    size_mb = output_path.stat().st_size / (1024 * 1024)
    if profile.max_size_mb and size_mb > profile.max_size_mb:
        console.print(
            f"[yellow]⚠  File is {size_mb:.1f} MB — exceeds {profile.max_size_mb} MB "
            f"Discord limit. Consider a shorter clip.[/yellow]"
        )

    console.print(f"✅ [green]Audio saved:[/green] {output_path}")
    if config.get("copy_to_clipboard", True):
        subprocess.run(
            ["osascript", "-e", f'set the clipboard to (POSIX file "{output_path}")']
        )
        console.print("[dim]📋 Copied to clipboard.[/dim]")

    return output_path
