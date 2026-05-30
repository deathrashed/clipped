"""
Clipped utility module.

Provides:
  - parse_time()       — "M:SS" / float string → float seconds
  - MediaAssets        — resolves cover art, logo, band photo + audio metadata
  - resolve_assets()   — convenience wrapper around MediaAssets
  - get_youtube_title() — yt-dlp title probe
"""
from __future__ import annotations

import functools
import json
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
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

    def __init__(
        self,
        audio_path: Path,
        cover_override: str | None = None,
        logo_override: str | None = None,
        artist_override: str | None = None,
        background_override: str | None = None,
        extra_images: list[str] | None = None,
        media: list[str] | None = None,
        lyrics_override: str | None = None,
    ):
        self.audio_path = audio_path.resolve()
        self.album_dir  = self.audio_path.parent
        self.artist_dir = self.album_dir.parent

        # Rich metadata read first to allow iTunes / artist fetching
        self._meta = read_metadata(self.audio_path)

        self._cover_override = cover_override
        self._logo_override = logo_override
        self._artist_override = artist_override
        self.background = self._resolve_path_or_url(background_override) if background_override else None
        
        self.extra_images = [p for p in (self._resolve_path_or_url(u) for u in (extra_images or [])) if p]
        self.media = [p for p in (self._resolve_path_or_url(u) for u in (media or [])) if p]
        self.lyrics = self._resolve_path_or_url(lyrics_override) if lyrics_override else None

        # Embedded lyrics JSON (pre-parsed for Remotion)
        self._lyrics_json: str | None = None
        if not self.lyrics:
            self._lyrics_json = self._extract_embedded_lyrics()

    def _ensure_artist_fetched(self) -> None:
        if getattr(self, "_artist_fetched", False):
            return
        self._artist_fetched = True
        
        logo_basic = self._resolve_path_or_url(self._logo_override) if self._logo_override else self._find(["logo"], self.artist_dir)
        artist_basic = self._resolve_path_or_url(self._artist_override) if self._artist_override else self._find(["artist", "band", "photo"], self.artist_dir)
        
        if self.artist_dir and self.artist_dir.exists() and (not logo_basic or not artist_basic):
            try:
                from .artist_image_fetcher import ArtistImageFetcher
                fetcher = ArtistImageFetcher(verbose=False)
                fetcher.process_artist(
                    artist_name=self.artist_name or self.artist_dir.name,
                    out_dir=self.artist_dir,
                    artist_folder=self.artist_dir,
                )
            except Exception:
                pass

    @functools.cached_property
    def logo(self) -> Path | None:
        logo_path = self._resolve_path_or_url(self._logo_override) if self._logo_override else (self._find(["logo"], self.artist_dir) or self._find(["logo"], self.album_dir))
        if not logo_path:
            self._ensure_artist_fetched()
            logo_path = self._find(["logo"], self.artist_dir) or self._find(["logo"], self.album_dir)
        if logo_path:
            return self._clean_logo_background(logo_path)
        return None

    @functools.cached_property
    def artist(self) -> Path | None:
        artist_path = self._resolve_path_or_url(self._artist_override) if self._artist_override else (self._find(["artist", "band", "photo"], self.artist_dir) or self._find(["artist", "band", "photo"], self.album_dir))
        if not artist_path:
            self._ensure_artist_fetched()
            artist_path = self._find(["artist", "band", "photo"], self.artist_dir) or self._find(["artist", "band", "photo"], self.album_dir)
        return artist_path

    @functools.cached_property
    def cover(self) -> Path | None:
        c = self._resolve_path_or_url(self._cover_override) if self._cover_override else self._find(["cover", "front", "folder", "album", "art"], self.album_dir)
        if not c:
            c = self._extract_embedded_cover()
        if not c:
            c = self._fetch_itunes_cover()
        return c

    @functools.cached_property
    def all_images(self) -> list[Path]:
        images = self._find_all([self.album_dir, self.artist_dir])
        if self.extra_images:
            images.extend(self.extra_images)
        return images

    def _clean_logo_background(self, logo_path: Path) -> Path:
        from .config import get_config
        config = get_config()
        rmbg_path = config.get("rmbg_path", "/Users/rd/Scripts/Riley/rmbg/bin/rmbg")
        rmbg = Path(rmbg_path).expanduser()
        if not rmbg.exists():
            resolved = shutil.which("rmbg")
            if resolved:
                rmbg = Path(resolved)
            else:
                return logo_path

        # If it's already a transparent PNG, check mode (avoid re-running rmbg)
        if logo_path.suffix.lower() == ".png":
            try:
                from PIL import Image
                with Image.open(logo_path) as img:
                    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                        return logo_path
            except Exception:
                pass

        # We'll save the cleaned logo in the same directory as logo_path, but as logo_cleaned.png
        cleaned_path = logo_path.parent / "logo_cleaned.png"
        if cleaned_path.exists() and cleaned_path.stat().st_size > 512:
            return cleaned_path

        cmd = [str(rmbg), "-i", str(logo_path), "-o", str(cleaned_path), "--fuzz", "15"]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0 and cleaned_path.exists():
                return cleaned_path
        except Exception:
            pass
        return logo_path

    def _fetch_itunes_cover(self) -> Path | None:
        artist = self.artist_name
        title = self.track_title
        if not artist or not title:
            term = self.audio_path.stem
        else:
            term = f"{artist} {title}"

        import urllib.request
        import urllib.parse
        import json

        try:
            url_encoded = urllib.parse.quote_plus(term)
            query_url = f"https://itunes.apple.com/search?term={url_encoded}&media=music&limit=1"
            req = urllib.request.Request(
                query_url,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))

            if data and data.get("resultCount", 0) > 0:
                result = data["results"][0]
                artwork_url = result.get("artworkUrl100")
                if artwork_url:
                    high_res_url = artwork_url.replace("100x100bb.jpg", "1000x1000bb.jpg")
                    if "100x100" in high_res_url:
                        high_res_url = high_res_url.replace("100x100", "1000x1000")
                    return self._download_media(high_res_url)
        except Exception:
            pass
        return None

    # ── Convenience properties ────────────────────────────────────────────────

    @property
    def artist_name(self) -> str:
        return self._meta.artist

    @property
    def lyrics_json(self) -> str | None:
        """Pre-parsed JSON lyrics for Remotion. None if not available."""
        return self._lyrics_json

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

    def _resolve_path_or_url(self, path_or_url: str) -> Path | None:
        if not path_or_url:
            return None
        if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
            return self._download_media(path_or_url)
        p = Path(path_or_url).expanduser().resolve()
        return p if p.exists() else None

    def _download_media(self, url: str) -> Path | None:
        import hashlib
        import urllib.request
        from urllib.parse import urlparse
        
        cache_dir = Path("~/.cache/clipped/downloads").expanduser()
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        parsed = urlparse(url)
        if "youtube.com" in parsed.netloc or "youtu.be" in parsed.netloc:
            url_hash = hashlib.md5(url.encode()).hexdigest()[:10]
            out_path = cache_dir / f"yt_{url_hash}.mp4"
            if out_path.exists():
                return out_path
            try:
                subprocess.run(
                    ["yt-dlp", "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4", "-o", str(out_path), url],
                    check=True, capture_output=True
                )
                return out_path
            except subprocess.CalledProcessError:
                return None
        
        url_hash = hashlib.md5(url.encode()).hexdigest()[:10]
        ext = Path(parsed.path).suffix or ".jpg"
        out_path = cache_dir / f"dl_{url_hash}{ext}"
        if out_path.exists():
            return out_path
            
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                out_path.write_bytes(response.read())
            return out_path
        except Exception:
            return None

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
                for n in names_lower:
                    if n in stem_lower:
                        if n == "art" and "artist" in stem_lower:
                            continue
                        return f

        # 3. If there is exactly one image in the directory, use it as a fallback.
        img_files = [f for f in files if f.suffix.lower() in img_exts]
        if len(img_files) == 1:
            f = img_files[0]
            stem_lower = f.stem.lower()
            if "cover" in names_lower:
                if any(x in stem_lower for x in ["artist", "band", "photo", "logo"]):
                    return None
            elif "artist" in names_lower or "band" in names_lower:
                if any(x in stem_lower for x in ["cover", "front", "folder", "album", "logo"]):
                    return None
            elif "logo" in names_lower:
                if any(x in stem_lower for x in ["cover", "front", "folder", "album", "art", "artist", "band", "photo"]):
                    return None
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

    def _extract_embedded_cover(self) -> Path | None:
        try:
            from mutagen import File as MutagenFile
        except ImportError:
            return None

        try:
            f = MutagenFile(str(self.audio_path))
            if f is None or not getattr(f, "tags", None):
                return None

            images: list[bytes] = []
            tags = f.tags
            if hasattr(tags, "getall"):
                images.extend(frame.data for frame in tags.getall("APIC") if hasattr(frame, "data"))
            if "covr" in tags:
                images.extend(bytes(img) for img in tags.get("covr", []) if img)
            if "metadata_block_picture" in tags:
                images.extend(bytes(pic) for pic in tags.get("metadata_block_picture", []) if pic)
            if hasattr(f, "pictures"):
                images.extend(bytes(pic) for pic in getattr(f, "pictures", []) if pic)

            if not images:
                return None

            data = images[0]
            suffix = ".jpg" if data.startswith(b"\xff\xd8") else ".png"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(data)
                return Path(tmp.name)
        except Exception:
            return None

    def _extract_embedded_lyrics(self) -> str | None:
        """
        Extract synced or plain lyrics from audio metadata tags.
        Returns a JSON string of SubtitleLine objects, or None if no lyrics found.

        Checks (in order):
          - ID3 USLT (unsynced) or SYLT (synced) tags in MP3
          - Vorbis 'lyrics' comment (FLAC / OGG)
          - MP4 '©lyr' atom (M4A / MP4)
        """
        try:
            from mutagen import File as MutagenFile
        except ImportError:
            return None

        raw_text: str | None = None
        try:
            f = MutagenFile(str(self.audio_path))
            if f is None or not getattr(f, "tags", None):
                return None

            tags = f.tags

            # -- ID3 SYLT (synced lyrics) --
            if hasattr(tags, "getall"):
                sylt_frames = tags.getall("SYLT")
                if sylt_frames:
                    frame = sylt_frames[0]
                    lines = []
                    data = getattr(frame, "text", [])
                    for text, ms in data:
                        start = ms / 1000.0
                        end = start + 3.0  # guess 3s unless next line resets it
                        lines.append({"start": start, "end": end, "text": text.strip()})
                    # Patch end times from next start
                    for i in range(len(lines) - 1):
                        lines[i]["end"] = lines[i + 1]["start"]
                    if lines:
                        return json.dumps(lines)

            # -- ID3 USLT (unsynced lyrics) --
            if hasattr(tags, "getall"):
                uslt_frames = tags.getall("USLT")
                if uslt_frames:
                    raw_text = getattr(uslt_frames[0], "text", "")

            # -- Vorbis LYRICS comment --
            if raw_text is None and hasattr(tags, "get"):
                for key in ("lyrics", "LYRICS"):
                    val = tags.get(key)
                    if val:
                        raw_text = str(val[0]) if isinstance(val, list) else str(val)
                        break

            # -- MP4 ©lyr atom --
            if raw_text is None and hasattr(tags, "get"):
                lyr = tags.get("\xa9lyr") or tags.get("©lyr")
                if lyr:
                    raw_text = str(lyr[0]) if isinstance(lyr, list) else str(lyr)

        except Exception:
            return None

        if not raw_text or not raw_text.strip():
            return None

        # If it looks like LRC format, parse it
        if "[" in raw_text and "]" in raw_text and ":" in raw_text:
            return self._parse_lrc_to_json(raw_text)

        # Plain-text lyrics: split by line, each line gets a ~3s window
        plain_lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
        if not plain_lines:
            return None
        result = []
        for i, text in enumerate(plain_lines):
            result.append({"start": i * 3.0, "end": (i + 1) * 3.0, "text": text})
        return json.dumps(result)

    @staticmethod
    def _parse_lrc_to_json(lrc_text: str) -> str | None:
        """Parse LRC format to JSON SubtitleLine array."""
        import re
        lines = lrc_text.splitlines()
        time_re = re.compile(r"\[(\d+):(\d+\.?\d*)\](.*)")
        result = []
        for line in lines:
            m = time_re.match(line.strip())
            if m:
                secs = int(m.group(1)) * 60 + float(m.group(2))
                text = m.group(3).strip()
                if text:
                    result.append({"start": secs, "end": secs, "text": text})
        # patch end times
        for i in range(len(result) - 1):
            result[i]["end"] = result[i + 1]["start"]
        if result:
            result[-1]["end"] = result[-1]["start"] + 5.0
        return json.dumps(result) if result else None


# ── Convenience wrapper ───────────────────────────────────────────────────────

def resolve_assets(filepath: str, **kwargs) -> MediaAssets:
    return MediaAssets(Path(filepath), **kwargs)


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
    Format: "Template ⋅ Artist - Title.ext" or "Template ⋅ Title.ext"
    """
    base_dir = base_dir.expanduser()
    base_dir.mkdir(parents=True, exist_ok=True)

    # Format prefix using clean template name if provided
    prefix = ""
    if template:
        words = template.replace("_", " ").split()
        formatted_words = [w.upper() if w.lower() == "vhs" else w.capitalize() for w in words]
        prefix = " ".join(formatted_words) + " ⋅ "

    if artist and title:
        name = f"{prefix}{artist} - {title}"
    else:
        name = f"{prefix}{title or fallback_stem}"

    # Robust sanitization
    safe = "".join(c for c in name if c.isalnum() or c in " -_().⋅·").strip()
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


# ── Showcase registration helper ──────────────────────────────────────────────

def register_clip_in_showcase(
    filepath: Path,
    kind: str,  # "video" or "audio"
    template: str = "",
    platform: str = "",
    start: float = 0.0,
    end: float | None = None,
    artist: str = "",
    title: str = "",
) -> None:
    import json
    import os
    from datetime import datetime
    
    try:
        repo_root = Path(__file__).resolve().parents[2]
        showcase_dir = repo_root / "showcase"
        showcase_dir.mkdir(exist_ok=True)
        
        json_file = showcase_dir / "clips.json"
        js_file = showcase_dir / "clips-list.js"
        
        clips = []
        if json_file.exists():
            try:
                clips = json.loads(json_file.read_text(encoding="utf-8"))
            except Exception:
                clips = []
                
        # Calculate relative path from showcase_dir to output file
        try:
            rel_path = os.path.relpath(filepath, start=showcase_dir)
        except Exception:
            rel_path = str(filepath)
            
        new_clip = {
            "filepath": rel_path,
            "filename": filepath.name,
            "kind": kind,
            "template": template,
            "platform": platform,
            "start": start,
            "end": end,
            "artist": artist,
            "title": title,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Append new clip and save
        clips.insert(0, new_clip)  # Newest clips first
        json_file.write_text(json.dumps(clips, indent=2), encoding="utf-8")
        js_file.write_text(f"var userClips = {json.dumps(clips, indent=2)};\n", encoding="utf-8")
        
    except Exception as e:
        print(f"Warning: Failed to register clip in showcase: {e}", file=sys.stderr)

