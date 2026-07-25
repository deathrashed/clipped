"""
Dynamic Reel Artist template — Vertical (9:16) with full story:
1. Logo fade in/out
2. Large Spinning Record (high position)
3. Full square album art reveal (75% start)
4. Artist photo reveal (fades in after album art)
5. Professional Typography starting during Spinner stage
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
_T_ART_START  = 0.70   # fraction of duration (earlier to leave room for artist)
_T_SPIN_OVERLAP = 0.3  # overlap between spinner and art
_T_ARTIST_ART_OVERLAP = 0.5  # quick crossfade between album art and artist photo
_T_FADE_DUR   = 1.2    # shorter, snappier fades
_T_TEXT_START = 7.0
_T_END_GAP    = 2.0
_T_TEXT_FADE_BEFORE_ART = 0.5
_T_TEXT_FADE_DUR = 1.0
_T_CORNER_R   = 60     # rounded corner radius for artist photo (px)
_Y_TITLE      = 1380
_Y_ARTIST     = 1495
_Y_PHOTO      = 485    # artist photo centered vertically (separate from album art at _Y_HIGH)
_FONT_FILE    = "/System/Library/Fonts/Supplemental/Arial.ttf"


class ReelArtistTemplate(VideoTemplate):
    info = TemplateInfo(
        name="reel_artist",
        label="Dynamic Reel Artist (Logo -> Spinner -> Art -> Artist)",
        description="Full vertical sequence with logo, spinner, album art square, and artist photo reveal.",
        aspect=(_W, _H),
        ideal_for=["Instagram Reels", "TikTok", "YouTube Shorts"],
    )

    def get_inputs(self, assets: MediaAssets) -> list[str]:
        inputs = [str(assets.audio_path)]
        if assets.cover:
            inputs.append(str(assets.cover))
        if assets.logo:
            inputs.append(str(assets.logo))
        if assets.artist:
            inputs.append(str(assets.artist))
        return inputs

    def get_filter_graph(self, assets: MediaAssets, duration: float) -> str:
        speed = self.config.get("spinner_speed", 2)
        cover_idx = 1 if assets.cover else None
        logo_idx = 1 + (1 if assets.cover else 0) if assets.logo else None
        artist_idx = 1 + (1 if assets.cover else 0) + (1 if assets.logo else 0) if assets.artist else None
        logo_fade_dur = min(1.0, max(0.25, duration * 0.08))
        t_logo_end = min(_T_LOGO_END, max(logo_fade_dur * 2, duration * 0.25))
        t_logo_fade_out = max(logo_fade_dur, t_logo_end - logo_fade_dur)

        t_spin_start = min(_T_SPIN_START, max(t_logo_end, duration * 0.25))
        t_art_start = max(t_spin_start + 0.75, duration * _T_ART_START)
        t_art_start = min(t_art_start, max(t_spin_start + 0.75, duration - 2.5))
        t_spin_end = t_art_start + _T_SPIN_OVERLAP
        t_spin_fade_out = max(t_spin_start, t_spin_end - 1)
        t_art_fade_start = max(t_art_start + _T_FADE_DUR, duration - _T_END_GAP - 2)

        # Artist photo timing: longer, smoother crossfade with album art
        if assets.artist:
            t_artist_start = t_art_start + 1.0  # start fading in soon after art appears
            t_artist_fade_out = max(t_artist_start + _T_FADE_DUR, duration - _T_END_GAP)
        else:
            t_artist_start = duration
            t_artist_fade_out = duration

        steps: list[str] = []

        # ── Background: blurred and darkened ──────────────────────────────────
        if assets.cover:
            steps.append(
                f"[{cover_idx}:v]scale={_W}:{_H}:force_original_aspect_ratio=increase,"
                f"crop={_W}:{_H},gblur=sigma=40,eq=brightness=-0.3:saturation=0.6[bg]"
            )
        else:
            steps.append(f"color=s={_W}x{_H}:c=#0d0d0d[bg]")

        current_v = "[bg]"

        # ── Stage 1: Logo Fade In/Out ────────────────────────────────────────
        if assets.logo:
            steps.append(
                f"[{logo_idx}:v]scale={_LOGO_SZ}:{_LOGO_SZ}:force_original_aspect_ratio=decrease,"
                f"format=rgba,fade=t=in:st=0.5:d={logo_fade_dur}:alpha=1,"
                f"fade=t=out:st={t_logo_fade_out}:d={logo_fade_dur}:alpha=1[logo_ov]"
            )
            steps.append(f"{current_v}[logo_ov]overlay=(W-w)/2:(H-h)/2[v1]")
            current_v = "[v1]"

        # ── Stage 2: Spinning Record ─────────────────────────────────────────
        if assets.cover:
            steps.append(
                f"[{cover_idx}:v]scale={_SPINNER_SZ}:{_SPINNER_SZ}:force_original_aspect_ratio=decrease,"
                f"pad={_SPINNER_SZ}:{_SPINNER_SZ}:(ow-iw)/2:(oh-ih)/2:color=black@0,format=rgba,"
                f"geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':"
                f"a='if(lte(pow(X-W/2,2)+pow(Y-H/2,2),pow(W/2,2)),255,0)',"
                f"rotate=t*{speed}:c=none,"
                f"fade=t=in:st={t_spin_start}:d=1:alpha=1,"
                f"fade=t=out:st={t_spin_fade_out}:d=1:alpha=1[spinner_ov]"
            )
            steps.append(
                f"{current_v}[spinner_ov]overlay=(W-w)/2:{_Y_HIGH}:"
                f"enable='between(t,{t_spin_start},{t_spin_end})'[v2]"
            )
            current_v = "[v2]"

        # ── Stage 3: Full square album art reveal ────────────────────────────
        if assets.cover:
            steps.append(
                f"[{cover_idx}:v]scale={_PHOTO_SZ}:{_PHOTO_SZ}:force_original_aspect_ratio=decrease,"
                f"pad={_PHOTO_SZ}:{_PHOTO_SZ}:(ow-iw)/2:(oh-ih)/2:color=black@0,"
                f"format=rgba,"
                f"fade=t=in:st={t_art_start}:d={_T_FADE_DUR}:alpha=1,"
                f"fade=t=out:st={t_art_fade_start}:d={_T_FADE_DUR}:alpha=1[artist_ov]"
            )
            # Extend art visibility so it overlaps with artist photo for smoother crossfade
            t_art_disable = max(t_artist_start + _T_FADE_DUR, t_art_fade_start + _T_FADE_DUR)
            steps.append(
                f"{current_v}[artist_ov]overlay=(W-w)/2:{_Y_HIGH}:"
                f"enable='between(t,{t_art_start},{t_art_disable})'[v3]"
            )
            current_v = "[v3]"

        # ── Stage 4: Artist Photo Reveal (with rounded corners) ─────────────
        if assets.artist:
            r = _T_CORNER_R
            steps.append(
                f"[{artist_idx}:v]scale={_PHOTO_SZ}:{_PHOTO_SZ}:force_original_aspect_ratio=decrease,"
                f"pad={_PHOTO_SZ}:{_PHOTO_SZ}:(ow-iw)/2:(oh-ih)/2:color=black@0,"
                f"format=rgba,"
                f"fade=t=in:st={t_artist_start}:d={_T_FADE_DUR}:alpha=1,"
                f"fade=t=out:st={t_artist_fade_out}:d={_T_FADE_DUR}:alpha=1,"
                # Rounded corners via geq: keep existing alpha inside rounded rect, zero outside
                f"geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':"
                f"a='if(lte(abs(X-W/2),W/2-{r})*lte(abs(Y-H/2),H/2-{r})"
                f"+lte(hypot(abs(X-W/2)-W/2+{r},abs(Y-H/2)-H/2+{r}),{r}),"
                f"alpha(X,Y),0)'[artist_photo_ov]"
            )
            steps.append(
                f"{current_v}[artist_photo_ov]overlay=(W-w)/2:{_Y_PHOTO}:"
                f"enable='gte(t,{t_artist_start})'[v4]"
            )
            current_v = "[v4]"

        graph = ";".join(steps)
        return graph + ";" + self._drawtext_overlay(
            assets,
            duration=duration,
            art_fade_start=t_artist_start if assets.artist else t_art_fade_start,
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

        t_title_start = min(_T_TEXT_START, max(0.5, duration * 0.35))
        t_artist_start_txt = min(t_title_start + 1.0, max(t_title_start, duration - _T_TEXT_FADE_DUR))
        t_text_end = min(
            duration,
            max(t_artist_start_txt + _T_TEXT_FADE_DUR, art_fade_start - _T_TEXT_FADE_BEFORE_ART),
        )
        title_fade_dur = min(
            _T_TEXT_FADE_DUR,
            max(0.25, (t_text_end - t_title_start) / 2),
        )
        artist_fade_dur = min(
            _T_TEXT_FADE_DUR,
            max(0.25, (t_text_end - t_artist_start_txt) / 2),
        )
        alpha_title = self.get_fade_alpha(t_title_start, t_text_end, title_fade_dur)
        alpha_artist = self.get_fade_alpha(t_artist_start_txt, t_text_end, artist_fade_dur)

        font = f":fontfile='{self._escape_path(_FONT_FILE)}'" if Path(_FONT_FILE).exists() else ""
        common = f"{font}:text_align=center:expansion=none"

        return (
            f"{link_in}"
            f"drawtext={title_src}:fontcolor=white:fontsize={title_fs}{common}"
            f":x=(w-text_w)/2:y={y_title}:enable='between(t,{t_title_start},{t_text_end})':alpha='{alpha_title}',"
            f"drawtext={artist_src}:fontcolor=0xBBBBBB:fontsize={artist_fs}{common}"
            f":x=(w-text_w)/2:y={y_artist}:enable='between(t,{t_artist_start_txt},{t_text_end})':alpha='{alpha_artist}'"
            f"{link_out}"
        )
