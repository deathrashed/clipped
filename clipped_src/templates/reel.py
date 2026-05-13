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
_Y_TITLE      = 1250
_Y_ARTIST     = 1365


class ReelTemplate(VideoTemplate):
    info = TemplateInfo(
        name="reel",
        label="Dynamic Reel (Logo -> Spinner -> Artist)",
        description="Sequential story with large spinner and professional typography.",
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
        speed = self.config.get("spinner_speed", 0.5)
        steps: list[str] = []

        steps.append(
            f"[1:v]scale={_W}:{_H}:force_original_aspect_ratio=increase,"
            f"crop={_W}:{_H},"
            f"gblur=sigma=60,"
            f"eq=brightness=-0.3:saturation=0.8[bg]"
        )

        current_v = "[bg]"
        idx = 2

        t_art_start = duration * _T_ART_START
        t_spin_end  = t_art_start + _T_SPIN_OVERLAP

        if assets.logo:
            steps.append(
                f"[{idx}:v]scale={_LOGO_SZ}:-1,"
                f"fade=t=in:st=0:d=1:alpha=1,"
                f"fade=t=out:st={_T_LOGO_END - 1}:d=1:alpha=1[logo_ov]"
            )
            steps.append(
                f"{current_v}[logo_ov]overlay=(W-w)/2:{_Y_HIGH}:"
                f"enable='between(t,0,{_T_LOGO_END})'[v1]"
            )
            current_v = "[v1]"
            idx += 1

        steps.append(
            f"[1:v]scale={_SPINNER_SZ}:{_SPINNER_SZ},"
            f"format=rgba,"
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

        if assets.artist:
            steps.append(
                f"[{idx}:v]scale={_PHOTO_SZ}:-1,"
                f"pad=iw+{_BORDER_PX*2}:ih+{_BORDER_PX*2}:{_BORDER_PX}:{_BORDER_PX}:white,"
                f"format=rgba,"
                f"W=iw:H=ih,"
                f"geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':"
                f"a='if(lte(pow(X-{_CORNER_R},2)+pow(Y-{_CORNER_R},2),pow({_CORNER_R},2))"
                f"*lt(X,{_CORNER_R})*lt(Y,{_CORNER_R})+"
                f"lte(pow(X-(W-{_CORNER_R}),2)+pow(Y-{_CORNER_R},2),pow({_CORNER_R},2))"
                f"*gt(X,W-{_CORNER_R})*lt(Y,{_CORNER_R})+"
                f"lte(pow(X-{_CORNER_R},2)+pow(Y-(H-{_CORNER_R}),2),pow({_CORNER_R},2))"
                f"*lt(X,{_CORNER_R})*gt(Y,H-{_CORNER_R})+"
                f"lte(pow(X-(W-{_CORNER_R}),2)+pow(Y-(H-{_CORNER_R}),2),pow({_CORNER_R},2))"
                f"*gt(X,W-{_CORNER_R})*gt(Y,H-{_CORNER_R})+"
                f"between(X,{_CORNER_R},W-{_CORNER_R})*between(Y,{_CORNER_R},H-{_CORNER_R})"
                f",255,0)',"
                f"fade=t=in:st={t_art_start}:d=1:alpha=1,"
                f"fade=t=out:st={duration - _T_END_GAP - 1}:d=1:alpha=1[artist_ov]"
            )
            steps.append(
                f"{current_v}[artist_ov]overlay=(W-w)/2:{_Y_HIGH}:"
                f"enable='between(t,{t_art_start},{duration})'[v3]"
            )
            current_v = "[v3]"

        graph = ";".join(steps)
        return graph + ";" + self._drawtext_pro(assets, current_v, duration)

    def _drawtext_pro(
        self,
        assets: "MediaAssets",
        link_in: str,
        duration: float,
        t_text_start: float = _T_TEXT_START,
    ) -> str:
        if not self.has_drawtext():
            return f"{link_in}null[v]"

        title  = self._escape_drawtext(self._wrap_text(assets.track_title, width=28, max_lines=2))
        artist = self._escape_drawtext(self._wrap_text(assets.artist_name, width=26, max_lines=2))

        t_end = duration - 1.5
        f_dur = 1.0

        alpha_title  = self.get_fade_alpha(t_text_start, t_end, f_dur)
        alpha_artist = self.get_fade_alpha(t_text_start + 1.2, t_end, f_dur)

        return (
            f"{link_in}"
            f"drawtext=text='{title}':fontcolor=white:fontsize=90"
            f":x=(w-text_w)/2:y={_Y_TITLE}"
            f":enable='gt(t,{t_text_start})':alpha='{alpha_title}',"
            f"drawtext=text='{artist}':fontcolor=0x00E5FF:fontsize=60"
            f":x=(w-text_w)/2:y={_Y_ARTIST}"
            f":enable='gt(t,{t_text_start + 1.2})':alpha='{alpha_artist}'"
            f"[v]"
        )
