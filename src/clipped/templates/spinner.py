from __future__ import annotations
from .base import VideoTemplate, TemplateInfo
from .polish import bg_cover, solid, square, circle, readable
from ..utils import MediaAssets

class SpinnerTemplate(VideoTemplate):
    info = TemplateInfo(
        name="spinner",
        label="Spinner Story",
        description="Square album-art spinner with staged reveal and readable lower card.",
        aspect=(1080, 1080),
        ideal_for=["Instagram Feed", "Archive", "Twitter/X"],
    )

    def get_inputs(self, assets: MediaAssets) -> list[str]:
        inputs = [str(assets.audio_path)]
        if assets.cover:
            inputs.append(str(assets.cover))
        return inputs

    def get_filter_graph(self, assets: MediaAssets, duration: float) -> str:
        speed = self.config.get("spinner_speed", 0.55)

        if not assets.cover:
            graph = solid(1080, 1080, "outv")
            return graph + ";" + self._text(assets, 1.0, duration)

        t_spin = 0.5
        t_text = min(2.8, max(1.1, duration * 0.2))
        t_reveal = min(max(4.0, duration * 0.68), max(4.0, duration - 1.4))

        steps = [
            bg_cover(1, 1080, 1080, "bg", 36, -0.38, 0.58),
            circle(1, 620, speed, "disc_raw"),
            "[disc_raw]fade=t=in:st=0.5:d=0.8:alpha=1,fade=t=out:st=%s:d=0.9:alpha=1[disc]" % t_reveal,
            "[bg][disc]overlay=(W-w)/2:105:enable='between(t,%s,%s)'[v1]" % (t_spin, t_reveal + 0.9),
            square(1, 650, "cover_raw"),
            "[cover_raw]fade=t=in:st=%s:d=0.9:alpha=1[cover]" % t_reveal,
            "[v1][cover]overlay=(W-w)/2:95:enable='gte(t,%s)'[outv]" % t_reveal,
        ]

        return ";".join(steps) + ";" + self._text(assets, t_text, duration)

    def _text(self, assets, start, end, link_in="[outv]", link_out="[v]"):
        if not self.has_drawtext():
            return f"{link_in}null{link_out}"

        title = self._wrap_text(assets.track_title, 24, 2)
        artist = self._wrap_text(assets.artist_name, 26, 1)
        title_src = self._drawtext_source(title, "title")
        artist_src = self._drawtext_source(artist, "artist")
        lines = self._line_count(title)
        y = int(790 - ((lines - 1) * 56))
        common = readable(self)

        return (
            f"{link_in}"
            f"drawtext={title_src}:fontcolor=white:fontsize=54{common}:x=(w-text_w)/2:y={y}:enable='between(t,{start},{end})':alpha='{self.get_fade_alpha(start,end,0.9)}',"
            f"drawtext={artist_src}:fontcolor=0xC8C8C8:fontsize=34{common}:x=(w-text_w)/2:y=920:enable='between(t,{start+0.45},{end})':alpha='{self.get_fade_alpha(start+0.45,end,0.9)}'"
            f"{link_out}"
        )
