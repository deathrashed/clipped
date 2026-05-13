"""
Minimal template — dark gradient background with large centered artwork + text.
Output: 1080×1080. Clean, typographic, editorial feel.

Layout:
  - Full-canvas dark gradient background
  - Album art: centred, ~600px, with subtle drop shadow via pad+overlay
  - Bold metadata beneath the artwork
"""
from __future__ import annotations
from .base import VideoTemplate, TemplateInfo
from ..utils import MediaAssets


class MinimalTemplate(VideoTemplate):
    info = TemplateInfo(
        name="minimal",
        label="Minimal (Dark Typographic)",
        description="Dark gradient canvas with centered artwork and clean typography.",
        aspect=(1080, 1080),
        ideal_for=["Twitter/X", "Archive", "Bandcamp"],
    )

    def get_inputs(self, assets: MediaAssets) -> list[str]:
        inputs = [str(assets.audio_path)]
        if assets.cover:
            inputs.append(str(assets.cover))
        return inputs

    def get_filter_graph(self, assets: MediaAssets, duration: float) -> str:
        if assets.cover:
            graph = (
                # Dark gradient background (very dark charcoal → black)
                "color=s=1080x1080:c=#111111[bg_base];"
                "[bg_base]geq="
                "r='lerp(17,0,(Y/H))':g='lerp(17,0,(Y/H))':b='lerp(20,0,(Y/H))'[bg];"
                # Album art: scale to 580px, centre horizontally at y=160
                "[1:v]scale=580:580:force_original_aspect_ratio=decrease,"
                "pad=580:580:(ow-iw)/2:(oh-ih)/2,format=rgba[art];"
                # Subtle vignette on art: radial darkening at edges
                "[art]geq="
                "r='r(X,Y)*max(0,1-0.5*sqrt(pow((X-290)/290,2)+pow((Y-290)/290,2)))':g='g(X,Y)*max(0,1-0.5*sqrt(pow((X-290)/290,2)+pow((Y-290)/290,2)))':b='b(X,Y)*max(0,1-0.5*sqrt(pow((X-290)/290,2)+pow((Y-290)/290,2)))':a='a(X,Y)'[art_v];"
                # Compose art onto background at (250, 140)
                "[bg][art_v]overlay=250:140[outv]"
            )
        else:
            graph = "color=s=1080x1080:c=#0d0d0d[outv]"

        return graph + ";" + self._drawtext_overlay(assets)

    def _drawtext_overlay(self, assets: "MediaAssets", link_in: str = "[outv]", link_out: str = "[v]") -> str:
        """Override: position text below the centred artwork."""
        if not self.has_drawtext():
            return f"{link_in}null{link_out}"

        title  = self._wrap_text(assets.track_title, width=28, max_lines=2)
        artist = self._wrap_text(assets.artist_name, width=26, max_lines=1)
        album  = self._wrap_text(assets.album_name, width=28, max_lines=1)

        title_src  = self._drawtext_source(title, prefix="title")
        artist_src = self._drawtext_source(artist, prefix="artist")
        album_src  = self._drawtext_source(album, prefix="album")

        return (
            f"{link_in}"
            f"drawtext={title_src}:fontcolor=white:fontsize=64:fontweight=bold"
            f":x=(w-text_w)/2:y=780:enable='gt(t,0.5)':alpha='if(lt(t,1.5),t-0.5,1)',"
            f"drawtext={artist_src}:fontcolor=0xBBBBBB:fontsize=42"
            f":x=(w-text_w)/2:y=860:enable='gt(t,1)':alpha='if(lt(t,2),t-1,1)',"
            f"drawtext={album_src}:fontcolor=0x777777:fontsize=32:fontstyle=italic"
            f":x=(w-text_w)/2:y=915:enable='gt(t,1.5)':alpha='if(lt(t,2.5),t-1.5,1)'"
            f"{link_out}"
        )
