from __future__ import annotations
from .base import VideoTemplate, TemplateInfo
from .polish import solid, readable, year, genre
from ..utils import MediaAssets

class CinematicTemplate(VideoTemplate):
    info = TemplateInfo(
        name="cinematic",
        label="Cinematic",
        description="Real cinematic crop with slow zoom, dark lower band and staged lower-third.",
        aspect=(1920,1080),
        ideal_for=["YouTube", "Archive", "Promos"],
    )

    def get_inputs(self, assets: MediaAssets) -> list[str]:
        inputs = [str(assets.audio_path)]
        if assets.cover:
            inputs.append(str(assets.cover))
        return inputs

    def get_filter_graph(self, assets: MediaAssets, duration: float) -> str:
        if assets.cover:
            frames = max(150, int(duration * 25))
            graph = (
                f"[1:v]scale=2160:2160:force_original_aspect_ratio=increase,crop=2160:2160,"
                f"zoompan=z='min(zoom+0.00016,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                f"d={frames}:s=1920x1080:fps=25,eq=brightness=-0.08:saturation=0.9[scene];"
                f"color=s=1920x230:c=black@0.72,format=rgba[band];"
                f"[scene][band]overlay=0:850[outv]"
            )
        else:
            graph = solid(1920,1080,"outv")
        return graph + ";" + self._text(assets, 1.0, duration)

    def _text(self, assets, start, end, link_in="[outv]", link_out="[v]"):
        if not self.has_drawtext():
            return f"{link_in}null{link_out}"

        title = self._wrap_text(assets.track_title, 40, 2)
        artist = self._wrap_text(assets.artist_name, 35, 1)
        detail = " · ".join(x for x in [getattr(assets, "album_name", ""), year(assets), genre(assets)] if x)

        title_src = self._drawtext_source(title, "title")
        artist_src = self._drawtext_source(artist, "artist")
        detail_src = self._drawtext_source(detail, "detail")
        common = readable(self, "left")

        return (
            f"{link_in}"
            f"drawtext={title_src}:fontcolor=white:fontsize=52{common}:x=90:y=875:enable='between(t,{start},{end})':alpha='{self.get_fade_alpha(start,end,1)}',"
            f"drawtext={artist_src}:fontcolor=0xD0D0D0:fontsize=34{common}:x=92:y=970:enable='between(t,{start+0.35},{end})':alpha='{self.get_fade_alpha(start+0.35,end,1)}',"
            f"drawtext={detail_src}:fontcolor=0x999999:fontsize=26{common}:x=92:y=1020:enable='between(t,{start+0.7},{end})':alpha='{self.get_fade_alpha(start+0.7,end,1)}'"
            f"{link_out}"
        )
