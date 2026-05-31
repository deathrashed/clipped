from __future__ import annotations
from .base import VideoTemplate, TemplateInfo
from .polish import bg_cover, solid, square, readable, year, genre
from ..utils import MediaAssets

class NeonPulseTemplate(VideoTemplate):
    info = TemplateInfo(
        name="neon_pulse",
        label="Neon Pulse",
        description="Animated glow, waveform accent, album cover reveal, and compact metadata.",
        aspect=(1080,1920),
        ideal_for=["EDM", "Metal", "Reels", "TikTok"],
    )

    def get_inputs(self, assets: MediaAssets) -> list[str]:
        inputs = [str(assets.audio_path)]
        if assets.cover:
            inputs.append(str(assets.cover))
        return inputs

    def get_filter_graph(self, assets: MediaAssets, duration: float) -> str:
        if not assets.cover:
            base = solid(1080,1920,"v1")
        else:
            base = ";".join([
                bg_cover(1,1080,1920,"bg",54,-0.44,0.95),
                square(1,760,"art_raw"),
                "[art_raw]scale=w='760+18*sin(t*2.8)':h='760+18*sin(t*2.8)':eval=frame[art_p]",
                "[art_p]gblur=sigma=22,colorchannelmixer=aa=0.55[glow]",
                "[bg][glow]overlay=(W-w)/2:330[v0]",
                "[v0][art_p]overlay=(W-w)/2:350[v1]",
            ])

        steps = [base]
        steps.append(
            "[0:a]aformat=channel_layouts=mono,"
            "showwaves=s=900x180:mode=cline:rate=30:colors=0x00E5FFFF,"
            "format=rgba,colorkey=0x000000:0.25:0.12,gblur=sigma=1,"
            "fade=t=in:st=1.5:d=0.8:alpha=1[wave]"
        )
        steps.append("[v1][wave]overlay=(W-w)/2:1180[outv]")
        return ";".join(steps) + ";" + self._text(assets, 1.8, duration)

    def _text(self, assets, start, end, link_in="[outv]", link_out="[v]"):
        if not self.has_drawtext():
            return f"{link_in}null{link_out}"

        title = self._wrap_text(assets.track_title, 23, 2)
        artist = self._wrap_text(assets.artist_name, 25, 1)
        detail = " · ".join(x for x in [year(assets), genre(assets)] if x)

        title_src = self._drawtext_source(title, "title")
        artist_src = self._drawtext_source(artist, "artist")
        detail_src = self._drawtext_source(detail, "detail")
        lines = self._line_count(title)
        y = int(1345 - ((lines - 1) * 62))
        common = readable(self)

        return (
            f"{link_in}"
            f"drawtext={title_src}:fontcolor=0x00E5FF:fontsize=62{common}:x=(w-text_w)/2:y={y}:enable='between(t,{start},{end})':alpha='{self.get_fade_alpha(start,end,1)}',"
            f"drawtext={artist_src}:fontcolor=white:fontsize=42{common}:x=(w-text_w)/2:y=1495:enable='between(t,{start+0.35},{end})':alpha='{self.get_fade_alpha(start+0.35,end,1)}',"
            f"drawtext={detail_src}:fontcolor=0xAEEFFF:fontsize=28{common}:x=(w-text_w)/2:y=1565:enable='between(t,{start+0.7},{end})':alpha='{self.get_fade_alpha(start+0.7,end,1)}'"
            f"{link_out}"
        )
