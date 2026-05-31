from __future__ import annotations
from .base import VideoTemplate, TemplateInfo
from .polish import bg_cover, solid, square, readable, year, genre
from ..utils import MediaAssets

class ArtistFocusTemplate(VideoTemplate):
    info = TemplateInfo(
        name="artist_focus",
        label="Artist Focus",
        description="Artist image hero background, album cover card, logo, year and genre.",
        aspect=(1080,1920),
        ideal_for=["Artist promos", "Reels", "TikTok"],
    )

    def get_inputs(self, assets: MediaAssets) -> list[str]:
        inputs = [str(assets.audio_path)]
        if assets.artist:
            inputs.append(str(assets.artist))
        if assets.logo:
            inputs.append(str(assets.logo))
        if assets.cover:
            inputs.append(str(assets.cover))
        return inputs

    def get_filter_graph(self, assets: MediaAssets, duration: float) -> str:
        idx = 1
        artist_idx = idx if assets.artist else None
        if assets.artist: idx += 1
        logo_idx = idx if assets.logo else None
        if assets.logo: idx += 1
        cover_idx = idx if assets.cover else None

        steps = []

        if artist_idx:
            frames = max(150, int(duration * 25))
            steps.append(
                f"[{artist_idx}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
                f"zoompan=z='min(zoom+0.00014,1.08)':d={frames}:s=1080x1920:fps=25,"
                f"eq=brightness=-0.22:saturation=0.82[base]"
            )
        elif cover_idx:
            steps.append(bg_cover(cover_idx,1080,1920,"base",48,-0.38,0.65))
        else:
            steps.append(solid(1080,1920,"base"))

        cur = "base"

        if logo_idx:
            steps.append(
                f"[{logo_idx}:v]scale=700:250:force_original_aspect_ratio=decrease,format=rgba,"
                f"fade=t=in:st=0.8:d=1:alpha=1[logo]"
            )
            steps.append(f"[{cur}][logo]overlay=(W-w)/2:150[v1]")
            cur = "v1"

        if cover_idx:
            steps.append(square(cover_idx,360,"cover_raw"))
            steps.append("[cover_raw]fade=t=in:st=2.2:d=0.9:alpha=1[cover]")
            steps.append(f"[{cur}][cover]overlay=80:1250[outv]")
        else:
            steps.append(f"[{cur}]null[outv]")

        return ";".join(steps) + ";" + self._text(assets, 2.4, duration)

    def _text(self, assets, start, end, link_in="[outv]", link_out="[v]"):
        if not self.has_drawtext():
            return f"{link_in}null{link_out}"

        artist = self._wrap_text(assets.artist_name.upper(), 22, 1)
        title = self._wrap_text(assets.track_title, 22, 2)
        detail = " · ".join(x for x in [getattr(assets, "album_name", ""), year(assets), genre(assets)] if x)

        artist_src = self._drawtext_source(artist, "artist")
        title_src = self._drawtext_source(title, "title")
        detail_src = self._drawtext_source(detail, "detail")
        common = readable(self, "left")

        return (
            f"{link_in}"
            f"drawtext={artist_src}:fontcolor=0xD8D8D8:fontsize=30{common}:x=480:y=1265:enable='between(t,{start},{end})':alpha='{self.get_fade_alpha(start,end,0.8)}',"
            f"drawtext={title_src}:fontcolor=white:fontsize=52{common}:x=480:y=1310:enable='between(t,{start+0.3},{end})':alpha='{self.get_fade_alpha(start+0.3,end,0.8)}',"
            f"drawtext={detail_src}:fontcolor=0xBBBBBB:fontsize=26{common}:x=480:y=1445:enable='between(t,{start+0.6},{end})':alpha='{self.get_fade_alpha(start+0.6,end,0.8)}'"
            f"{link_out}"
        )
