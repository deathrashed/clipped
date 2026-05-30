"""
Video engine for Clipped.

Thin coordinator: resolves assets → delegates to a VideoTemplate → applies
PlatformProfile (size, duration limit) → runs FFmpeg with a progress bar.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from .config import get_config, validate_output_dirs
from .platforms import PlatformProfile, get_profile
from .progress import run_ffmpeg_with_progress
from .remotion_engine import render_remotion_video, stage_remotion_preview
from .templates import get_template
from .utils import resolve_assets

def get_video_encoder_args(codec: str, crf: int, config: dict) -> list[str]:
    """Return encoder arguments, mapping libx264 to h264_videotoolbox on macOS if enabled."""
    use_vt = config.get("use_videotoolbox", True)
    if sys.platform == "darwin" and codec == "libx264" and use_vt:
        if crf <= 18:
            q_v = 85
        elif crf <= 23:
            q_v = 75
        elif crf <= 28:
            q_v = 60
        else:
            q_v = 50
        return ["-c:v", "h264_videotoolbox", "-q:v", str(q_v)]
    return ["-c:v", codec, "-crf", str(crf)]


def _get_ui():
    from .main import UI
    return UI


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
    output_path: Path | None = None,
    cover: str | None = None,
    logo: str | None = None,
    background: str | None = None,
    media: str | None = None,
    lyrics: str | None = None,
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
    media_list = [media] if media else None
    assets  = resolve_assets(
        src,
        cover_override=cover,
        logo_override=logo,
        background_override=background,
        media=media_list,
        lyrics_override=lyrics,
    )
    config  = get_config()
    is_preview = False
    if extra_config:
        extra_config = dict(extra_config)
        is_preview = extra_config.pop("is_preview_render", False)
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
        _get_ui().warn(
            f"Clip ({calc_dur:.0f}s) exceeds {profile.label} max "
            f"({profile.max_duration:.0f}s). Trimming."
        )
        calc_dur = profile.max_duration

    # ── Discord: audio-only fast path ─────────────────────────────────────────
    if profile.output_format == "mp3":
        return _export_audio_only(
            src,
            assets,
            config,
            profile,
            start,
            calc_dur,
            dry_run,
            output_path,
        )

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
    from .utils import get_output_path
    if output_path:
        output_path = Path(output_path)
    else:
        output_path = get_output_path(
            base_dir=Path(config["video_dir"]),
            artist=assets.artist_name,
            title=assets.track_title,
            fallback_stem=assets.audio_path.stem,
            template=template_name,
            extension="mp4"
        )
    if is_preview:
        output_path = output_path.with_name(f"{output_path.stem} [preview]{output_path.suffix}")

    if getattr(template.info, "engine", "ffmpeg") == "remotion":
        _get_ui().sys(
            f"Generating [bold cyan]{template.info.label}[/bold cyan] "
            f"for [bold magenta]{profile.label}[/bold magenta] with Remotion..."
        )
        result = render_remotion_video(
            assets=assets,
            template=template,
            profile=profile,
            config=config,
            start=start,
            duration=calc_dur,
            output_path=output_path,
            dry_run=dry_run,
            fade_in=fade_in,
            fade_out=fade_out,
        )

        if dry_run:
            return None

        if result:
            _get_ui().info(f"Video saved: [white]{result.name}[/white]")
            
            try:
                from .utils import register_clip_in_showcase
                register_clip_in_showcase(
                    filepath=result,
                    kind="video",
                    template=template_name,
                    platform=platform_name,
                    start=start,
                    end=end or (start + calc_dur),
                    artist=assets.artist_name,
                    title=assets.track_title
                )
            except Exception:
                pass

            if config.get("copy_to_clipboard", True):
                subprocess.run(
                    ["osascript", "-e", f'set the clipboard to (POSIX file "{result}")']
                )
                _get_ui().sys("Copied to clipboard.")

            subprocess.run(
                ["osascript", "-e", f'display notification "{result.name}" with title "Clipped"'],
                capture_output=True,
            )
        return result

    # ── Build FFmpeg command ──────────────────────────────────────────────────
    inputs         = template.get_inputs(assets)
    filter_graph   = template.get_filter_graph(assets, calc_dur)

    # Stream labels
    video_map = "[v]"
    audio_map = "0:a"

    # If platform needs a different size, append a scale step
    if scale_out and scale_out != template.get_output_size():
        filter_graph += f";[v]scale={scale_out[0]}:{scale_out[1]}[vout]"
        video_map = "[vout]"

    cmd = ["ffmpeg", "-y"]

    # Input 0: audio (seeked)
    if start:
        cmd += ["-ss", str(start)]
    cmd += ["-i", inputs[0]]

    # Remaining inputs (images): looped
    for img in inputs[1:]:
        cmd += ["-loop", "1", "-i", img]

    # Audio fades
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
    encoder_args = get_video_encoder_args(profile.video_codec, profile.crf, config)
    cmd += encoder_args + ["-pix_fmt", "yuv420p"]
    cmd += ["-t", str(calc_dur)]
    cmd += ["-c:a", profile.audio_codec, "-b:a", profile.audio_bitrate]
    cmd.append(str(output_path))

    # ── Run ───────────────────────────────────────────────────────────────────
    _get_ui().sys(
        f"Generating [bold cyan]{template.info.label}[/bold cyan] "
        f"for [bold magenta]{profile.label}[/bold magenta]…"
    )

    try:
        run_ffmpeg_with_progress(
            cmd,
            duration_secs=calc_dur,
            label=f"{template.info.label} → {profile.label}",
            dry_run=dry_run,
        )

        if dry_run:
            return None

        _get_ui().info(f"Video saved: [white]{output_path.name}[/white]")

        try:
            from .utils import register_clip_in_showcase
            register_clip_in_showcase(
                filepath=output_path,
                kind="video",
                template=template_name,
                platform=platform_name,
                start=start,
                end=end or (start + calc_dur),
                artist=assets.artist_name,
                title=assets.track_title
            )
        except Exception:
            pass

        if config.get("copy_to_clipboard", True):
            subprocess.run(
                ["osascript", "-e", f'set the clipboard to (POSIX file "{output_path}")']
            )
            _get_ui().sys("Copied to clipboard.")

        subprocess.run(
            ["osascript", "-e", f'display notification "{output_path.name}" with title "Clipped"'],
            capture_output=True,
        )

        return output_path
    finally:
        template.cleanup()


def _export_audio_only(
    src: str,
    assets,
    config: dict,
    profile: PlatformProfile,
    start: float,
    duration: float,
    dry_run: bool,
    output_path: Path | None = None,
) -> Path | None:
    """Fast-path for audio-only platforms (Discord)."""
    audio_dir  = Path(config["audio_dir"]).expanduser()
    audio_dir.mkdir(parents=True, exist_ok=True)
    output_path = Path(output_path) if output_path else audio_dir / f"{assets.audio_path.stem}_{profile.name}.mp3"

    cmd = ["ffmpeg", "-y"]
    if start:
        cmd += ["-ss", str(start)]
    cmd += ["-i", src, "-t", str(duration), "-c:a", "libmp3lame", "-q:a", "4"]
    cmd.append(str(output_path))

    _get_ui().sys(f"Exporting audio for [bold magenta]{profile.label}[/bold magenta]…")
    run_ffmpeg_with_progress(cmd, duration_secs=duration, label=profile.label, dry_run=dry_run)

    if dry_run:
        return None

    size_mb = output_path.stat().st_size / (1024 * 1024)
    if profile.max_size_mb and size_mb > profile.max_size_mb:
        _get_ui().warn(
            f"File is {size_mb:.1f} MB — exceeds {profile.max_size_mb} MB "
            f"Discord limit. Consider a shorter clip."
        )

    _get_ui().info(f"Audio saved: [white]{output_path.name}[/white]")
    
    try:
        from .utils import register_clip_in_showcase
        register_clip_in_showcase(
            filepath=output_path,
            kind="audio",
            template="audio_only",
            platform=profile.name,
            start=start,
            end=start + duration,
            artist=assets.artist_name,
            title=assets.track_title
        )
    except Exception:
        pass

    if config.get("copy_to_clipboard", True):
        subprocess.run(
            ["osascript", "-e", f'set the clipboard to (POSIX file "{output_path}")']
        )
        _get_ui().sys("Copied to clipboard.")

    subprocess.run(
        ["osascript", "-e", f'display notification "{output_path.name}" with title "Clipped"'],
        capture_output=True,
    )

    return output_path


def run_preview(
    src: str,
    template_name: str = "spinner",
    platform_name: str = "default",
    start: float = 0,
    end: float | None = None,
    duration: float | None = None,
    port: int = 3000,
    cover: str | None = None,
    logo: str | None = None,
    background: str | None = None,
    media: str | None = None,
    lyrics: str | None = None,
) -> None:
    """Stage a preview and either open the Remotion Studio or render/open a short FFmpeg clip."""
    media_list = [media] if media else None
    assets = resolve_assets(
        src,
        cover_override=cover,
        logo_override=logo,
        background_override=background,
        media=media_list,
        lyrics_override=lyrics,
    )
    config = get_config()
    profile = get_profile(platform_name)
    template = get_template(template_name, config=config)

    # Resolve preview duration (default to 3 seconds if not specified)
    preview_dur = duration if duration is not None else float(config.get("preview_duration", 3.0))
    if end is not None:
        calc_dur = end - start
    else:
        calc_dur = preview_dur

    if getattr(template.info, "engine", "ffmpeg") == "remotion":
        _get_ui().sys(f"Staging preview assets for [bold cyan]{template.info.label}[/bold cyan]...")
        
        # Override default-props.json and copy files to public/jobs/preview
        stage_remotion_preview(
            assets=assets,
            template=template,
            profile=profile,
            config=config,
            start=start,
            duration=calc_dur,
            fade_in=config.get("fade_duration", 0.5),
            fade_out=config.get("fade_duration", 0.5),
        )
        
        # Start the Remotion studio
        _get_ui().sys(f"Launching Remotion Studio on port {port}...")
        from .remotion_engine import REMOTION_DIR
        cmd = ["npx", "--no-install", "remotion", "studio", "src/index.ts", "--port", str(port)]
        try:
            subprocess.call(cmd, cwd=REMOTION_DIR)
        except KeyboardInterrupt:
            _get_ui().sys("Studio preview stopped.")
    else:
        # For FFmpeg templates, render a short clip and open it
        _get_ui().warn("Remotion Studio only supports Remotion templates. Rendering a short FFmpeg preview clip...")
        
        out_dir = Path("~/Music/clipped/_previews").expanduser()
        out_dir.mkdir(parents=True, exist_ok=True)
        out_ext = profile.output_format if profile else "mp4"
        out_path = out_dir / f"{assets.audio_path.stem} ({template_name}) [preview].{out_ext}"

        result = process_video(
            src=src,
            template_name=template_name,
            platform_name=platform_name,
            start=start,
            end=start + calc_dur,
            dry_run=False,
            extra_config={"is_preview_render": True},
            output_path=out_path,
            cover=cover,
            logo=logo,
            background=background,
            media=media,
            lyrics=lyrics,
        )
        
        if result and result.exists():
            _get_ui().info(f"Opening preview video: {result.name}")
            subprocess.run(["open", str(result)])
