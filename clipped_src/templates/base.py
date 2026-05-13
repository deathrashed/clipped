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
import tempfile
import textwrap
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
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
        self._temp_text_files: list[Path] = []

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
        """Escape text for safe use in FFmpeg filter parameters without outer quotes."""
        if not text:
            return ""
        # Characters that must be escaped in unquoted filter arguments:
        # \ (must come first), :, ,, ', and space.
        for char in ["\\", ":", ",", "'", " "]:
            text = text.replace(char, "\\" + char)
        return text

    def _escape_drawtext(self, text: str) -> str:
        """Escape text for safe use inside quoted FFmpeg drawtext strings."""
        if not text:
            return ""
        text = text.replace("\\", "\\\\")
        text = text.replace("'", "\\'")
        return text.replace("\n", "\\n")

    def _escape_path(self, text: str) -> str:
        """Escape a file path for use in an FFmpeg drawtext textfile parameter."""
        if not text:
            return ""
        return text.replace("\\", "\\\\").replace("'", "\\'")

    def _make_textfile(self, text: str, prefix: str = "clipped_text", suffix: str = ".txt") -> str:
        """Write wrapped text to a temporary file for textfile-based drawtext."""
        tmp = tempfile.NamedTemporaryFile(delete=False, prefix=prefix, suffix=suffix, mode="w", encoding="utf-8")
        tmp.write(text)
        tmp.close()
        path = Path(tmp.name)
        self._temp_text_files.append(path)
        return str(path)

    def _drawtext_source(self, text: str, prefix: str = "clipped_text") -> str:
        """Create a drawtext source clause pointing at a temporary text file."""
        path = self._make_textfile(text, prefix=prefix)
        return f"textfile='{self._escape_path(path)}'"

    def cleanup(self) -> None:
        """Remove temporary text files created while building filter graphs."""
        for path in list(self._temp_text_files):
            try:
                path.unlink()
            except Exception:
                pass
        self._temp_text_files.clear()

    def _wrap_text(self, text: str, width: int = 28, max_lines: int = 2) -> str:
        """
        Wrap long text into multiple lines for FFmpeg drawtext (textfile mode).

        Uses character-count width as a heuristic — not pixel-perfect, but
        good enough for fixed-size monospace-ish rendering at typical font sizes.
        Returns a string with \\n separating lines (written to a temp file).
        """
        if not text:
            return ""
        normalized = " ".join(text.strip().split())
        lines = textwrap.wrap(
            normalized,
            width=width,
            break_long_words=False,
            break_on_hyphens=False,
            max_lines=max_lines,
        )
        if len(lines) == max_lines and len(" ".join(lines)) < len(normalized):
            last = lines[-1].rstrip(" .,;:?!")
            lines[-1] = f"{last}..."
        return "\n".join(lines)

    def _line_count(self, text: str) -> int:
        """Return the number of rendered lines in a wrapped text string."""
        if not text:
            return 1
        return text.count("\n") + 1

    def _drawtext_overlay(self, assets: "MediaAssets", link_in: str = "[outv]", link_out: str = "[v]") -> str:
        """
        Standard three-line metadata overlay: title / artist / album.

        When the title wraps to 2 lines the entire block shifts up by one
        title line-height so the extra line stays inside the reserved area
        rather than overflowing into the frame below.
        """
        if not self.has_drawtext():
            return f"{link_in}null{link_out}"

        title_text  = self._wrap_text(assets.track_title, width=28, max_lines=2)
        artist_text = self._wrap_text(assets.artist_name, width=28, max_lines=2)
        album_text  = self._wrap_text(assets.album_name,  width=32, max_lines=2)

        title_src  = self._drawtext_source(title_text,  prefix="title")
        artist_src = self._drawtext_source(artist_text, prefix="artist")
        album_src  = self._drawtext_source(album_text,  prefix="album")

        w, h = self.info.aspect
        title_fs  = 70
        artist_fs = 45
        album_fs  = 35
        line_gap  = 10  # extra pixels between stacked blocks

        # Extra vertical space consumed by a 2-line title
        title_extra = (title_fs + line_gap) * (self._line_count(title_text) - 1)

        y_title  = h - 220 - title_extra
        y_artist = h - 130 - title_extra
        y_album  = h - 70  - title_extra

        return (
            f"{link_in}"
            f"drawtext={title_src}:fontcolor=white:fontsize={title_fs}"
            f":x=(w-text_w)/2:y={y_title}:enable='gt(t,1)':alpha='{self.get_fade_alpha(1.0, 0, 1.0)}',"
            f"drawtext={artist_src}:fontcolor=0xAAAAAA:fontsize={artist_fs}"
            f":x=(w-text_w)/2:y={y_artist}:enable='gt(t,1.5)':alpha='{self.get_fade_alpha(1.5, 0, 1.0)}',"
            f"drawtext={album_src}:fontcolor=0x888888:fontsize={album_fs}"
            f":x=(w-text_w)/2:y={y_album}:enable='gt(t,2)':alpha='{self.get_fade_alpha(2.0, 0, 1.0)}'"
            f"{link_out}"
        )

    def get_fade_alpha(self, st: float, et: float = 0, dur: float = 1.0) -> str:
        """
        Generate an FFmpeg alpha expression for a fade-in and optional fade-out.
        
        Args:
            st  : Start time (fade-in start)
            et  : End time (fade-out end). If 0 or < st, no fade-out is applied.
            dur : Fade duration (used for both in and out).
        """
        fade_in = f"if(lt(t,{st}),0,if(lt(t,{st+dur}),(t-{st})/{dur},1))"
        if et > st + dur:
            # Add fade-out: if(lt(t, et-dur), 1, if(lt(t, et), 1-(t-(et-dur))/dur, 0))
            # Combined with fade-in:
            return (
                f"if(lt(t,{st}),0,"
                f"if(lt(t,{st+dur}),(t-{st})/{dur},"
                f"if(lt(t,{et-dur}),1,"
                f"if(lt(t,{et}),1-(t-({et-dur}))/{dur},0))))"
            )
        return fade_in

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
