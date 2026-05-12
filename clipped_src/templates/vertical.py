"""
Vertical Spinner template — rotating record on a 9:16 canvas.
Output: 1080×1920. Ideal for Instagram Reels, TikTok, YouTube Shorts.

Layout:
  - Top 60%:  blurred + darkened album art as background fill
  - Centre:   crisp circular spinning record
  - Bottom:   metadata text overlays
"""
from __future__ import annotations
from .base import VideoTemplate, TemplateInfo
from ..utils import MediaAssets


class VerticalTemplate(VideoTemplate):
    info = TemplateInfo(
        name="vertical",
        label="Vertical Spinner (9:16 Reel)",
        description="Rotating record on a blurred background. Built for Reels & TikTok.",
        aspect=(1080, 1920),
        ideal_for=["Instagram Reels", "TikTok", "YouTube Shorts"],
    )

    def get_inputs(self, assets: MediaAssets) -> list[str]:
        inputs = [str(assets.audio_path)]
        if assets.cover:
            inputs.append(str(assets.cover))
        return inputs

    def get_filter_graph(self, assets: MediaAssets, duration: float) -> str:
        # Load from config
        speed = self.config.get("vertical_spinner_speed", 0.5)
        reveal_start = self.config.get("vertical_reveal_start_percent", 0.82)
        f_dur = self.config.get("vertical_transition_duration", 2.0)
        
        t_out = duration * reveal_start
        
        # Background: scaled, cropped, blurred, dimmed
        bg = (
            f"[1:v]scale=1080:1920:force_original_aspect_ratio=increase,"
            f"crop=1080:1920,gblur=sigma=30,eq=brightness=-0.25[bg];"
        )
        if assets.cover:
            # 1. Spinner (Circular, Rotating, Fades OUT at t_out)
            fg_spinner = (
                "[1:v]scale=720:720[art_circle];"
                "[art_circle]format=rgba,"
                "geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':"
                f"a='if(lte(pow(X-W/2,2)+pow(Y-H/2,2),pow(W/2,2)),255,0)'[fg_circle];"
                f"[fg_circle]rotate=t*{speed}:c=none,"
                f"fade=t=out:st={t_out}:d={f_dur}:alpha=1[fr];"
            )
            
            # 2. Square Cover (Full, Non-Rotating, Fades IN at t_out)
            fg_square = (
                "[1:v]scale=900:900[art_square];"
                "[art_square]format=rgba,"
                f"fade=t=in:st={t_out}:d={f_dur}:alpha=1[sq];"
            )

            # Compose: Base -> Overlay Spinner -> Overlay Square
            compose = (
                f"[bg][fr]overlay=(W-w)/2:(H-h)/2-200[v_spinner];"
                f"[v_spinner][sq]overlay=(W-w)/2:(H-h)/2-200[outv]"
            )
            graph = bg + fg_spinner + fg_square + compose
        else:
            graph = "color=s=1080x1920:c=black[outv]"

        return graph + ";" + self._drawtext_overlay(assets, duration, t_out, link_in="[outv]")

    def _drawtext_overlay(self, assets: "MediaAssets", duration: float, t_out_video: float, link_in: str = "[outv]", link_out: str = "[v]") -> str:
        """Override: show only Track Title and Band Name under the spinner."""
        if not self.has_drawtext():
            return f"{link_in}null{link_out}"

        # Load from config
        t_in_p    = self.config.get("vertical_text_in_percent", 0.25)
        f_dur     = self.config.get("vertical_text_fade_duration", 1.0)
        overlap   = self.config.get("vertical_text_reveal_overlap", 1.0)

        # Aggressive cleanup: strip quotes and leading/trailing whitespace
        title  = assets.track_title.strip().strip('"').strip("'")
        artist = assets.artist_name.strip().strip('"').strip("'")
        
        title_esc  = self._escape(title)
        artist_esc = self._escape(artist)

        # Timing: In at configured percentage, Out at reveal + overlap
        t_text_start = duration * t_in_p
        t_end = t_out_video + overlap
        
        # Track Fade (starts at t_text_start)
        alpha_title = self.get_fade_alpha(t_text_start, t_end, f_dur)
        
        # Artist Fade (starts shortly later)
        alpha_artist = self.get_fade_alpha(t_text_start + 1.2, t_end, f_dur)

        # Using white for both, increased contrast, and expansion=none for safety
        return (
            f"{link_in}"
            f"drawtext=text={title_esc}:fontcolor=white:fontsize=85:expansion=none"
            f":x=(w-text_w)/2:y=1280:alpha='{alpha_title}',"
            f"drawtext=text={artist_esc}:fontcolor=white:fontsize=60:expansion=none"
            f":x=(w-text_w)/2:y=1400:alpha='{alpha_artist}'"
            f"{link_out}"
        )
