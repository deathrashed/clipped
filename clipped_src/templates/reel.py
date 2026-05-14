"""
Dynamic Reel template — Vertical (9:16) with a sequential story:
1. Logo fade in/out
2. Large Spinning Record (high position) - stays until Artist stage
3. Artist Photo (Professional Subtle Border, 75% start)
4. Professional Typography starting during Spinner stage
"""
from __future__ import annotations
from .base import VideoTemplate, TemplateInfo
from ..utils import MediaAssets

# Canvas
_W           = 1080
_H           = 1920
_SPINNER_SZ  = 850
_LOGO_SZ     = 900
_PHOTO_SZ    = 950
_BORDER_PX   = 5
_CORNER_R    = 8
_Y_HIGH      = 350
_T_LOGO_END  = 5.0
_T_SPIN_START = 5.0
_T_ART_START  = 0.75   # fraction of duration
_T_SPIN_OVERLAP = 0.5  # overlap between spinner and artist
_T_TEXT_START = 7.0
_T_END_GAP    = 2.0
_Y_TITLE      = 1380
_Y_ARTIST     = 1495


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

        # ── Stage 3: Artist Photo ────────────────────────────────────────────
        if assets.cover:
            steps.append(
                f"[1:v]scale={_PHOTO_SZ-2*_BORDER_PX}:{_PHOTO_SZ-2*_BORDER_PX}:force_original_aspect_ratio=decrease,"
                f"pad={_PHOTO_SZ-2*_BORDER_PX}:{_PHOTO_SZ-2*_BORDER_PX}:(ow-iw)/2:(oh-ih)/2:color=black@0,"
                f"pad={_PHOTO_SZ}:{_PHOTO_SZ}:{_BORDER_PX}:{_BORDER_PX}:white,"
                f"format=rgba,"
                f"geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':"
                f"a='if(lte(pow(X-W/2,2)+pow(Y-H/2,2),pow(W/2,2)),255,0)',"
                f"fade=t=in:st={t_art_start}:d=1:alpha=1,"
                f"fade=t=out:st={max(0.0, duration - _T_END_GAP - 1)}:d=1:alpha=1[artist_ov]"
            )
            steps.append(
                f"{current_v}[artist_ov]overlay=(W-w)/2:{_Y_HIGH}:"
                f"enable='gte(t,{t_art_start})'[v3]"
            )
            current_v = "[v3]"

        graph = ";".join(steps)
        return graph + ";" + self._drawtext_overlay(assets, link_in=current_v)

    def _drawtext_overlay(self, assets: MediaAssets, link_in: str = "[outv]", link_out: str = "[v]") -> str:
        if not self.has_drawtext():
            return f"{link_in}null{link_out}"

        title_text  = self._wrap_text(assets.track_title, width=24, max_lines=2)
        artist_text = self._wrap_text(assets.artist_name, width=22, max_lines=1)

        title_src  = self._drawtext_source(title_text,  prefix="title")
        artist_src = self._drawtext_source(artist_text, prefix="artist")

        title_lines  = self._line_count(title_text)
        artist_lines = self._line_count(artist_text)

        title_fs  = 52
        artist_fs = 36
        gap       = 15
        lh_factor = 1.15

        h_title = title_lines * title_fs * lh_factor

        # Standard vertical stacking
        y_title  = _Y_TITLE - int((h_title - (title_fs * lh_factor)))
        y_artist = _Y_ARTIST

        common = ":text_align=center:expansion=none"

        return (
            f"{link_in}"
            f"drawtext={title_src}:fontcolor=white:fontsize={title_fs}{common}"
            f":x=(w-text_w)/2:y={y_title}:enable='gt(t,{_T_TEXT_START})':alpha='if(lt(t,{_T_TEXT_START+1}),t-{_T_TEXT_START},1)',"
            f"drawtext={artist_src}:fontcolor=0xBBBBBB:fontsize={artist_fs}{common}"
            f":x=(w-text_w)/2:y={y_artist}:enable='gt(t,{_T_TEXT_START+1})':alpha='if(lt(t,{_T_TEXT_START+2}),t-{_T_TEXT_START+1},1)'"
            f"{link_out}"
        )
