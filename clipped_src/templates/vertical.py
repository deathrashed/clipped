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
        speed = self.config.get("spinner_speed", 0.5)
        # Background: scaled, cropped, blurred, dimmed
        bg = (
            f"[1:v]scale=1080:1920:force_original_aspect_ratio=increase,"
            f"crop=1080:1920,gblur=sigma=30,eq=brightness=-0.25[bg];"
        )
        if assets.cover:
            # Foreground: circular spinner
            fg = (
                "[1:v]scale=720:720[art];"
                "[art]format=rgba,"
                "geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':"
                f"a='if(lte(pow(X-W/2,2)+pow(Y-H/2,2),pow(W/2,2)),255,0)'[fg];"
                f"[fg]rotate=t*{speed}:c=none[fr];"
            )
            # Compose: spinner centred at ~40% height
            compose = (
                "[bg][fr]overlay=(W-w)/2:(H-h)/2-200[outv]"
            )
            graph = bg + fg + compose
        else:
            graph = "color=s=1080x1920:c=black[outv]"

        return graph + ";" + self._drawtext_overlay(assets, duration)

    def _drawtext_overlay(self, assets: "MediaAssets", duration: float, link_in: str = "[outv]", link_out: str = "[v]") -> str:
        """Override: show only Track Title and Band Name under the spinner."""
        if not self.has_drawtext():
            return f"{link_in}null{link_out}"

        # Strip any literal quotes from metadata for a cleaner look
        title  = self._escape(assets.track_title.strip('"'))
        artist = self._escape(assets.artist_name.strip('"'))

        # Timing: 25% in, 75% out
        t_in  = duration * 0.25
        t_out = duration * 0.75
        f_dur = 1.0 # 1s fade duration
        
        # Robust fade expression: in at t_in, out at t_out
        def get_alpha(st):
            return (
                f"if(lt(t\\,{st})\\,0\\,"
                f"if(lt(t\\,{st+f_dur})\\,(t-{st})/{f_dur}\\,"
                f"if(lt(t\\,{t_out-f_dur})\\,1\\,"
                f"if(lt(t\\,{t_out})\\,1-(t-({t_out-f_dur}))/{f_dur}\\,0))))"
            )

        alpha_title  = get_alpha(t_in)
        alpha_artist = get_alpha(t_in + 0.5) # Slight stagger

        # Position text under the spinner (spinner bottom is at ~1120)
        # Using Track Title (White, Large) and Band Name (Cyan/Subdued, Medium)
        return (
            f"{link_in}"
            f"drawtext=text={title}:fontcolor=white:fontsize=85"
            f":x=(w-text_w)/2:y=1280:enable=between(t\\,{t_in}\\,{t_out}):alpha={alpha_title},"
            f"drawtext=text={artist}:fontcolor=0x00E5FF:fontsize=60"
            f":x=(w-text_w)/2:y=1400:enable=between(t\\,{t_in+0.5}\\,{t_out}):alpha={alpha_artist}"
            f"{link_out}"
        )
