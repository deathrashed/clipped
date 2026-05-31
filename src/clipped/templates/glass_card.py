from __future__ import annotations
from .base import VideoTemplate, TemplateInfo
from .polish import blurred_bg, fallback_bg, square_art, readable_common
from ..utils import MediaAssets

class GlassCardTemplate(VideoTemplate):
    info = TemplateInfo(
        name="glass_card",
        label="Glass Card",
        description="Apple Music-style frosted glass card with album art, title, and artist in a compact layout.",
        aspect=(1080, 1920),
        ideal_for=["Reels", "Stories"],
    )

    def get_inputs(self, assets: MediaAssets) -> list[str]:
        inputs = [str(assets.audio_path)]
        if assets.cover:
            inputs.append(str(assets.cover))
        if assets.logo:
            inputs.append(str(assets.logo))
        return inputs

    def get_filter_graph(self, assets: MediaAssets, duration: float) -> str:
        idx = 1
        cover_idx = idx if assets.cover else None
        if assets.cover: idx += 1
        logo_idx = idx if assets.logo else None

        steps = []
        if cover_idx:
            steps.append(blurred_bg(cover_idx, 1080, 1920, 55, -0.40, 0.55, "bg"))
        else:
            steps.append(fallback_bg(1080, 1920, "bg"))

        steps.append("color=s=960x540:c=black@0.35,format=rgba,"
                     "drawbox=x=0:y=0:w=960:h=540:color=white@0.10:t=fill,"
                     "gblur=sigma=8[card]")
        steps.append("[bg][card]overlay=(W-w)/2:(H-h)/2[v1]")

        if cover_idx:
            steps.append(square_art(cover_idx, 340, "art"))
            steps.append("[art]fade=t=in:st=0.5:d=1:alpha=1[art_f]")
            steps.append("[v1][art_f]overlay=(W-w)/2:615[v2]")
        else:
            steps.append("[v1]null[v2]")

        if logo_idx:
            steps.append(f"[{logo_idx}:v]scale=150:50:force_original_aspect_ratio=decrease,"
                         f"format=rgba,fade=t=in:st=0.8:d=0.8:alpha=1[logo_f]")
            steps.append("[v2][logo_f]overlay=(W-w)/2:905[v3]")
        else:
            steps.append("[v2]null[v3]")

        cur = "v3"
        return ";".join(steps) + ";" + self._text(assets, f"[{cur}]")

    def _text(self, assets, link_in="[v3]", link_out="[v]"):
        if not self.has_drawtext():
            return f"{link_in}null{link_out}"
        title = self._wrap_text(assets.track_title, 22, 2)
        artist = self._wrap_text(assets.artist_name, 26, 1)
        title_src = self._drawtext_source(title, "title")
        artist_src = self._drawtext_source(artist, "artist")
        common = readable_common(self)
        return (
            f"{link_in}"
            f"drawtext={title_src}:fontcolor=white:fontsize=46{common}:x=(w-text_w)/2:y=1010:enable='gt(t,1)':alpha='if(lt(t,2),t-1,1)',"
            f"drawtext={artist_src}:fontcolor=0xAAAAAA:fontsize=30{common}:x=(w-text_w)/2:y=1090:enable='gt(t,1.5)':alpha='if(lt(t,2.5),t-1.5,1)'"
            f"{link_out}"
        )
