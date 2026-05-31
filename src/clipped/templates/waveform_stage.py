from __future__ import annotations
from .base import VideoTemplate, TemplateInfo
from .polish import bg_cover, solid, square, readable, year, genre
from ..utils import MediaAssets

class WaveformStageTemplate(VideoTemplate):
    info = TemplateInfo(
        name="waveform_stage",
        label="Waveform Stage",
        description="Album cover plus real audio waveform hero and metadata.",
        aspect=(1080,1920),
        ideal_for=["Audio previews", "Reels", "TikTok"],
    )

    def get_inputs(self, assets: MediaAssets) -> list[str]:
        inputs = [str(assets.audio_path)]
        if assets.cover:
            inputs.append(str(assets.cover))
        return inputs

    def get_filter_graph(self, assets: MediaAssets, duration: float) -> str:
        if assets.cover:
            base = ";".join([
                bg_cover(1,1080,1920,"bg",52,-0.42,0.72),
                square(1,600,"cover"),
                "[cover]fade=t=in:st=1.1:d=0.9:alpha=1[cover_f]",
                "[bg][cover_f]overlay=(W-w)/2:930[v1]",
            ])
        else:
            base = solid(1080,1920,"v1")

        steps = [base]
        steps.append(
            "[0:a]aformat=channel_layouts=mono,"
            "showwaves=s=940x440:mode=p2p:rate=30:colors=0x00E5FFFF,"
            "format=rgba,colorkey=0x000000:0.25:0.12,gblur=sigma=1.1,"
            "fade=t=in:st=0.8:d=1:alpha=1[wave]"
        )
        steps.append(
            "[0:a]aformat=channel_layouts=mono,"
            "showwaves=s=940x440:mode=p2p:rate=30:colors=0x7A00FFFF,"
            "format=rgba,colorkey=0x000000:0.25:0.12,gblur=sigma=10,"
            "fade=t=in:st=0.8:d=1:alpha=1[glow]"
        )
        steps.append("[v1][glow]overlay=(W-w)/2:430[v2]")
        steps.append("[v2][wave]overlay=(W-w)/2:430[outv]")
        return ";".join(steps) + ";" + self._text(assets, 0.8, duration)

    def _text(self, assets, start, end, link_in="[outv]", link_out="[v]"):
        if not self.has_drawtext():
            return f"{link_in}null{link_out}"

        title = self._wrap_text(assets.track_title, 22, 2)
        artist = self._wrap_text(assets.artist_name, 24, 1)
        detail = " · ".join(x for x in [year(assets), genre(assets)] if x)

        title_src = self._drawtext_source(title, "title")
        artist_src = self._drawtext_source(artist, "artist")
        detail_src = self._drawtext_source(detail, "detail")
        common = readable(self)

        return (
            f"{link_in}"
            f"drawtext={title_src}:fontcolor=white:fontsize=64{common}:x=(w-text_w)/2:y=175:enable='between(t,{start},{end})':alpha='{self.get_fade_alpha(start,end,1)}',"
            f"drawtext={artist_src}:fontcolor=0xCFCFCF:fontsize=42{common}:x=(w-text_w)/2:y=330:enable='between(t,{start+0.3},{end})':alpha='{self.get_fade_alpha(start+0.3,end,1)}',"
            f"drawtext={detail_src}:fontcolor=0xAAAAAA:fontsize=28{common}:x=(w-text_w)/2:y=390:enable='between(t,{start+0.6},{end})':alpha='{self.get_fade_alpha(start+0.6,end,1)}'"
            f"{link_out}"
        )
