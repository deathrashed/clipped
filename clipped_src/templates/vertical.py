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

        if assets.cover:
            # Background: fill 1080×1920 with blurred, darkened artwork
            bg = (
                "[1:v]scale=1080:1920:force_original_aspect_ratio=increase,"
                "crop=1080:1920,"
                "gblur=sigma=30,"
                "eq=brightness=-0.25[bg];"
            )
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

        return graph + ";" + self._drawtext_overlay(assets)

    def _drawtext_overlay(self, assets: "MediaAssets", link_in: str = "[outv]", link_out: str = "[v]") -> str:
        """Override: push text lower on the tall canvas."""
        if not self.has_drawtext():
            return f"{link_in}null{link_out}"

        title  = self._escape(assets.track_title)
        artist = self._escape(assets.artist_name)
        album  = self._escape(assets.album_name)

        # Position text in the lower quarter of the 1920-high canvas
        return (
            f"{link_in}"
            f"drawtext=text='{title}':fontcolor=white:fontsize=70"
            f":x=(w-text_w)/2:y=1540:enable='gt(t,1)':alpha='if(lt(t,2),t-1,1)',"
            f"drawtext=text='{artist}':fontcolor=0xCCCCCC:fontsize=50"
            f":x=(w-text_w)/2:y=1630:enable='gt(t,1.5)':alpha='if(lt(t,2.5),t-1.5,1)',"
            f"drawtext=text='{album}':fontcolor=0x999999:fontsize=38:fontstyle=italic"
            f":x=(w-text_w)/2:y=1705:enable='gt(t,2)':alpha='if(lt(t,3),t-2,1)'"
            f"{link_out}"
        )
