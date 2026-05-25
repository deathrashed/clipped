"""
Vertical Wave template — rotating record with a reactive circular waveform behind it.
Output: 1080×1920 (9:16).
"""
from __future__ import annotations
from .base import VideoTemplate, TemplateInfo
from ..utils import MediaAssets

class VerticalWaveTemplate(VideoTemplate):
    info = TemplateInfo(
        name="vertical_wave",
        label="Vertical Wave (9:16 Reel + Circular Wave)",
        description="Spinning record with a circular reactive waveform behind it.",
        aspect=(1080, 1920),
        ideal_for=["Instagram Reels", "TikTok", "YouTube Shorts"],
    )

    def get_inputs(self, assets: MediaAssets) -> list[str]:
        inputs = [str(assets.audio_path)]
        if assets.cover:
            inputs.append(str(assets.cover))
        return inputs

    def get_filter_graph(self, assets: MediaAssets, duration: float) -> str:
        speed = self.config.get("spinner_speed", 0.5)
        color = self.config.get("waveform_color", "0x00E5FF")
        
        # Wave size slightly larger than the art to peek out from behind
        wave_sz = 860
        art_sz  = 720
        inner_r = art_sz // 2 - 25
        outer_r = wave_sz // 2
        
        steps: list[str] = []
        steps.append(
            f"[0:a]showwaves=s={wave_sz}x{wave_sz}:mode=line:colors={color}@0.75:rate=30,"
            f"format=rgba,colorkey=black:0.12:0.08,"
            f"geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':"
            f"a='if(gte(pow(X-W/2,2)+pow(Y-H/2,2),pow({inner_r},2))*"
            f"lte(pow(X-W/2,2)+pow(Y-H/2,2),pow({outer_r},2)),alpha(X,Y),0)'[wave]"
        )

        if assets.cover:
            # ── 1. Background ─────────────────────────────────────────────────
            steps.append(
                f"[1:v]scale=1080:1920:force_original_aspect_ratio=increase,"
                f"crop=1080:1920,"
                f"gblur=sigma=40,"
                f"eq=brightness=-0.3:saturation=0.8[bg]"
            )

            # ── 2. Spinning Record ────────────────────────────────────────────
            steps.append(
                f"[1:v]scale={art_sz}:{art_sz}:force_original_aspect_ratio=decrease,"
                f"pad={art_sz}:{art_sz}:(ow-iw)/2:(oh-ih)/2:color=black@0,"
                f"format=rgba,"
                f"geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':"
                f"a='if(lte(pow(X-W/2,2)+pow(Y-H/2,2),pow(W/2,2)),255,0)',"
                f"rotate=t*{speed}:c=none[spinner]"
            )

            # ── 3. Composition ────────────────────────────────────────────────
            y_off = 960 - 250
            wave_y = y_off - ((wave_sz - art_sz) // 2)
            steps.append(f"[bg][wave]overlay=(W-w)/2:{wave_y}[bg_wave]")
            steps.append(f"[bg_wave][spinner]overlay=(W-w)/2:{y_off}[outv]")
        else:
            steps.append(f"color=s=1080x1920:c=#0a0a0a[bg]")
            steps.append(f"[bg][wave]overlay=(W-w)/2:640[outv]")

        graph = ";".join(steps)
        return graph + ";" + self._drawtext_overlay(assets, duration, link_in="[outv]")

    def _drawtext_overlay(self, assets: "MediaAssets", duration: float, link_in: str = "[outv]", link_out: str = "[v]") -> str:
        if not self.has_drawtext():
            return f"{link_in}null{link_out}"

        title  = self._wrap_text(assets.track_title, width=28, max_lines=2)
        artist = self._wrap_text(assets.artist_name, width=26, max_lines=1)

        title_src  = self._drawtext_source(title, prefix="title")
        artist_src = self._drawtext_source(artist, prefix="artist")

        t_start = duration / 2
        t_end   = max(t_start + 1.0, duration - 5)
        f_dur   = 1.0
        
        # Safe alpha expression for FFmpeg
        alpha = self.get_fade_alpha(t_start, t_end, f_dur)

        title_fs  = 70
        artist_fs = 45
        gap       = 20
        lh_factor = 1.15

        h_title = self._line_count(title) * title_fs * lh_factor
        y_title = int(1480 - (h_title - (title_fs * lh_factor)))
        y_artist = int(y_title + h_title + gap)

        common = ":text_align=center:expansion=none"

        return (
            f"{link_in}"
            f"drawtext={title_src}:fontcolor=white:fontsize={title_fs}{common}"
            f":x=(w-text_w)/2:y={y_title}:enable='between(t,{t_start},{t_end})':alpha='{alpha}',"
            f"drawtext={artist_src}:fontcolor=0x00E5FF:fontsize={artist_fs}{common}"
            f":x=(w-text_w)/2:y={y_artist}:enable='between(t,{t_start+0.5},{t_end})':alpha='{alpha}'"
            f"{link_out}"
        )
