from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.markup import escape
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from .platforms import PlatformProfile

console = Console()


REPO_ROOT = Path(__file__).resolve().parents[1]
REMOTION_DIR = REPO_ROOT / "remotion"
REMOTION_PUBLIC_DIR = REMOTION_DIR / "public"
REMOTION_JOBS_DIR = REMOTION_PUBLIC_DIR / "jobs"
REMOTION_ENTRYPOINT = "src/index.ts"


@dataclass
class RemotionRenderResult:
    output_path: Path
    job_dir: Path
    props_path: Path


def _shell_quote(args: list[str]) -> str:
    return " ".join(f'"{arg}"' if " " in arg else arg for arg in args)


def _copy_asset(src: Path | None, job_dir: Path, name: str) -> str | None:
    if not src:
        return None
    src = Path(src).expanduser()
    if not src.exists():
        return None
    suffix = src.suffix.lower() or ".bin"
    dest = job_dir / f"{name}{suffix}"
    shutil.copyfile(src, dest)
    return f"jobs/{job_dir.name}/{dest.name}"


def _clean_logo(src: Path | None, job_dir: Path, config: dict) -> Path | None:
    if not src:
        return None
    src = Path(src).expanduser()
    if not src.exists():
        return None
        
    clean_logos = config.get("clean_logo", config.get("remotion_clean_logos", True))
    if str(clean_logos).lower() in ("false", "0", "no"):
        return src
        
    try:
        from PIL import Image
        with Image.open(src) as img:
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                return src
    except Exception:
        pass
        
    rmbg_path = config.get("rmbg_path", "/Users/rd/Scripts/Riley/rmbg/bin/rmbg")
    rmbg = Path(rmbg_path).expanduser()
    if not rmbg.exists():
        return src
        
    dest = job_dir / f"logo_cleaned.png"
    fuzz = config.get("logo_fuzz", config.get("remotion_logo_fuzz", 15))
    bg = config.get("logo_bg", config.get("remotion_logo_bg", "auto"))
    
    cmd = [str(rmbg), "-i", str(src), "-o", str(dest), "--fuzz", str(fuzz)]
    if bg and str(bg) != "auto":
        cmd += ["--color", str(bg)]
        
    try:
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0 and dest.exists():
            return dest
    except Exception:
        pass
        
    return src


def _copy_extra_assets(paths: list[Path], job_dir: Path, prefix: str = "extra") -> list[str]:
    copied: list[str] = []
    seen: set[Path] = set()
    for idx, path in enumerate(paths):
        path = Path(path).expanduser()
        if not path.exists() or path in seen:
            continue
        seen.add(path)
        suffix = path.suffix.lower() or ".bin"
        dest = job_dir / f"{prefix}-{idx}{suffix}"
        shutil.copyfile(path, dest)
        copied.append(f"jobs/{job_dir.name}/{dest.name}")
    return copied


def _build_audio_filter(config: dict, duration: float, fade_in: float | None, fade_out: float | None) -> str | None:
    fi = fade_in
    fo = fade_out
    if fi is None and fo is None and config.get("auto_fade", True):
        fd = float(config.get("fade_duration", 0.5))
        fi = fo = fd

    filters: list[str] = []
    if fi and fi > 0:
        filters.append(f"afade=t=in:st=0:d={fi}")
    if fo and fo > 0:
        filters.append(f"afade=t=out:st={max(0, duration - fo)}:d={fo}")
    return ",".join(filters) if filters else None


def _prepare_audio(
    src: Path,
    job_dir: Path,
    start: float,
    duration: float,
    config: dict,
    fade_in: float | None,
    fade_out: float | None,
    dry_run: bool,
) -> str | None:
    dest = job_dir / "audio.wav"
    cmd = ["ffmpeg", "-y"]
    if start:
        cmd += ["-ss", str(start)]
    cmd += ["-i", str(src), "-t", str(duration)]

    afilter = _build_audio_filter(config, duration, fade_in, fade_out)
    if afilter:
        cmd += ["-af", afilter]
    cmd += ["-ar", "48000", "-ac", "2", str(dest)]

    if dry_run:
        console.print("\n[bold cyan]-- Dry Run: Remotion Audio Prep --[/bold cyan]")
        console.print(escape(_shell_quote(cmd)))
        return f"jobs/{job_dir.name}/{dest.name}"

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        detail = res.stderr.strip() or res.stdout.strip()
        raise RuntimeError(f"Remotion audio prep failed: {detail}")
    return f"jobs/{job_dir.name}/{dest.name}"


def _remotion_command(
    composition_id: str,
    props_path: Path,
    output_path: Path,
    width: int,
    height: int,
    fps: int,
    duration_frames: int,
    profile: PlatformProfile,
) -> list[str]:
    cmd = [
        "npx",
        "--no-install",
        "remotion",
        "render",
        REMOTION_ENTRYPOINT,
        composition_id,
        str(output_path),
        "--props",
        str(props_path),
        "--width",
        str(width),
        "--height",
        str(height),
        "--fps",
        str(fps),
        "--duration",
        str(duration_frames),
        "--codec",
        "h264",
        "--audio-codec",
        profile.audio_codec,
        "--audio-bitrate",
        profile.audio_bitrate,
        "--crf",
        str(profile.crf),
        "--pixel-format",
        "yuv420p",
        "--overwrite",
    ]
    return cmd


def _run_remotion(cmd: list[str], label: str, dry_run: bool) -> None:
    if dry_run:
        console.print("\n[bold cyan]-- Dry Run: Remotion Command --[/bold cyan]")
        console.print(escape(_shell_quote(cmd)))
        console.print("[bold cyan]--------------------------------[/bold cyan]\n")
        return

    if not (REMOTION_DIR / "node_modules" / "remotion").exists():
        raise RuntimeError("Remotion dependencies are not installed. Run: cd remotion && npm install")

    output_lines: list[str] = []
    with Progress(
        SpinnerColumn(),
        TextColumn(f"[bold cyan]{label}"),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    ) as progress:
        progress.add_task(label, total=None)
        proc = subprocess.Popen(
            cmd,
            cwd=REMOTION_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        try:
            for line in proc.stdout:  # type: ignore[union-attr]
                stripped = line.strip()
                if stripped:
                    output_lines.append(stripped)
            proc.wait()
        except KeyboardInterrupt:
            proc.kill()
            proc.wait()
            raise

    if proc.returncode != 0:
        console.print(f"\n[bold red]Remotion Error (exit {proc.returncode}):[/bold red]")
        for line in output_lines[-30:]:
            console.print(f"  [dim]{line}[/dim]")
        raise RuntimeError("Remotion render failed")


def render_remotion_video(
    *,
    assets,
    template,
    profile: PlatformProfile,
    config: dict,
    start: float,
    duration: float,
    output_path: Path,
    dry_run: bool,
    fade_in: float | None,
    fade_out: float | None,
) -> Path | None:
    info = template.info
    if not info.composition_id:
        raise RuntimeError(f"Remotion template '{info.name}' is missing composition_id")

    if not (REMOTION_DIR / "package.json").exists():
        raise RuntimeError(f"Remotion app is missing at {REMOTION_DIR}")

    output_path = Path(output_path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fps = int(config.get("remotion_fps", 30) or 30)
    width = int(profile.width or info.aspect[0])
    height = int(profile.height or info.aspect[1])
    duration_frames = max(1, int(round(duration * fps)))

    job_id = f"{int(time.time())}-{uuid.uuid4().hex[:10]}"
    job_dir = REMOTION_JOBS_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    try:
        audio_src = _prepare_audio(
            assets.audio_path,
            job_dir,
            start,
            duration,
            config,
            fade_in,
            fade_out,
            dry_run,
        )
        cover_src = _copy_asset(assets.cover, job_dir, "cover")
        
        logo_path = _clean_logo(assets.logo, job_dir, config)
        logo_src = _copy_asset(logo_path, job_dir, "logo")
        
        artist_src = _copy_asset(assets.artist, job_dir, "artist")
        background_src = _copy_asset(getattr(assets, "background", None), job_dir, "background")
        lyrics_src = _copy_asset(getattr(assets, "lyrics", None), job_dir, "lyrics")

        # Embedded lyrics JSON (from audio metadata) takes precedence if no lyrics file
        lyrics_json = getattr(assets, "lyrics_json", None)
        
        extra_srcs = _copy_extra_assets(list(getattr(assets, "all_images", [])), job_dir, "extra")
        media_srcs = _copy_extra_assets(list(getattr(assets, "media", [])), job_dir, "media")

        defaults = dict(getattr(info, "defaults", {}) or {})
        options = {
            "style": config.get("style") or config.get("remotion_style") or defaults.get("style", "classic"),
            "motion": config.get("motion") or config.get("remotion_motion") or defaults.get("motion", "medium"),
            "waveform": config.get("waveform") or config.get("remotion_waveform") or defaults.get("waveform", "none"),
            "palette": config.get("palette") or config.get("remotion_palette") or defaults.get("palette", "auto"),
            "scene_pack": config.get("scene_pack") or config.get("remotion_scene_pack") or defaults.get("scene_pack", "art_focus"),
            "effects": config.get("effects") or config.get("remotion_effects") or defaults.get("effects", "texture"),
            "captions": config.get("captions") or config.get("remotion_captions") or defaults.get("captions", "off"),
            "mediaMode": config.get("media_mode") or defaults.get("mediaMode", "background"),
            "cleanLogo": config.get("clean_logo", config.get("remotion_clean_logos", True)),
            "logoBg": config.get("logo_bg") or config.get("remotion_logo_bg") or "auto",
            "logoFuzz": config.get("logo_fuzz") or config.get("remotion_logo_fuzz") or 15,
            "seed": str(config.get("seed") or defaults.get("seed", "")),
        }

        props = {
            "version": 1,
            "templateId": info.name,
            "compositionId": info.composition_id,
            "platformName": profile.name,
            "width": width,
            "height": height,
            "fps": fps,
            "durationSeconds": duration,
            "durationFrames": duration_frames,
            "assets": {
                "audioSrc": audio_src,
                "coverSrc": cover_src,
                "logoSrc": logo_src,
                "artistImageSrc": artist_src,
                "backgroundSrc": background_src,
                "lyrics": lyrics_src,
                "lyricsJson": lyrics_json,
                "extraImageSrcs": extra_srcs,
                "mediaSrcs": media_srcs,
            },
            "metadata": {
                "artist": assets.artist_name,
                "title": assets.track_title,
                "album": assets.album_name,
                "trackNumber": assets.track_number,
                "year": assets.year,
                "genre": assets.genre,
                "sourceFilename": assets.audio_path.name,
            },
            "audio": {
                "fadeIn": fade_in,
                "fadeOut": fade_out,
                "volume": 1,
                "originalStart": start,
                "preparedDuration": duration,
            },
            "options": options,
            "encoding": {
                "codec": profile.video_codec,
                "crf": profile.crf,
                "audioCodec": profile.audio_codec,
                "audioBitrate": profile.audio_bitrate,
                "pixelFormat": "yuv420p",
            },
        }

        props_path = job_dir / "props.json"
        props_path.write_text(json.dumps(props, indent=2), encoding="utf-8")

        cmd = _remotion_command(
            info.composition_id,
            props_path,
            output_path,
            width,
            height,
            fps,
            duration_frames,
            profile,
        )
        _run_remotion(cmd, f"{info.label} -> {profile.label}", dry_run)

        if dry_run:
            return None
        return output_path
    finally:
        keep_jobs = os.environ.get("CLIPPED_KEEP_REMOTION_JOBS", "").lower() in {"1", "true", "yes"}
        if not keep_jobs and (dry_run or output_path.exists()):
            shutil.rmtree(job_dir, ignore_errors=True)


def stage_remotion_preview(
    *,
    assets,
    template,
    profile: PlatformProfile,
    config: dict,
    start: float,
    duration: float,
    fade_in: float | None,
    fade_out: float | None,
) -> Path:
    """
    Stage all assets into the stable preview directory remotion/public/jobs/preview/
    and overwrite remotion/src/default-props.json.
    Returns the path to default-props.json.
    """
    info = template.info
    if not info.composition_id:
        raise RuntimeError(f"Remotion template '{info.name}' is missing composition_id")

    if not (REMOTION_DIR / "package.json").exists():
        raise RuntimeError(f"Remotion app is missing at {REMOTION_DIR}")

    fps = int(config.get("remotion_fps", 30) or 30)
    width = int(profile.width or info.aspect[0])
    height = int(profile.height or info.aspect[1])
    duration_frames = max(1, int(round(duration * fps)))

    # Use a stable directory for previewing
    job_dir = REMOTION_JOBS_DIR / "preview"
    if job_dir.exists():
        shutil.rmtree(job_dir, ignore_errors=True)
    job_dir.mkdir(parents=True, exist_ok=True)

    audio_src = _prepare_audio(
        assets.audio_path,
        job_dir,
        start,
        duration,
        config,
        fade_in,
        fade_out,
        dry_run=False,
    )
    cover_src = _copy_asset(assets.cover, job_dir, "cover")
    
    logo_path = _clean_logo(assets.logo, job_dir, config)
    logo_src = _copy_asset(logo_path, job_dir, "logo")
    
    artist_src = _copy_asset(assets.artist, job_dir, "artist")
    background_src = _copy_asset(getattr(assets, "background", None), job_dir, "background")
    lyrics_src = _copy_asset(getattr(assets, "lyrics", None), job_dir, "lyrics")
    lyrics_json = getattr(assets, "lyrics_json", None)
    
    extra_srcs = _copy_extra_assets(list(getattr(assets, "all_images", [])), job_dir, "extra")
    media_srcs = _copy_extra_assets(list(getattr(assets, "media", [])), job_dir, "media")

    defaults = dict(getattr(info, "defaults", {}) or {})
    options = {
        "style": config.get("style") or config.get("remotion_style") or defaults.get("style", "classic"),
        "motion": config.get("motion") or config.get("remotion_motion") or defaults.get("motion", "medium"),
        "waveform": config.get("waveform") or config.get("remotion_waveform") or defaults.get("waveform", "none"),
        "palette": config.get("palette") or config.get("remotion_palette") or defaults.get("palette", "auto"),
        "scene_pack": config.get("scene_pack") or config.get("remotion_scene_pack") or defaults.get("scene_pack", "art_focus"),
        "effects": config.get("effects") or config.get("remotion_effects") or defaults.get("effects", "texture"),
        "captions": config.get("captions") or config.get("remotion_captions") or defaults.get("captions", "off"),
        "mediaMode": config.get("media_mode") or defaults.get("mediaMode", "background"),
        "cleanLogo": config.get("clean_logo", config.get("remotion_clean_logos", True)),
        "logoBg": config.get("logo_bg") or config.get("remotion_logo_bg") or "auto",
        "logoFuzz": config.get("logo_fuzz") or config.get("remotion_logo_fuzz") or 15,
        "seed": str(config.get("seed") or defaults.get("seed", "")),
    }

    props = {
        "version": 1,
        "templateId": info.name,
        "compositionId": info.composition_id,
        "platformName": profile.name,
        "width": width,
        "height": height,
        "fps": fps,
        "durationSeconds": duration,
        "durationFrames": duration_frames,
        "assets": {
            "audioSrc": audio_src,
            "coverSrc": cover_src,
            "logoSrc": logo_src,
            "artistImageSrc": artist_src,
            "backgroundSrc": background_src,
            "lyrics": lyrics_src,
            "lyricsJson": lyrics_json,
            "extraImageSrcs": extra_srcs,
            "mediaSrcs": media_srcs,
        },
        "metadata": {
            "artist": assets.artist_name,
            "title": assets.track_title,
            "album": assets.album_name,
            "trackNumber": assets.track_number,
            "year": assets.year,
            "genre": assets.genre,
            "sourceFilename": assets.audio_path.name,
        },
        "audio": {
            "fadeIn": fade_in,
            "fadeOut": fade_out,
            "volume": 1,
            "originalStart": start,
            "preparedDuration": duration,
        },
        "options": options,
        "encoding": {
            "codec": profile.video_codec,
            "crf": profile.crf,
            "audioCodec": profile.audio_codec,
            "audioBitrate": profile.audio_bitrate,
            "pixelFormat": "yuv420p",
        },
    }

    default_props_path = REMOTION_DIR / "src" / "default-props.json"
    default_props_path.write_text(json.dumps(props, indent=2), encoding="utf-8")
    return default_props_path
