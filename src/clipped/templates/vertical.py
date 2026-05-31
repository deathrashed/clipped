from __future__ import annotations
from .base import VideoTemplate, TemplateInfo
from .polish import blurred_bg, fallback_bg, circular_art, square_art, readable_common
from ..utils import MediaAssets

_W = 1080
_H = 1920
_SPINNER = 850
_COVER = 950
_ART_Y = 350
_TITLE_Y = 1380
_ARTIST_Y = 1495

class VerticalTemplate(VideoTemplate):
    info = TemplateInfo(
        name="vertical",
        label="Vertical Premium Spinner (9:16)",
        description="Polished Reel-style spinner with safe text and smooth album reveal.",
        aspect=(_W, _H),
        ideal_for=["Instagram Reels", "TikTok", "YouTube Shorts"],
    )

    def get_inputs(self, assets: MediaAssets) -> list[str]:
        inputs = [str(assets.audio_path)]
        if assets.cover:
            inputs.append(str(assets.cover))
        return inputs

    def get_filter_graph(self, assets: MediaAssets, duration: float) -> str:
        speed = self.config.get("vertical_spinner_speed", 0.7)
        cover_idx = 1 if assets.cover else None

        t_spin = min(1.0, max(0.4, duration * 0.08))
        t_text = min(7.0, max(2.5, duration * 0.35))
        t_reveal = max(t_text + 2.0, duration * 0.72)
        t_reveal = min(t_reveal, max(t_spin + 1.5, duration - 1.5))
        t_spin_end = t_reveal + 0.5
        t_text_end = max(t_reveal - 0.3, t_text + 1.5)

        steps = []

        if assets.cover:
            steps.append(blurred_bg(cover_idx, _W, _H, blur=40, brightness=-0.32, saturation=0.6, label="bg"))

            steps.append(circular_art(cover_idx, _SPINNER, speed, "spin_raw"))
            steps.append(
                f"[spin_raw]fade=t=in:st={t_spin}:d=1:alpha=1,"
                f"fade=t=out:st={t_reveal}:d=1:alpha=1[spin]"
            )
            steps.append(f"[bg][spin]overlay=(W-w)/2:{_ART_Y}:enable='between(t,{t_spin},{t_spin_end})'[v1]")

            steps.append(square_art(cover_idx, _COVER, "cover_raw"))
            steps.append(f"[cover_raw]fade=t=in:st={t_reveal}:d=1:alpha=1[cover]")
            steps.append(f"[v1][cover]overlay=(W-w)/2:{_ART_Y}:enable='gte(t,{t_reveal})'[outv]")
        else:
            steps.append(fallback_bg(_W, _H, "outv"))

        return ";".join(steps) + ";" + self._text(assets, t_text, t_text_end)

    def _text(self, assets, start, end, link_in="[outv]", link_out="[v]"):
        if not self.has_drawtext():
            return f"{link_in}null{link_out}"

        title = self._wrap_text(assets.track_title.strip().strip('"').strip("'"), width=24, max_lines=2)
        artist = self._wrap_text(assets.artist_name.strip().strip('"').strip("'"), width=24, max_lines=1)

        title_src = self._drawtext_source(title, "title")
        artist_src = self._drawtext_source(artist, "artist")
        title_lines = self._line_count(title)

        title_fs = 68
        artist_fs = 48
        y_title = int(_TITLE_Y - ((title_lines - 1) * title_fs * 1.15))
        y_artist = _ARTIST_Y

        common = readable_common(self)
        alpha_title = self.get_fade_alpha(start, end, 1.25)
        alpha_artist = self.get_fade_alpha(start + 0.8, end, 1.25)

        return (
            f"{link_in}"
            f"drawtext={title_src}:fontcolor=white:fontsize={title_fs}{common}"
            f":x=(w-text_w)/2:y={y_title}:enable='between(t,{start},{end})':alpha='{alpha_title}',"
            f"drawtext={artist_src}:fontcolor=0xBBBBBB:fontsize={artist_fs}{common}"
            f":x=(w-text_w)/2:y={y_artist}:enable='between(t,{start+0.8},{end})':alpha='{alpha_artist}'"
            f"{link_out}"
        )
