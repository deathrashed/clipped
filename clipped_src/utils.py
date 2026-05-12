"""
Clipped utility module.

Provides:
  - parse_time()       — "M:SS" / float string → float seconds
  - MediaAssets        — resolves cover art, logo, band photo + audio metadata
  - resolve_assets()   — convenience wrapper around MediaAssets
  - get_youtube_title() — yt-dlp title probe
"""
from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path


# ── Time parsing ──────────────────────────────────────────────────────────────

def parse_time(time_str: str | None) -> float:
    """
    Parse a time string into float seconds.
    Supported formats: "SS", "SS.ms", "M:SS", "H:MM:SS"
    """
    if not time_str:
        return 0.0
    
    s = str(time_str).strip()
    if not s:
        return 0.0

    # 1. Direct float/int
    try:
        return float(s)
    except ValueError:
        pass

    # 2. Colon formats
    if ":" in s:
        try:
            parts = [float(p) for p in s.split(":")]
            if len(parts) == 3:    # H:MM:SS
                return parts[0] * 3600 + parts[1] * 60 + parts[2]
            if len(parts) == 2:    # M:SS
                return parts[0] * 60 + parts[1]
        except (ValueError, IndexError):
            pass
            
    return 0.0


# ── Rich metadata dataclass ───────────────────────────────────────────────────

@dataclass
class TrackMetadata:
    """All the tag fields we extract from an audio file."""
    artist:      str = ""
    album:       str = ""
    title:       str = ""
    track:       str = ""   # "3" or "3/12"
    track_num:   int = 0    # numeric track number
    year:        str = ""
    genre:       str = ""
    disc:        str = ""
    comment:     str = ""
    duration:    float = 0.0


def read_metadata(audio_path: Path) -> TrackMetadata:
    """
    Extract metadata from an audio file.

    Strategy:
      1. Try mutagen (handles MP3 ID3, FLAC, MP4/M4A, OGG, OPUS, WAV).
      2. Fall back to ffprobe JSON for any format mutagen can't parse.
      3. Last resort: use the filename stem as the title.
    """
    meta = _try_mutagen(audio_path)
    if not meta:
        meta = _try_ffprobe(audio_path)
    if not meta:
        meta = TrackMetadata(title=audio_path.stem)
    # Fill in title from stem if still empty
    if not meta.title:
        meta.title = audio_path.stem
    return meta


def _try_mutagen(path: Path) -> TrackMetadata | None:
    try:
        from mutagen import File as MutagenFile
        from mutagen.id3 import ID3NoHeaderError
    except ImportError:
        return None

    try:
        f = MutagenFile(str(path), easy=True)
        if f is None:
            return None

        def _get(key: str) -> str:
            val = f.get(key)
            return str(val[0]).strip() if val else ""

        track_str = _get("tracknumber")
        track_num = 0
        if track_str:
            try:
                track_num = int(track_str.split("/")[0])
            except ValueError:
                pass

        dur = 0.0
        if hasattr(f, "info") and f.info:
            dur = getattr(f.info, "length", 0.0)

        return TrackMetadata(
            artist=_get("artist") or _get("albumartist"),
            album=_get("album"),
            title=_get("title"),
            track=track_str,
            track_num=track_num,
            year=_get("date") or _get("year"),
            genre=_get("genre"),
            disc=_get("discnumber"),
            comment=_get("comment"),
            duration=dur,
        )
    except Exception:
        return None


def _try_ffprobe(path: Path) -> TrackMetadata | None:
    try:
        cmd = [
            "ffprobe", "-v", "quiet",
            "-print_format", "json",
            "-show_format", "-show_streams",
            str(path),
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        data = json.loads(res.stdout)
        tags = data.get("format", {}).get("tags", {})
        tags = {k.lower(): v for k, v in tags.items()}

        track_str = tags.get("track", "")
        track_num = 0
        if track_str:
            try:
                track_num = int(track_str.split("/")[0])
            except ValueError:
                pass

        dur = 0.0
        try:
            dur = float(data.get("format", {}).get("duration", 0))
        except (ValueError, TypeError):
            pass

        return TrackMetadata(
            artist=tags.get("artist", "") or tags.get("album_artist", ""),
            album=tags.get("album", ""),
            title=tags.get("title", ""),
            track=track_str,
            track_num=track_num,
            year=tags.get("date", "") or tags.get("year", ""),
            genre=tags.get("genre", ""),
            disc=tags.get("disc", ""),
            comment=tags.get("comment", ""),
            duration=dur,
        )
    except Exception:
        return None


# ── Media asset resolver ──────────────────────────────────────────────────────

class MediaAssets:
    """
    Resolves all media assets associated with an audio file:
      - cover art (album dir)
      - band logo and band photo (artist dir)
      - rich track metadata via mutagen → ffprobe fallback
    """

    def __init__(self, audio_path: Path):
        self.audio_path = audio_path.resolve()
        self.album_dir  = self.audio_path.parent
        self.artist_dir = self.album_dir.parent

        # Image assets
        self.cover  = self._find(["cover", "front", "folder", "album", "art"], self.album_dir)
        self.logo   = self._find(["logo"],                              self.artist_dir)
        self.artist = self._find(["artist", "band", "photo"],           self.artist_dir)

        # Fallbacks: if cover is missing in album dir, look in artist dir for anything
        if not self.cover:
            self.cover = self.logo or self.artist

        # All available images for custom sequences (cover + artist images)
        self.all_images = self._find_all([self.album_dir, self.artist_dir])

        # Rich metadata
        self._meta = read_metadata(self.audio_path)

    # ── Convenience properties ────────────────────────────────────────────────

    @property
    def artist_name(self) -> str:
        return self._meta.artist

    @property
    def album_name(self) -> str:
        return self._meta.album

    @property
    def track_title(self) -> str:
        return self._meta.title

    @property
    def track_number(self) -> int:
        return self._meta.track_num

    @property
    def year(self) -> str:
        return self._meta.year

    @property
    def genre(self) -> str:
        return self._meta.genre

    @property
    def duration(self) -> float:
        return self._meta.duration

    @property
    def meta(self) -> TrackMetadata:
        """Access the full TrackMetadata dataclass."""
        return self._meta

    def summary(self) -> str:
        """Human-readable one-liner for TUI display."""
        parts = []
        if self._meta.artist: parts.append(self._meta.artist)
        if self._meta.album:  parts.append(self._meta.album)
        if self._meta.title:  parts.append(f'"{self._meta.title}"')
        if self._meta.year:   parts.append(f"({self._meta.year})")
        return "  ".join(parts) if parts else self.audio_path.name

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _find(self, names: list[str], directory: Path) -> Path | None:
        if not directory.exists() or not directory.is_dir():
            return None
        
        try:
            files = list(directory.iterdir())
        except OSError:
            return None

        img_exts = {".jpg", ".jpeg", ".png", ".webp"}
        names_lower = [n.lower() for n in names]

        # 1. Try exact matches first
        for f in files:
            if f.suffix.lower() in img_exts:
                stem_lower = f.stem.lower()
                if any(stem_lower == n for n in names_lower):
                    return f

        # 2. Try substring matches
        for f in files:
            if f.suffix.lower() in img_exts:
                stem_lower = f.stem.lower()
                if any(n in stem_lower for n in names_lower):
                    return f
        return None

    def _find_all(self, dirs: list[Path]) -> list[Path]:
        images: set[Path] = set()
        img_exts = {".jpg", ".jpeg", ".png", ".webp"}
        for d in dirs:
            if d.exists() and d.is_dir():
                for f in d.iterdir():
                    if f.suffix.lower() in img_exts:
                        images.add(f)
        return sorted(images)


# ── Convenience wrapper ───────────────────────────────────────────────────────

def resolve_assets(filepath: str) -> MediaAssets:
    return MediaAssets(Path(filepath))


# ── Output Path Generation ──────────────────────────────────────────────────

def get_output_path(
    base_dir: Path,
    artist: str = "",
    title: str = "",
    fallback_stem: str = "",
    template: str = "",
    extension: str = "mp3"
) -> Path:
    """
    Generate a sanitized output file path.
    Format: "Artist - Title.ext" or "Artist - Title (Template).ext"
    """
    base_dir = base_dir.expanduser()
    base_dir.mkdir(parents=True, exist_ok=True)

    if artist and title:
        name = f"{artist} - {title}"
        if template:
            name += f" ({template})"
    else:
        name = title or fallback_stem
        if template:
            name += f"_{template}"

    # Robust sanitization
    safe = "".join(c for c in name if c.isalnum() or c in " -_").strip()
    safe = safe.replace("  ", " ")
    
    return base_dir / f"{safe}.{extension}"


# ── YouTube title probe ───────────────────────────────────────────────────────

def get_youtube_title(url: str) -> str:
    res = subprocess.run(
        ["yt-dlp", "--print", "%(title)s", url],
        capture_output=True, text=True, timeout=30,
    )
    if res.returncode == 0 and res.stdout.strip():
        return res.stdout.strip()
    return "YouTube_Clip"
