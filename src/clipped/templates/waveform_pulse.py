from __future__ import annotations
from .base import VideoTemplate, TemplateInfo
from .polish import blurred_bg, fallback_bg, square_art, readable_common
from ..utils import MediaAssets

_W = 1080
_H = 1920

class WaveformPulseTemplate(VideoTemplate):
    info = TemplateInfo(
        name="waveform_pulse",
        label="Waveform Pulse (Pro Audio Reactive)",
        description="Premium vertical reel with real audio waveform, glow, cover art, and safe typography.",
        aspect=(_W, _H),
        ideal_for=["Instagram Reels", "TikTok", "YouTube Shorts"],
    )

    def get_inputs(self, assets: MediaAssets) -> list[str]:
        inputs = [str(assets.audio_path)]
        if assets.cover:
            inputs.append(str(assets.cover))
        return inputs

    def get_filter_graph(self, assets: MediaAssets, duration: float) -> str:
        steps = []

        if assets.cover:
            steps.append(blurred_bg(1, _W, _H, 48, -0.38, 0.75, "bg"))
            steps.append(square_art(1, 780, "art_raw"))
            steps.append(
                "[art_raw]fade=t=in:st=0.7:d=1:alpha=1,"
                "fade=t=out:st=99999:d=1:alpha=1[art]"
            )
            steps.append("[bg][art]overlay=(W-w)/2:360[v1]")
        else:
            steps.append(fallback_bg(_W, _H, "v1"))

        # Real waveform from audio input.
        steps.append(
            "[0:a]aformat=channel_layouts=mono,"
            "showwaves=s=920x230:mode=cline:rate=30:colors=0x00E5FFFF,"
            "format=rgba,colorkey=0x000000:0.22:0.12,"
            "gblur=sigma=1.2,"
            "fade=t=in:st=1.2:d=1:alpha=1[wave]"
        )

        # Soft glow duplicate.
        steps.append(
            "[0:a]aformat=channel_layouts=mono,"
            "showwaves=s=920x230:mode=cline:rate=30:colors=0x5F00FFFF,"
            "format=rgba,colorkey=0x000000:0.22:0.12,"
            "gblur=sigma=8,"
            "fade=t=in:st=1.2:d=1:alpha=1[waveglow]"
        )

        steps.append("[v1][waveglow]overlay=(W-w)/2:1185[v2]")
        steps.append("[v2][wave]overlay=(W-w)/2:1185[outv]")

        return ";".join(steps) + ";" + self._text(assets)

    def _text(self, assets, link_in="[outv]", link_out="[v]"):
        if not self.has_drawtext():
            return f"{link_in}null{link_out}"

        title = self._wrap_text(assets.track_title, 24, 2)
        artist = self._wrap_text(assets.artist_name, 24, 1)
        title_src = self._drawtext_source(title, "title")
        artist_src = self._drawtext_source(artist, "artist")
        lines = self._line_count(title)

        common = readable_common(self)
        y_title = int(1435 - ((lines - 1) * 72))

        return (
            f"{link_in}"
            f"drawtext={title_src}:fontcolor=white:fontsize=70{common}"
            f":x=(w-text_w)/2:y={y_title}:enable='gt(t,1.4)':alpha='if(lt(t,2.4),t-1.4,1)',"
            f"drawtext={artist_src}:fontcolor=0xC9C9C9:fontsize=46{common}"
            f":x=(w-text_w)/2:y=1585:enable='gt(t,1.8)':alpha='if(lt(t,2.8),t-1.8,1)'"
            f"{link_out}"
        )
