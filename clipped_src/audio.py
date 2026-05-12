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
from .library import Library, ClipEntry
from .utils import resolve_assets

console = Console()

# Maximum clip duration before showing a sanity warning
_DURATION_WARN_SECS = 120.0


class AudioClipper:
    def __init__(
        self,
        src: str,
        start: float,
        end: float,
        fade_in: float | None = None,
        fade_out: float | None = None,
    ):
        self.src       = src
        self.start     = start
        self.end       = end
        self.duration  = max(0.0, end - start)
        self.config    = get_config()
        self.temp_dir  = Path(tempfile.mkdtemp())
        self._input_src: str = src  # resolved during run(); used for re-processes

        # Per-clip fade overrides (None = use config auto_fade / fade_duration)
        self._fade_in  = fade_in
        self._fade_out = fade_out

        validate_output_dirs(self.config)

    # ── Output path ───────────────────────────────────────────────────────────

    def _get_output_path(self, artist: str = "", title: str = "") -> Path:
        audio_dir = Path(self.config["audio_dir"]).expanduser()
        audio_dir.mkdir(parents=True, exist_ok=True)

        name = f"{artist} - {title}" if artist and title else (title or Path(self.src).stem)
        safe = "".join(c for c in name if c.isalnum() or c in " -_").strip()
        return audio_dir / f"{safe}.mp3"

    # ── Sanity checks ─────────────────────────────────────────────────────────

    def _check_duration(self) -> None:
        if self.duration > _DURATION_WARN_SECS:
            console.print(
                f"[bold yellow]⚠  Long clip ({self.duration:.0f}s)[/bold yellow] — "
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
        console.print("📥 [dim]Downloading from YouTube…[/dim]")

        subprocess.run(
            ["yt-dlp", "-x", "--audio-format", "mp3",
             "--audio-quality", "0", "-o", template, self.src],
            check=True, capture_output=True,
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
        console.print(
            f"✂️  [dim]Processing audio ({self.start:.2f}s – {self.end:.2f}s, "
            f"{self.duration:.1f}s)…[/dim]"
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
            "-map_metadata", "0",
            "-c:a", "libmp3lame", "-q:a", "2",
            str(output_path),
        ]

        from rich.status import Status
        with Status("[cyan]Encoding audio…[/cyan]", console=console):
            result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            console.print(f"[bold red]FFmpeg error (exit {result.returncode}):[/bold red]")
            # Show the last 20 lines of stderr for diagnostics
            for ln in result.stderr.splitlines()[-20:]:
                console.print(f"  [dim]{ln}[/dim]")
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
        console.print(f"\n✅ [green]Saved clip:[/green] {path}")

        import questionary

        while True:
            choice = questionary.select(
                "Clip preview:",
                choices=["▶ Play", "⇄ Adjust Offset", "✓ Keep"],
            ).ask()

            if choice == "▶ Play":
                console.print(
                    f"[dim]▶ Playing: {self.start:.2f}s – {self.end:.2f}s "
                    f"({self.duration:.1f}s)[/dim]"
                )
                subprocess.run(["afplay", str(path)])

            elif choice == "⇄ Adjust Offset":
                adj = questionary.text(
                    "Shift window by (seconds, e.g. -0.5 or 1.2):", default="0"
                ).ask()
                try:
                    delta = float(adj)
                    if delta == 0:
                        continue
                    self.start += delta
                    self.end   += delta
                    # Re-process in place
                    return self._execute_ffmpeg(
                        input_src, path,
                        artist=artist, album=album, title=title,
                    )
                except ValueError:
                    console.print("[red]Invalid offset.[/red]")

            else:  # Keep
                break

        # Record to library
        lib = Library()
        lib.record(ClipEntry(
            source=self.src,
            start=self.start,
            end=self.end,
            output_audio=str(path),
            artist=artist,
            album=album,
            title=title,
        ))

        # Copy to clipboard
        if self.config.get("copy_to_clipboard", True):
            subprocess.run(
                ["osascript", "-e", f'set the clipboard to (POSIX file "{path}")']
            )
            console.print("[dim]📋 Copied to clipboard.[/dim]")

        return path


def process_clip(
    src: str,
    start: float,
    end: float,
    is_url: bool = False,
    dry_run: bool = False,
    fade_in: float | None = None,
    fade_out: float | None = None,
) -> Path | None:
    """
    Clip audio from *start* to *end*.

    Args:
        fade_in  : Fade-in duration in seconds (None = use config default).
        fade_out : Fade-out duration in seconds (None = use config default).
    """
    if dry_run:
        console.print(
            f"\n[bold cyan]── Dry Run ──[/bold cyan]\n"
            f"  Source   : {src}\n"
            f"  Start    : {start}s\n"
            f"  End      : {end}s\n"
            f"  Duration : {end - start:.1f}s\n"
            f"  Fade in  : {fade_in if fade_in is not None else 'auto'}s\n"
            f"  Fade out : {fade_out if fade_out is not None else 'auto'}s\n"
        )
        return None

    clipper = AudioClipper(src, start, end, fade_in=fade_in, fade_out=fade_out)
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
    console.print(f"📍 [bold green]Start marked at {pos}s[/bold green]")


def mark_end() -> None:
    """Mark the current playback position and clip from start to now."""
    state_file = Path("/tmp/clipped_hotkey.json")
    if not state_file.exists():
        console.print("[red]No start marker found. Press the mark-start hotkey first.[/red]")
        return

    state = json.loads(state_file.read_text())
    res = subprocess.run(
        ["osascript", "-e", 'tell application "Swinsian" to get player position'],
        capture_output=True, text=True,
    )
    end_pos = res.stdout.strip()
    console.print(f"📍 [bold green]End marked at {end_pos}s — Processing…[/bold green]")

    process_clip(state["src"], float(state["start"]), float(end_pos))
    state_file.unlink(missing_ok=True)
