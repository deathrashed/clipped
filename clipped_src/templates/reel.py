"""
Dynamic Reel template — Vertical (9:16) with a sequential story:
1. Logo fade in/out
2. Large Spinning Record (high position) - stays until Artist stage
3. Full square album art reveal (75% start)
4. Professional Typography starting during Spinner stage
"""
from __future__ import annotations
from pathlib import Path

from .base import VideoTemplate, TemplateInfo
from ..utils import MediaAssets

# Canvas
_W           = 1080
_H           = 1920
_SPINNER_SZ  = 850
_LOGO_SZ     = 900
_PHOTO_SZ    = 950
_Y_HIGH      = 350
_T_LOGO_END  = 5.0
_T_SPIN_START = 5.0
_T_ART_START  = 0.75   # fraction of duration
_T_SPIN_OVERLAP = 0.5  # overlap between spinner and artist
_T_TEXT_START = 7.0
_T_END_GAP    = 2.0
_T_TEXT_FADE_BEFORE_ART = 1.5
_T_TEXT_FADE_DUR = 1.4
_Y_TITLE      = 1380
_Y_ARTIST     = 1495
_FONT_FILE    = "/System/Library/Fonts/Supplemental/Arial.ttf"


class ReelTemplate(VideoTemplate):
    info = TemplateInfo(
        name="reel",
        label="Dynamic Reel (Logo -> Spinner -> Artist)",
        description="High-energy vertical sequence perfect for Instagram/TikTok.",
        aspect=(_W, _H),
        ideal_for=["Instagram Reels", "TikTok", "YouTube Shorts"],
    )

    def get_inputs(self, assets: MediaAssets) -> list[str]:
        inputs = [str(assets.audio_path)]
        if assets.cover:
            inputs.append(str(assets.cover))
        if assets.logo:
            inputs.append(str(assets.logo))
        return inputs

    def get_filter_graph(self, assets: MediaAssets, duration: float) -> str:
        speed = self.config.get("spinner_speed", 2)
        t_art_start = duration * _T_ART_START
        t_spin_end = t_art_start + _T_SPIN_OVERLAP
        t_art_fade_start = max(0.0, duration - _T_END_GAP - 1)

        steps: list[str] = []

        # ── Background: blurred and darkened ──────────────────────────────────
        if assets.cover:
            steps.append(
                f"[1:v]scale={_W}:{_H}:force_original_aspect_ratio=increase,"
                f"crop={_W}:{_H},gblur=sigma=40,eq=brightness=-0.3:saturation=0.6[bg]"
            )
        else:
            steps.append(f"color=s={_W}x{_H}:c=#0d0d0d[bg]")

        current_v = "[bg]"

        # ── Stage 1: Logo Fade In/Out ────────────────────────────────────────
        if assets.logo:
            steps.append(
                f"[2:v]scale={_LOGO_SZ}:{_LOGO_SZ}:force_original_aspect_ratio=decrease,"
                f"format=rgba,fade=t=in:st=0.5:d=1:alpha=1,fade=t=out:st={_T_LOGO_END - 1.5}:d=1:alpha=1[logo_ov]"
            )
            steps.append(f"{current_v}[logo_ov]overlay=(W-w)/2:(H-h)/2[v1]")
            current_v = "[v1]"

        # ── Stage 2: Spinning Record ─────────────────────────────────────────
        if assets.cover:
            steps.append(
                f"[1:v]scale={_SPINNER_SZ}:{_SPINNER_SZ}:force_original_aspect_ratio=decrease,"
                f"pad={_SPINNER_SZ}:{_SPINNER_SZ}:(ow-iw)/2:(oh-ih)/2:color=black@0,format=rgba,"
                f"geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':"
                f"a='if(lte(pow(X-W/2,2)+pow(Y-H/2,2),pow(W/2,2)),255,0)',"
                f"rotate=t*{speed}:c=none,"
                f"fade=t=in:st={_T_SPIN_START}:d=1:alpha=1,"
                f"fade=t=out:st={t_spin_end - 1}:d=1:alpha=1[spinner_ov]"
            )
            steps.append(
                f"{current_v}[spinner_ov]overlay=(W-w)/2:{_Y_HIGH}:"
                f"enable='between(t,{_T_SPIN_START},{t_spin_end})'[v2]"
            )
            current_v = "[v2]"

        # ── Stage 3: Full square album art reveal ────────────────────────────
        if assets.cover:
            steps.append(
                f"[1:v]scale={_PHOTO_SZ}:{_PHOTO_SZ}:force_original_aspect_ratio=decrease,"
                f"pad={_PHOTO_SZ}:{_PHOTO_SZ}:(ow-iw)/2:(oh-ih)/2:color=black@0,"
                f"format=rgba,"
                f"fade=t=in:st={t_art_start}:d=1:alpha=1,"
                f"fade=t=out:st={t_art_fade_start}:d=1:alpha=1[artist_ov]"
            )
            steps.append(
                f"{current_v}[artist_ov]overlay=(W-w)/2:{_Y_HIGH}:"
                f"enable='gte(t,{t_art_start})'[v3]"
            )
            current_v = "[v3]"

        graph = ";".join(steps)
        return graph + ";" + self._drawtext_overlay(
            assets,
            duration=duration,
            art_fade_start=t_art_fade_start,
            link_in=current_v,
        )

    def _drawtext_overlay(
        self,
        assets: MediaAssets,
        duration: float,
        art_fade_start: float,
        link_in: str = "[outv]",
        link_out: str = "[v]",
    ) -> str:
        if not self.has_drawtext():
            return f"{link_in}null{link_out}"

        title_text  = self._wrap_text(assets.track_title, width=24, max_lines=2)
        artist_text = self._wrap_text(assets.artist_name, width=22, max_lines=1)

        title_src  = self._drawtext_source(title_text,  prefix="title")
        artist_src = self._drawtext_source(artist_text, prefix="artist")

        title_lines  = self._line_count(title_text)
        title_fs  = 68
        artist_fs = 48
        gap       = 15
        lh_factor = 1.15

        h_title = title_lines * title_fs * lh_factor

        # Standard vertical stacking
        y_title  = _Y_TITLE - int((h_title - (title_fs * lh_factor)))
        y_artist = _Y_ARTIST

        t_title_start = _T_TEXT_START
        t_artist_start = _T_TEXT_START + 1.0
        t_text_end = max(t_artist_start + _T_TEXT_FADE_DUR, art_fade_start - _T_TEXT_FADE_BEFORE_ART)
        alpha_title = self.get_fade_alpha(t_title_start, t_text_end, _T_TEXT_FADE_DUR)
        alpha_artist = self.get_fade_alpha(t_artist_start, t_text_end, _T_TEXT_FADE_DUR)

        font = f":fontfile='{self._escape_path(_FONT_FILE)}'" if Path(_FONT_FILE).exists() else ""
        common = f"{font}:text_align=center:expansion=none"

        return (
            f"{link_in}"
            f"drawtext={title_src}:fontcolor=white:fontsize={title_fs}{common}"
            f":x=(w-text_w)/2:y={y_title}:enable='between(t,{t_title_start},{t_text_end})':alpha='{alpha_title}',"
            f"drawtext={artist_src}:fontcolor=0xBBBBBB:fontsize={artist_fs}{common}"
            f":x=(w-text_w)/2:y={y_artist}:enable='between(t,{t_artist_start},{t_text_end})':alpha='{alpha_artist}'"
            f"{link_out}"
        )
