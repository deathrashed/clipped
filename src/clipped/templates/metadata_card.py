from __future__ import annotations
from .base import VideoTemplate, TemplateInfo
from .polish import bg_cover, solid, square, readable, year, genre
from ..utils import MediaAssets

class MetadataCardTemplate(VideoTemplate):
    info = TemplateInfo(
        name="metadata_card",
        label="Metadata Card",
        description="Detailed album-art card using title, artist, album, year and genre.",
        aspect=(1080,1920),
        ideal_for=["Archives", "Library previews", "Reels"],
    )

    def get_inputs(self, assets: MediaAssets) -> list[str]:
        inputs = [str(assets.audio_path)]
        if assets.cover:
            inputs.append(str(assets.cover))
        return inputs

    def get_filter_graph(self, assets: MediaAssets, duration: float) -> str:
        if assets.cover:
            graph = ";".join([
                bg_cover(1,1080,1920,"bg",48,-0.42,0.55),
                square(1,620,"cover"),
                "[cover]fade=t=in:st=0.7:d=0.9:alpha=1[cover_f]",
                "[bg][cover_f]overlay=80:255[outv]",
            ])
        else:
            graph = solid(1080,1920,"outv")
        return graph + ";" + self._text(assets, 1.2, duration)

    def _text(self, assets, start, end, link_in="[outv]", link_out="[v]"):
        if not self.has_drawtext():
            return f"{link_in}null{link_out}"

        album = getattr(assets, "album_name", "") or ""
        rows = [
            ("TRACK", assets.track_title),
            ("ARTIST", assets.artist_name),
            ("ALBUM", album),
            ("YEAR", year(assets)),
            ("GENRE", genre(assets)),
        ]

        common = readable(self, "left")
        out = link_in
        y = 960
        for i, (label, value) in enumerate(rows):
            if not value:
                continue
            label_src = self._drawtext_source(label, f"label{i}")
            value_src = self._drawtext_source(self._wrap_text(value, 26, 2), f"value{i}")
            st = start + i * 0.25
            out += (
                f"drawtext={label_src}:fontcolor=0x8E8E8E:fontsize=24{common}:x=80:y={y}:enable='between(t,{st},{end})':alpha='{self.get_fade_alpha(st,end,0.7)}',"
                f"drawtext={value_src}:fontcolor=white:fontsize={50 if i == 0 else 36}{common}:x=80:y={y+36}:enable='between(t,{st+0.1},{end})':alpha='{self.get_fade_alpha(st+0.1,end,0.7)}',"
            )
            y += 140 if i == 0 else 115

        return out.rstrip(",") + link_out
