from __future__ import annotations
from .base import VideoTemplate, TemplateInfo
from .polish import bg_cover, solid, square, circle, readable, year, genre
from ..utils import MediaAssets

class VinylSleeveTemplate(VideoTemplate):
    info = TemplateInfo(
        name="vinyl_sleeve",
        label="Vinyl Sleeve",
        description="Album cover sleeve with spinning record reveal. Uses album art, not artist image.",
        aspect=(1080, 1920),
        ideal_for=["Reels", "TikTok", "Music promos"],
    )

    def get_inputs(self, assets: MediaAssets) -> list[str]:
        inputs = [str(assets.audio_path)]
        if assets.cover:
            inputs.append(str(assets.cover))
        return inputs

    def get_filter_graph(self, assets: MediaAssets, duration: float) -> str:
        if not assets.cover:
            return solid(1080, 1920, "outv") + ";" + self._text(assets, 1, duration)

        speed = self.config.get("vinyl_speed", 0.75)
        steps = [
            bg_cover(1,1080,1920,"bg",46,-0.38,0.64),
            circle(1,760,speed,"disc_raw"),
            square(1,760,"sleeve_raw"),
            "[disc_raw]fade=t=in:st=0.6:d=0.8:alpha=1[disc]",
            "[sleeve_raw]fade=t=in:st=1.0:d=0.8:alpha=1[sleeve]",
            "[bg][disc]overlay=x='120+min(max(t-1.2,0)*95,190)':y=350[v1]",
            "[v1][sleeve]overlay=x='90-min(max(t-2.2,0)*12,30)':y=350[outv]",
        ]
        return ";".join(steps) + ";" + self._text(assets, 2.2, duration)

    def _text(self, assets, start, end, link_in="[outv]", link_out="[v]"):
        if not self.has_drawtext():
            return f"{link_in}null{link_out}"

        title = self._wrap_text(assets.track_title, 24, 2)
        artist = self._wrap_text(assets.artist_name, 26, 1)
        detail = " · ".join(x for x in [year(assets), genre(assets)] if x)

        title_src = self._drawtext_source(title, "title")
        artist_src = self._drawtext_source(artist, "artist")
        detail_src = self._drawtext_source(detail, "detail")
        lines = self._line_count(title)
        y = int(1240 - ((lines - 1) * 68))
        common = readable(self)

        return (
            f"{link_in}"
            f"drawtext={title_src}:fontcolor=white:fontsize=66{common}:x=(w-text_w)/2:y={y}:enable='between(t,{start},{end})':alpha='{self.get_fade_alpha(start,end,1)}',"
            f"drawtext={artist_src}:fontcolor=0xCFCFCF:fontsize=44{common}:x=(w-text_w)/2:y=1415:enable='between(t,{start+0.4},{end})':alpha='{self.get_fade_alpha(start+0.4,end,1)}',"
            f"drawtext={detail_src}:fontcolor=0x9E9E9E:fontsize=30{common}:x=(w-text_w)/2:y=1495:enable='between(t,{start+0.8},{end})':alpha='{self.get_fade_alpha(start+0.8,end,1)}'"
            f"{link_out}"
        )
