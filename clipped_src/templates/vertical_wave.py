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
        
        # Wave size slightly larger than the art to peek out from behind
        wave_sz = 820
        art_sz  = 720
        
        steps: list[str] = []

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
                f"[1:v]scale={art_sz}:{art_sz},"
                f"format=rgba,"
                f"geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':"
                f"a='if(lte(pow(X-W/2,2)+pow(Y-H/2,2),pow(W/2,2)),255,0)',"
                f"rotate=t*{speed}:c=none[spinner]"
            )

            # ── 3. Composition ────────────────────────────────────────────────
            y_off = 960 - 250
            steps.append(f"[bg][spinner]overlay=(W-w)/2:{y_off}[outv]")
        else:
            steps.append(f"color=s=1080x1920:c=#0a0a0a[bg]")
            steps.append(f"[bg]null[outv]")

        graph = ";".join(steps)
        return graph + ";" + self._drawtext_overlay(assets, duration, link_in="[outv]")

    def _drawtext_overlay(self, assets: "MediaAssets", duration: float, link_in: str = "[outv]", link_out: str = "[v]") -> str:
        if not self.has_drawtext():
            return f"{link_in}null{link_out}"

        title  = self._escape(assets.track_title)
        artist = self._escape(assets.artist_name)

        t_start = duration / 2
        t_end   = duration - 5
        f_dur   = 1.0
        
        # Safe alpha expression for FFmpeg
        alpha = self.get_fade_alpha(t_start, t_end, f_dur)

        return (
            f"{link_in}"
            f"drawtext=text='{title}':fontcolor=white:fontsize=80:fontweight=bold"
            f":x=(w-text_w)/2:y=1400:enable='between(t,{t_start},{t_end})':alpha='{alpha}',"
            f"drawtext=text='{artist}':fontcolor=0x00E5FF:fontsize=50"
            f":x=(w-text_w)/2:y=1500:enable='between(t,{t_start+0.5},{t_end})':alpha='{alpha}'"
            f"{link_out}"
        )
