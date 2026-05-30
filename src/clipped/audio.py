"""
Audio engine for Clipped.

Handles:
- Clipping local files and YouTube URLs
- Interactive preview / adjust-offset loop
- Clipboard copy
- Keyboard Maestro / Swinsian hotkey integration (mark_start / mark_end)
"""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from rich.console import Console

from .config import get_config, HISTORY_FILE, validate_output_dirs
from .utils import resolve_assets

def _get_ui():
    from .main import UI
    return UI


def _swinsian_current_track() -> str | None:
    """Get the current track path from Swinsian. Returns None on failure."""
    try:
        res = subprocess.run(
            ["osascript", "-e",
             'tell application "Swinsian" to POSIX path of (get location of current track)'],
            capture_output=True, text=True, timeout=5,
        )
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    except (subprocess.TimeoutExpired, OSError):
        pass
    return None


def _notify(title: str, message: str) -> None:
    subprocess.run(
        ["osascript", "-e", f'display notification "{message}" with title "{title}"'],
        capture_output=True,
    )

# Maximum clip duration before showing a sanity warning
def format_time_for_filename(seconds: float) -> str:
    mins = int(seconds) // 60
    secs = int(seconds) % 60
    ms = int(round((seconds - int(seconds)) * 100))
    if ms > 0:
        return f"{mins}.{secs:02d}.{ms:02d}"
    return f"{mins}.{secs:02d}"


_DURATION_WARN_SECS = 120.0


class AudioClipper:
    def __init__(
        self,
        src: str,
        start: float,
        end: float,
        fade_in: float | None = None,
        fade_out: float | None = None,
        output_path: Path | None = None,
    ):
        self.src       = src
        self.start     = start
        self.end       = end
        self.duration  = end - start
        if self.duration <= 0:
            raise ValueError(f"End time ({end}s) must be greater than start time ({start}s)")
        self.config    = get_config()
        self.temp_dir  = Path(tempfile.mkdtemp())
        self._input_src: str = src
        self._custom_output = output_path
        self._fade_in  = fade_in
        self._fade_out = fade_out

        validate_output_dirs(self.config)

    # ── Output path ───────────────────────────────────────────────────────────

    def _get_output_path(self, artist: str = "", title: str = "") -> Path:
        base_dir = Path(self.config["audio_dir"])
        if self._custom_output:
            if self._custom_output.is_dir() or not self._custom_output.suffix:
                base_dir = self._custom_output
                base_dir.mkdir(parents=True, exist_ok=True)
            else:
                return self._custom_output

        # Format time suffix: e.g. " (2.41 - 3.06)"
        start_fmt = format_time_for_filename(self.start)
        end_fmt = format_time_for_filename(self.end)
        suffix = f" ({start_fmt} - {end_fmt})"

        adjusted_title = f"{title}{suffix}" if title else ""
        adjusted_stem = f"{Path(self.src).stem}{suffix}"

        from .utils import get_output_path
        return get_output_path(
            base_dir=base_dir,
            artist=artist,
            title=adjusted_title,
            fallback_stem=adjusted_stem,
            extension="mp3"
        )

    # ── Sanity checks ─────────────────────────────────────────────────────────

    def _check_duration(self) -> None:
        if self.duration > _DURATION_WARN_SECS:
            _get_ui().warn(
                f"Long clip ({self.duration:.0f}s) — "
                f"did you enter minutes instead of seconds? "
                f"(e.g. start={self.start:.0f}, end={self.end:.0f})"
            )

    # ── Public entry point ────────────────────────────────────────────────────

    def run(self, is_url: bool = False) -> Path:
        self._check_duration()
        if is_url:
            return self._handle_url()
        return self._handle_file()

    # ── URL / file handlers ───────────────────────────────────────────────────

    def _handle_url(self) -> Path:
        # Use a stem template — yt-dlp appends the real format extension
        # e.g. "download.%(ext)s" → "download.mp4" → converted to "download.mp3"
        template = str(self.temp_dir / "download.%(ext)s")
        _get_ui().sys("Downloading from YouTube…")

        subprocess.run(
            ["yt-dlp", "-x", "--audio-format", "mp3",
             "--audio-quality", "0", "-o", template, self.src],
            check=True, capture_output=True, timeout=300,
        )

        # Find whatever audio container yt-dlp produced.
        # yt-dlp may output .mp3, .m4a, .mp4, .webm, .opus depending on its
        # own ffmpeg availability. We let our FFmpeg do the final encode.
        _AUDIO_EXTS = {".mp3", ".m4a", ".mp4", ".opus", ".ogg", ".webm", ".flac"}
        candidates = [
            f for f in self.temp_dir.iterdir()
            if f.suffix.lower() in _AUDIO_EXTS
            and not f.name.endswith(".info.json")
        ]
        if not candidates:
            raise FileNotFoundError(
                f"yt-dlp download succeeded but no audio file found in {self.temp_dir}. "
                f"Files: {list(self.temp_dir.iterdir())}"
            )
        # Prefer mp3 > m4a > mp4 > anything else
        actual_audio = sorted(candidates, key=lambda f: (f.suffix != ".mp3", f.suffix != ".m4a"))[0]

        res = subprocess.run(
            ["yt-dlp", "--print", "%(uploader)s|||%(title)s", self.src],
            capture_output=True, text=True,
        )
        meta   = res.stdout.strip().split("|||")
        artist = meta[0] if len(meta) > 1 else ""
        title  = meta[1] if len(meta) > 1 else meta[0]

        final_path = self._get_output_path(artist, title)
        self._input_src = str(actual_audio)
        return self._execute_ffmpeg(str(actual_audio), final_path, artist=artist, title=title)

    def _handle_file(self) -> Path:
        assets     = resolve_assets(self.src)
        final_path = self._get_output_path(assets.artist_name, assets.track_title)
        self._input_src = self.src
        return self._execute_ffmpeg(
            self.src, final_path,
            artist=assets.artist_name,
            album=assets.album_name,
            title=assets.track_title,
        )

    # ── FFmpeg ────────────────────────────────────────────────────────────────

    def _execute_ffmpeg(
        self,
        input_src: str,
        output_path: Path,
        artist: str = "",
        album: str = "",
        title: str = "",
    ) -> Path:
        self.duration = max(0.0, self.end - self.start)
        _get_ui().sys(
            f"Processing audio ({self.start:.2f}s – {self.end:.2f}s, "
            f"{self.duration:.1f}s)…"
        )

        filters: list[str] = []
        # Per-clip fade takes precedence over config auto_fade
        fi = self._fade_in
        fo = self._fade_out
        if fi is None and fo is None and self.config.get("auto_fade", True):
            fd = self.config.get("fade_duration", 0.5)
            fi = fo = fd
        if fi and fi > 0:
            filters.append(f"afade=t=in:st=0:d={fi}")
        if fo and fo > 0:
            filters.append(f"afade=t=out:st={max(0, self.duration - fo)}:d={fo}")

        cmd = ["ffmpeg", "-y"]
        # Only add -ss if we're not starting from 0 (avoids seek on very short files)
        if self.start > 0:
            cmd += ["-ss", str(self.start)]
        cmd += ["-i", input_src, "-t", str(self.duration)]
        if filters:
            cmd += ["-af", ",".join(filters)]
        cmd += [
            "-map", "0:a",
            "-map", "0:v?",
            "-map_metadata", "0",
            "-c:a", "libmp3lame", "-q:a", "2",
            "-c:v", "copy",
            str(output_path),
        ]

        from rich.status import Status
        with Status("[cyan]Encoding audio…[/cyan]", console=Console()) as status:
            result = subprocess.run(cmd, capture_output=True, text=True)

 
        if result.returncode != 0:
            _get_ui().err(f"FFmpeg error (exit {result.returncode})")
            # Show the last 20 lines of stderr for diagnostics
            for ln in result.stderr.splitlines()[-20:]:
                Console().print(f"  [dim]{ln}[/dim]")
            raise subprocess.CalledProcessError(result.returncode, cmd)

        return self._finalize(
            output_path, input_src,
            artist=artist, album=album, title=title,
        )

    # ── Post-process ──────────────────────────────────────────────────────────

    def _finalize(
        self,
        path: Path,
        input_src: str,
        artist: str = "",
        album: str = "",
        title: str = "",
    ) -> Path:
        HISTORY_FILE.write_text(self.src)
        _get_ui().info(f"Saved clip: [white]{path.name}[/white]")

        if self.config.get("copy_to_clipboard", True):
            subprocess.run(
                ["osascript", "-e", f'set the clipboard to (POSIX file "{path}")']
            )
            _get_ui().sys("Copied to clipboard.")

        _notify("Clipped", f"Saved: {path.name}")

        return path


def process_clip(
    src: str,
    start: float,
    end: float,
    is_url: bool = False,
    dry_run: bool = False,
    fade_in: float | None = None,
    fade_out: float | None = None,
    output_path: Path | None = None,
) -> Path | None:
    """
    Clip audio from *start* to *end*.

    Args:
        fade_in  : Fade-in duration in seconds (None = use config default).
        fade_out : Fade-out duration in seconds (None = use config default).
    """
    if dry_run:
        UI = _get_ui()
        Console().print(f"\n[bold cyan]── Dry Run ──[/bold cyan]")
        UI.sys(f"Source   : {src}")
        UI.sys(f"Start    : {start}s")
        UI.sys(f"End      : {end}s")
        UI.sys(f"Duration : {end - start:.1f}s")
        UI.sys(f"Fade in  : {fade_in if fade_in is not None else 'auto'}s")
        UI.sys(f"Fade out : {fade_out if fade_out is not None else 'auto'}s\n")
        return None

    clipper = AudioClipper(src, start, end, fade_in=fade_in, fade_out=fade_out, output_path=output_path)
    try:
        return clipper.run(is_url)
    finally:
        shutil.rmtree(clipper.temp_dir, ignore_errors=True)


# ── Keyboard Maestro / Swinsian hotkey helpers ────────────────────────────────

def mark_start() -> None:
    """Mark the current playback position in Swinsian as clip start."""
    state_file = Path("/tmp/clipped_hotkey.json")
    res = subprocess.run(
        ["osascript", "-e",
         'tell application "Swinsian" to get {player position, current track\'s location}'],
        capture_output=True, text=True,
    )
    pos, loc = res.stdout.strip().split(", ", 1)
    state_file.write_text(json.dumps({"start": pos, "src": loc}))
    _get_ui().info(f"Start marked at [bold white]{pos}s[/bold white]")


def mark_end() -> None:
    """Mark the current playback position and clip from start to now."""
    state_file = Path("/tmp/clipped_hotkey.json")
    if not state_file.exists():
        _get_ui().err("No start marker found. Press the mark-start hotkey first.")
        return

    state = json.loads(state_file.read_text())
    res = subprocess.run(
        ["osascript", "-e", 'tell application "Swinsian" to get player position'],
        capture_output=True, text=True,
    )
    end_pos = res.stdout.strip()
    _get_ui().info(f"End marked at [bold white]{end_pos}s[/bold white] — Processing…")

    process_clip(state["src"], float(state["start"]), float(end_pos))
    state_file.unlink(missing_ok=True)
