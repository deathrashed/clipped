"""
Dynamic Reel template — Vertical (9:16) with a sequential story:
1. Logo fade in/out
2. Large Spinning Record (high position) - stays until Artist stage
3. Artist Photo (Professional Subtle Border, 75% start) 
4. Professional Typography (Helvetica Neue) starting during Spinner stage
"""
from __future__ import annotations
from .base import VideoTemplate, TemplateInfo
from ..utils import MediaAssets

class ReelTemplate(VideoTemplate):
    info = TemplateInfo(
        name="reel",
        label="Dynamic Reel (Logo -> Spinner -> Artist)",
        description="Sequential story with large spinner and professional typography.",
        aspect=(1080, 1920),
        ideal_for=["Instagram Reels", "TikTok", "YouTube Shorts"],
    )

    def get_inputs(self, assets: MediaAssets) -> list[str]:
        inputs = [str(assets.audio_path)]
        # Input 1: Background/Cover
        inputs.append(str(assets.cover))
        # Input 2: Logo
        if assets.logo:
            inputs.append(str(assets.logo))
        # Input 3: Artist
        if assets.artist:
            inputs.append(str(assets.artist))
        return inputs

    def get_filter_graph(self, assets: MediaAssets, duration: float) -> str:
        speed = self.config.get("spinner_speed", 0.5)
        steps: list[str] = []
        
        # ── 1. Background (Blurred Always) ────────────────────────────────────
        steps.append(
            f"[1:v]scale=1080:1920:force_original_aspect_ratio=increase,"
            f"crop=1080:1920,"
            f"gblur=sigma=60,"
            f"eq=brightness=-0.3:saturation=0.8[bg]"
        )

        current_v = "[bg]"
        idx = 2
        
        # Timing
        t_logo_end   = 5.0
        t_art_start  = duration * 0.75
        t_spin_start = 5.0
        t_spin_end   = t_art_start + 0.5 # Small overlap for continuity
        t_text_start = 7.0
        t_end_gap    = 2.0
        
        # High position for all overlays
        y_high = 350
        
        # --- Stage 1: Logo ---
        if assets.logo:
            steps.append(
                f"[{idx}:v]scale=900:-1,"
                f"fade=t=in:st=0:d=1:alpha=1,"
                f"fade=t=out:st={t_logo_end-1}:d=1:alpha=1[logo_ov]"
            )
            steps.append(f"{current_v}[logo_ov]overlay=(W-w)/2:{y_high}:enable='between(t,0,{t_logo_end})'[v1]")
            current_v = "[v1]"
            idx += 1

        # --- Stage 2: Large Spinning Record ---
        # Increased size to 850
        steps.append(
            f"[1:v]scale=850:850,"
            f"format=rgba,"
            f"geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':"
            f"a='if(lte(pow(X-W/2,2)+pow(Y-H/2,2),pow(W/2,2)),255,0)',"
            f"rotate=t*{speed}:c=none,"
            f"fade=t=in:st={t_spin_start}:d=1:alpha=1,"
            f"fade=t=out:st={t_spin_end-1}:d=1:alpha=1[spinner_ov]"
        )
        steps.append(f"{current_v}[spinner_ov]overlay=(W-w)/2:{y_high}:enable='between(t,{t_spin_start},{t_spin_end})'[v2]")
        current_v = "[v2]"

        # --- Stage 3: Artist Photo (Professional Subtle Border) ---
        if assets.artist:
            # Subtle corner radius (8px - sharper look)
            R = 8
            steps.append(
                f"[{idx}:v]scale=950:-1," # Slightly larger photo
                f"pad=iw+10:ih+10:5:5:white," # 5px white border
                f"format=rgba,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':"
                f"a='if(lte(pow(X-{R},2)+pow(Y-{R},2),pow({R},2))*lt(X,{R})*lt(Y,{R})+"
                f"lte(pow(X-(W-{R}),2)+pow(Y-{R},2),pow({R},2))*gt(X,W-{R})*lt(Y,{R})+"
                f"lte(pow(X-{R},2)+pow(Y-(H-{R}),2),pow({R},2))*lt(X,{R})*gt(Y,H-{R})+"
                f"lte(pow(X-(W-{R}),2)+pow(Y-(H-{R}),2),pow({R},2))*gt(X,W-{R})*gt(Y,H-{R})+"
                f"between(X,{R},W-{R})+between(Y,{R},H-{R}),255,0)',"
                f"fade=t=in:st={t_art_start}:d=1:alpha=1,"
                f"fade=t=out:st={duration-t_end_gap-1}:d=1:alpha=1[artist_ov]"
            )
            steps.append(f"{current_v}[artist_ov]overlay=(W-w)/2:{y_high}:enable='between(t,{t_art_start},{duration})'[v3]")
            current_v = "[v3]"

        graph = ";".join(steps)
        return graph + ";" + self._drawtext_professional_overlay(assets, duration, current_v, t_text_start)

    def _drawtext_professional_overlay(self, assets: "MediaAssets", duration: float, link_in: str, t_text_start: float) -> str:
        if not self.has_drawtext():
            return f"{link_in}null[v]"

        title  = self._escape(assets.track_title)
        artist = self._escape(assets.artist_name)
        
        t_end = duration - 1.5
        f_dur = 1.0
        
        # Professional Typography: Helvetica Neue (escaped space) with subtle shadow
        font_style = "font=Helvetica\\ Neue:shadowcolor=black@0.5:shadowx=2:shadowy=2"
        
        # Track Fade (starts at t_text_start)
        alpha_title = self.get_fade_alpha(t_text_start, t_end, f_dur)
        
        # Artist Fade (starts shortly later)
        alpha_artist = self.get_fade_alpha(t_text_start + 1.2, t_end, f_dur)

        return (
            f"{link_in}"
            f"drawtext=text={title}:fontcolor=white:fontsize=90:{font_style}"
            f":x=(w-text_w)/2:y=1250:enable='gt(t,{t_text_start})':alpha='{alpha_title}',"
            f"drawtext=text={artist}:fontcolor=0x00E5FF:fontsize=60:{font_style}"
            f":x=(w-text_w)/2:y=1365:enable='gt(t,{t_artist_fade})':alpha='{alpha_artist}'"
            f"[v]"
        )
