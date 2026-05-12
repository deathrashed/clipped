"""
Abstract base class for all Clipped video templates.

To add a new template:
1. Create a new .py file in this directory
2. Subclass VideoTemplate
3. Set a `info = TemplateInfo(...)` class attribute
4. Implement get_inputs() and get_filter_graph()
5. Register it in registry.py
"""
from __future__ import annotations

import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

# Lazy import to avoid circular dependency
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..utils import MediaAssets


@dataclass
class TemplateInfo:
    """Metadata displayed in the TUI template picker."""
    name: str               # e.g. "spinner"
    label: str              # e.g. "Spinner (Rotating Record)"
    description: str        # One-line user-facing description
    aspect: tuple[int, int] # Output dimensions (width, height)
    ideal_for: list[str] = field(default_factory=list)  # e.g. ["Instagram", "TikTok"]


class VideoTemplate(ABC):
    """
    Abstract base for all video style templates.

    Config is a dict from the [general] section of config.toml,
    giving templates access to user settings like spinner_speed.
    """
    info: TemplateInfo  # Must be set as a class attribute

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self._has_drawtext: Optional[bool] = None

    # ── Capability detection ──────────────────────────────────────────────

    def has_drawtext(self) -> bool:
        """Check whether the installed FFmpeg supports the drawtext filter."""
        if self._has_drawtext is None:
            try:
                res = subprocess.run(
                    ["ffmpeg", "-filters"],
                    capture_output=True, text=True
                )
                self._has_drawtext = "drawtext" in res.stdout
            except Exception:
                self._has_drawtext = False
        return self._has_drawtext

    # ── Helpers ───────────────────────────────────────────────────────────

    def _escape(self, text: str) -> str:
        """Escape text for safe use in FFmpeg drawtext filter."""
        # Colons separate arguments in FFmpeg filters
        text = text.replace(":", "\\:")
        # Single quotes break the text='...' wrapping. 
        # In FFmpeg's filter parser, ' inside '...' is escaped as '\''
        # But wait, the standard way is to use a backslash if not in quotes, 
        # or special sequence if in quotes. 
        # Safer: replace ' with a "smart" quote or just escape it if drawtext allows.
        # Actually, drawtext text parameter handles ' if escaped with \
        return text.replace("'", "\\'")

    def _drawtext_overlay(self, assets: "MediaAssets", link_in: str = "[outv]", link_out: str = "[v]") -> str:
        """
        Standard three-line metadata overlay: title / artist / album.
        Returns an empty string if drawtext is unavailable.
        """
        if not self.has_drawtext():
            return f"{link_in}null{link_out}"

        title  = self._escape(assets.track_title)
        artist = self._escape(assets.artist_name)
        album  = self._escape(assets.album_name)

        w, h = self.info.aspect
        y_title  = h - 220
        y_artist = h - 130
        y_album  = h - 70

        return (
            f"{link_in}"
            f"drawtext=text='{title}':fontcolor=white:fontsize=70"
            f":x=(w-text_w)/2:y={y_title}:enable='gt(t,1)':alpha='if(lt(t\\,2)\\,t-1\\,1)',"
            f"drawtext=text='{artist}':fontcolor=0xAAAAAA:fontsize=45"
            f":x=(w-text_w)/2:y={y_artist}:enable='gt(t,1.5)':alpha='if(lt(t\\,2.5)\\,t-1.5\\,1)',"
            f"drawtext=text='{album}':fontcolor=0x888888:fontsize=35"
            f":x=(w-text_w)/2:y={y_album}:enable='gt(t,2)':alpha='if(lt(t\\,3)\\,t-2\\,1)'"
            f"{link_out}"
        )

    # ── Abstract interface ────────────────────────────────────────────────

    @abstractmethod
    def get_inputs(self, assets: "MediaAssets") -> list[str]:
        """Return list of file paths for FFmpeg -i arguments (audio first)."""
        ...

    @abstractmethod
    def get_filter_graph(self, assets: "MediaAssets", duration: float) -> str:
        """
        Return an FFmpeg filter_complex string.
        The final output video stream must be labelled [v].
        """
        ...

    def get_output_size(self) -> tuple[int, int]:
        """Return (width, height) of this template's output."""
        return self.info.aspect
