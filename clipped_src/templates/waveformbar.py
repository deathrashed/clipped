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
        safe_duration_hint=30.0,
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

        steps: list[str] = []
        steps.append(self._build_waveform_step(mode, color))

        if assets.cover:
            steps.extend(self._build_cover_background_steps(assets, art_x))
        else:
            steps.extend(self._build_plain_background_steps())

        graph = ";".join(steps)
        return graph + ";" + self._drawtext_overlay(assets)

    def _build_waveform_step(self, mode: str, color: str) -> str:
        return (
            f"[0:a]showwaves=s={_W}x{_BAR_H}:mode={mode}:colors={color}:rate=30,"
            f"format=rgba[wave]"
        )

    def _build_cover_background_steps(self, assets: "MediaAssets", art_x: int) -> list[str]:
        steps: list[str] = [
            f"[1:v]scale={_W}:{_H}:force_original_aspect_ratio=increase,"
            f"crop={_W}:{_H},gblur=sigma=25,eq=brightness=-0.35:saturation=0.7[bgblur]",
            f"color=s={_W}x{_H}:c=black@0.45[darkmask]",
            f"[bgblur][darkmask]overlay=0:0[bg]",
            f"[1:v]scale={_ART_SZ}:{_ART_SZ}:force_original_aspect_ratio=decrease,"
            f"pad={_ART_SZ}:{_ART_SZ}:(ow-iw)/2:(oh-ih)/2,format=rgba[art]",
            f"[bg][art]overlay={art_x}:{_ART_Y}[mid]",
            f"[wave]colorkey=black:0.1:0.1[wave_trans]",
        ]

        if assets.logo:
            logo_sz = 180
            steps.extend([
                f"[2:v]scale={logo_sz}:{logo_sz}:force_original_aspect_ratio=decrease,format=rgba[logo]",
                f"[mid][logo]overlay=W-w-40:40[mid_logo]",
                f"[mid_logo][wave_trans]overlay=0:{_BAR_Y}[outv]",
            ])
        else:
            steps.append(f"[mid][wave_trans]overlay=0:{_BAR_Y}[outv]")

        return steps

    def _build_plain_background_steps(self) -> list[str]:
        return [
            f"[wave]colorkey=black:0.1:0.1[wave_trans]",
            f"color=s={_W}x{_H}:c=#0a0a0a[bg]",
            f"[bg][wave_trans]overlay=0:{_BAR_Y}[outv]",
        ]

    def _layout_text_positions(
        self,
        title_lines: int,
        artist_lines: int,
        album_lines: int,
        title_fs: int,
        artist_fs: int,
        album_fs: int,
        lh_factor: float = 1.15,
        gap: int = 8,
    ) -> tuple[int, int, int]:
        title_height = title_lines * title_fs * lh_factor
        artist_height = artist_lines * artist_fs * lh_factor
        y_title = _BAR_Y + 16
        y_artist = int(y_title + title_height + gap)
        y_album = int(y_artist + artist_height + gap)
        return y_title, y_artist, y_album

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
        artist_text = self._wrap_text(assets.artist_name, width=28, max_lines=2)
        album_text  = self._wrap_text(assets.album_name,  width=30, max_lines=2)

        title_src  = self._drawtext_source(title_text,  prefix="title")
        artist_src = self._drawtext_source(artist_text, prefix="artist")
        album_src  = self._drawtext_source(album_text,  prefix="album")

        title_lines  = self._line_count(title_text)
        artist_lines = self._line_count(artist_text)
        album_lines  = self._line_count(album_text)

        title_fs  = 34
        artist_fs = 28
        album_fs  = 24
        gap       = 8
        lh_factor = 1.15

        y_title, y_artist, y_album = self._layout_text_positions(
            title_lines, artist_lines, album_lines,
            title_fs, artist_fs, album_fs,
            lh_factor=lh_factor,
            gap=gap,
        )

        common = ":text_align=center:expansion=none"

        return (
            f"{link_in}"
            f"drawtext={title_src}:fontcolor=white:fontsize={title_fs}{common}"
            f":x=(w-text_w)/2:y={y_title}"
            f":enable='gt(t,1)':alpha='if(lt(t,2),t-1,1)',"
            f"drawtext={artist_src}:fontcolor=0x00E5FF:fontsize={artist_fs}{common}"
            f":x=(w-text_w)/2:y={y_artist}"
            f":enable='gt(t,1.5)':alpha='if(lt(t,2.5),t-1.5,1)',"
            f"drawtext={album_src}:fontcolor=0x777777:fontsize={album_fs}{common}"
            f":x=(w-text_w)/2:y={y_album}"
            f":enable='gt(t,2)':alpha='if(lt(t,3),t-2,1)'"
            f"{link_out}"
        )
