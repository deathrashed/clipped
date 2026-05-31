from __future__ import annotations
from .base import VideoTemplate, TemplateInfo
from .polish import bg_cover, solid, square, readable, year, genre
from ..utils import MediaAssets

class FadePremiumTemplate(VideoTemplate):
    info = TemplateInfo(
        name="fade_premium",
        label="Fade Premium",
        description="Logo/artist/album sequence with album cover as final hero image.",
        aspect=(1080,1080),
        ideal_for=["Instagram Feed", "Archive"],
    )

    def get_inputs(self, assets: MediaAssets) -> list[str]:
        inputs = [str(assets.audio_path)]
        if assets.logo:
            inputs.append(str(assets.logo))
        if assets.artist:
            inputs.append(str(assets.artist))
        if assets.cover:
            inputs.append(str(assets.cover))
        return inputs

    def get_filter_graph(self, assets: MediaAssets, duration: float) -> str:
        idx = 1
        logo_idx = idx if assets.logo else None
        if assets.logo: idx += 1
        artist_idx = idx if assets.artist else None
        if assets.artist: idx += 1
        cover_idx = idx if assets.cover else None

        if cover_idx:
            steps = [bg_cover(cover_idx,1080,1080,"bg",36,-0.40,0.58)]
        else:
            steps = [solid(1080,1080,"bg")]

        current = "bg"

        if logo_idx:
            steps.append(
                f"[{logo_idx}:v]scale=720:260:force_original_aspect_ratio=decrease,format=rgba,"
                f"fade=t=in:st=0.4:d=0.7:alpha=1,fade=t=out:st=2.8:d=0.7:alpha=1[logo]"
            )
            steps.append(f"[{current}][logo]overlay=(W-w)/2:145[v1]")
            current = "v1"

        if artist_idx:
            steps.append(
                f"[{artist_idx}:v]scale=760:430:force_original_aspect_ratio=increase,crop=760:430,"
                f"format=rgba,fade=t=in:st=3.0:d=0.8:alpha=1,fade=t=out:st=5.4:d=0.8:alpha=1[artistimg]"
            )
            steps.append(f"[{current}][artistimg]overlay=(W-w)/2:130[v2]")
            current = "v2"

        if cover_idx:
            steps.append(square(cover_idx,620,"cover_raw"))
            steps.append("[cover_raw]fade=t=in:st=5.6:d=0.9:alpha=1[cover]")
            steps.append(f"[{current}][cover]overlay=(W-w)/2:90[outv]")
        else:
            steps.append(f"[{current}]null[outv]")

        return ";".join(steps) + ";" + self._text(assets, 2.8, duration)

    def _text(self, assets, start, end, link_in="[outv]", link_out="[v]"):
        if not self.has_drawtext():
            return f"{link_in}null{link_out}"

        title = self._wrap_text(assets.track_title, 24, 2)
        artist = self._wrap_text(assets.artist_name, 26, 1)
        detail = " · ".join(x for x in [year(assets), genre(assets)] if x)

        title_src = self._drawtext_source(title, "title")
        artist_src = self._drawtext_source(artist, "artist")
        detail_src = self._drawtext_source(detail, "detail")
        common = readable(self)
        lines = self._line_count(title)
        y = int(735 - ((lines - 1) * 54))

        return (
            f"{link_in}"
            f"drawtext={title_src}:fontcolor=white:fontsize=52{common}:x=(w-text_w)/2:y={y}:enable='between(t,{start},{end})':alpha='{self.get_fade_alpha(start,end,0.8)}',"
            f"drawtext={artist_src}:fontcolor=0xD0D0D0:fontsize=34{common}:x=(w-text_w)/2:y=870:enable='between(t,{start+0.4},{end})':alpha='{self.get_fade_alpha(start+0.4,end,0.8)}',"
            f"drawtext={detail_src}:fontcolor=0x9E9E9E:fontsize=24{common}:x=(w-text_w)/2:y=925:enable='between(t,{start+0.8},{end})':alpha='{self.get_fade_alpha(start+0.8,end,0.8)}'"
            f"{link_out}"
        )
