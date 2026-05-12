"""
Clip library — append-only JSONL log of every audio clip and video generated.

Schema (one JSON object per line):
  id          : str   — uuid4
  created_at  : str   — ISO-8601
  source      : str   — local path or YouTube URL
  start       : float — seconds
  end         : float — seconds
  output_audio: str   — path (or "" if not clipped)
  output_video: str   — path (or "" if no video)
  artist      : str
  album       : str
  title       : str
  platform    : str   — e.g. "instagram" or "default"
  template    : str   — e.g. "spinner"

Usage:
    from .library import Library
    lib = Library()
    lib.record(entry)
    results = lib.search("Slayer")
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class ClipEntry:
    source: str
    start: float
    end: float
    output_audio: str = ""
    output_video: str = ""
    artist: str = ""
    album: str = ""
    title: str = ""
    platform: str = "default"
    template: str = "spinner"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @property
    def duration(self) -> float:
        return round(self.end - self.start, 2)

    @property
    def display_name(self) -> str:
        if self.artist and self.title:
            return f"{self.artist} — {self.title}"
        return self.title or Path(self.source).stem

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "ClipEntry":
        known = {k: data[k] for k in cls.__dataclass_fields__ if k in data}
        return cls(**known)


class Library:
    """Thread-safe append-only JSONL clip library."""

    def __init__(self, path: Optional[Path] = None):
        if path is None:
            from .config import CONFIG_FILE
            path = CONFIG_FILE.parent / "library.jsonl"
        self.path = path

    def record(self, entry: ClipEntry) -> None:
        """Append a clip entry to the library."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry.to_dict()) + "\n")

    def all(self) -> list[ClipEntry]:
        """Return all entries, newest first."""
        if not self.path.exists():
            return []
        entries = []
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(ClipEntry.from_dict(json.loads(line)))
                    except Exception:
                        pass
        return list(reversed(entries))

    def search(self, query: str) -> list[ClipEntry]:
        """Case-insensitive substring search across artist, title, album, source."""
        q = query.lower()
        return [
            e for e in self.all()
            if q in e.artist.lower()
            or q in e.title.lower()
            or q in e.album.lower()
            or q in e.source.lower()
        ]

    def count(self) -> int:
        return len(self.all())
