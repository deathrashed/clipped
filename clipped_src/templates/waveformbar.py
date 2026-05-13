"""
Waveform Bar template — album art canvas with a live animated waveform.

Output: 1080×1080 (square).

Layout:
  - Background: album art scaled/blurred + dark overlay for depth
  - Centre: crisp album art in a clean framed panel (~640×640)
  - Bottom strip (~220px): animated waveform bar rendered from the audio
  - Text: title / artist / album fade in over the bottom strip

Features:
  - Waveform style can be one of: line, cline, p2p, point (config: waveform_mode)
  - Waveform colour from config: waveform_color (default: #00E5FF — vivid cyan)
  - Works without album art (dark background only)
"""
from __future__ import annotations

from .base import VideoTemplate, TemplateInfo
from ..utils import MediaAssets

# Canvas constants
_W       = 1080
_H       = 1080
_ART_SZ  = 640    # square art panel side
_BAR_H   = 220    # waveform strip height
_ART_Y   = 40     # top margin for art panel
_BAR_Y   = _H - _BAR_H   # 860 — wavestrip y-offset


class WaveformBarTemplate(VideoTemplate):
    info = TemplateInfo(
        name="waveformbar",
        label="Waveform Bar (Live Audio Visual)",
        description="Album art with an animated live waveform bar at the bottom.",
        aspect=(_W, _H),
        ideal_for=["Instagram Feed", "Twitter/X", "SoundCloud", "YouTube"],
    )

    def get_inputs(self, assets: MediaAssets) -> list[str]:
        inputs = [str(assets.audio_path)]
        if assets.cover:
            inputs.append(str(assets.cover))
        if assets.logo:
            inputs.append(str(assets.logo))
        return inputs

    def get_filter_graph(self, assets: MediaAssets, duration: float) -> str:
        mode  = self.config.get("waveform_mode",  "line")    # line|cline|p2p|point
        color = self.config.get("waveform_color", "0x00E5FF")
        art_x = (_W - _ART_SZ) // 2                          # 220

        # Build a flat list of filterchain steps; each is a complete filterchain
        # (possibly chained with commas) prefixed with input pad labels.
        # All steps are joined with "; " at the end.
        steps: list[str] = []

        # ── Waveform generation from the audio stream ──────────────────────────
        steps.append(
            f"[0:a]showwaves=s={_W}x{_BAR_H}:mode={mode}:colors={color}:rate=30,"
            f"format=rgba"
            f"[wave]"
        )

        if assets.cover:
            # ── Background: blurred, darkened artwork fill ────────────────────
            steps.append(
                f"[1:v]scale={_W}:{_H}:force_original_aspect_ratio=increase,"
                f"crop={_W}:{_H},"
                f"gblur=sigma=25,"
                f"eq=brightness=-0.35:saturation=0.7"
                f"[bgblur]"
            )
            # Semi-transparent black overlay to darken the blur
            steps.append(f"color=s={_W}x{_H}:c=black@0.45[darkmask]")
            steps.append(f"[bgblur][darkmask]overlay=0:0[bg]")

            # ── Art panel: centred, padded square ─────────────────────────────
            steps.append(
                f"[1:v]scale={_ART_SZ}:{_ART_SZ}:force_original_aspect_ratio=decrease,"
                f"pad={_ART_SZ}:{_ART_SZ}:(ow-iw)/2:(oh-ih)/2,"
                f"format=rgba"
                f"[art]"
            )

            # ── Waveform strip: dark backing + waveform ───────────────────────
            steps.append(f"color=s={_W}x{_BAR_H}:c=black@0.75[stripbg]")
            steps.append(f"[stripbg][wave]overlay=0:0[wavestrip]")

            # ── Composite: bg → art → wavestrip ──────────────────────────────
            steps.append(f"[bg][art]overlay={art_x}:{_ART_Y}[mid]")
            
            # Optional logo overlay (top right)
            if assets.logo:
                logo_idx = 2
                logo_sz = 180
                steps.append(
                    f"[{logo_idx}:v]scale={logo_sz}:{logo_sz}:force_original_aspect_ratio=decrease,"
                    f"format=rgba[logo]"
                )
                steps.append(f"[mid][logo]overlay=W-w-40:40[mid_logo]")
                steps.append(f"[mid_logo][wavestrip]overlay=0:{_BAR_Y}[outv]")
            else:
                steps.append(f"[mid][wavestrip]overlay=0:{_BAR_Y}[outv]")
        else:
            # ── No cover: plain dark background ──────────────────────────────
            steps.append(f"color=s={_W}x{_H}:c=#0a0a0a[bg]")
            steps.append(f"color=s={_W}x{_BAR_H}:c=#1a1a1a[stripbg]")
            steps.append(f"[stripbg][wave]overlay=0:0[wavestrip]")
            steps.append(f"[bg][wavestrip]overlay=0:{_BAR_Y}[outv]")

        graph = ";".join(steps)
        return graph + ";" + self._drawtext_overlay(assets)

    def _drawtext_overlay(
        self,
        assets: "MediaAssets",
        link_in: str = "[outv]",
        link_out: str = "[v]",
    ) -> str:
        """Fade-in metadata text inside the waveform strip."""
        if not self.has_drawtext():
            return f"{link_in}null{link_out}"

        title_text  = self._wrap_text(assets.track_title, width=30, max_lines=2)
        artist_text = self._wrap_text(assets.artist_name, width=28, max_lines=1)
        album_text  = self._wrap_text(assets.album_name,  width=30, max_lines=1)

        title_src  = self._drawtext_source(title_text,  prefix="title")
        artist_src = self._drawtext_source(artist_text, prefix="artist")
        album_src  = self._drawtext_source(album_text,  prefix="album")

        title_fs = 52
        line_gap = 8

        # When title wraps to 2 lines, push the whole block up so it fits in the strip
        title_extra = (title_fs + line_gap) * (self._line_count(title_text) - 1)

        y_title  = _BAR_Y + 12  - title_extra
        y_artist = _BAR_Y + 95  - title_extra
        y_album  = _BAR_Y + 148 - title_extra

        return (
            f"{link_in}"
            # Track title — large, white, bold
            f"drawtext={title_src}:fontcolor=white:fontsize={title_fs}"
            f":x=(w-text_w)/2:y={y_title}"
            f":enable='gt(t,1)':alpha='if(lt(t,2),t-1,1)',"
            # Artist — medium, cyan
            f"drawtext={artist_src}:fontcolor=0x00E5FF:fontsize=36"
            f":x=(w-text_w)/2:y={y_artist}"
            f":enable='gt(t,1.5)':alpha='if(lt(t,2.5),t-1.5,1)',"
            # Album — dim, italic
            f"drawtext={album_src}:fontcolor=0x777777:fontsize=28:fontstyle=italic"
            f":x=(w-text_w)/2:y={y_album}"
            f":enable='gt(t,2)':alpha='if(lt(t,3),t-2,1)'"
            f"{link_out}"
        )
