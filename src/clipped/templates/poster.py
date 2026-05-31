from __future__ import annotations
from .base import VideoTemplate, TemplateInfo
from .polish import bg_cover, solid, square, readable, year, genre
from ..utils import MediaAssets

class PosterTemplate(VideoTemplate):
    info = TemplateInfo(
        name="poster",
        label="Concert Poster",
        description="Animated poster layout with album cover reveal and metadata.",
        aspect=(1080,1920),
        ideal_for=["Promos", "Stories", "Reels"],
    )

    def get_inputs(self, assets: MediaAssets) -> list[str]:
        inputs = [str(assets.audio_path)]
        if assets.cover:
            inputs.append(str(assets.cover))
        return inputs

    def get_filter_graph(self, assets: MediaAssets, duration: float) -> str:
        if assets.cover:
            graph = ";".join([
                bg_cover(1,1080,1920,"bg",38,-0.48,0.5),
                square(1,600,"cover_raw"),
                "[cover_raw]fade=t=in:st=1.4:d=0.9:alpha=1[cover]",
                "[bg][cover]overlay=x=(W-w)/2:y='790-min(max(t-1.4,0)*35,55)'[outv]",
            ])
        else:
            graph = solid(1080,1920,"outv")
        return graph + ";" + self._text(assets, 0.5, duration)

    def _text(self, assets, start, end, link_in="[outv]", link_out="[v]"):
        if not self.has_drawtext():
            return f"{link_in}null{link_out}"

        artist = self._wrap_text(assets.artist_name.upper(), 22, 1)
        title = self._wrap_text(assets.track_title.upper(), 16, 3)
        detail = " · ".join(x for x in [year(assets), genre(assets)] if x)

        artist_src = self._drawtext_source(artist, "artist")
        title_src = self._drawtext_source(title, "title")
        detail_src = self._drawtext_source(detail, "detail")
        common = readable(self)

        return (
            f"{link_in}"
            f"drawtext={artist_src}:fontcolor=0xCFCFCF:fontsize=38{common}:x=(w-text_w)/2:y=205:enable='between(t,{start},{end})':alpha='{self.get_fade_alpha(start,end,0.8)}',"
            f"drawtext={title_src}:fontcolor=white:fontsize=78{common}:x=(w-text_w)/2:y=280:enable='between(t,{start+0.35},{end})':alpha='{self.get_fade_alpha(start+0.35,end,0.8)}',"
            f"drawtext={detail_src}:fontcolor=0xAAAAAA:fontsize=30{common}:x=(w-text_w)/2:y=1495:enable='between(t,{start+1.4},{end})':alpha='{self.get_fade_alpha(start+1.4,end,0.8)}'"
            f"{link_out}"
        )
