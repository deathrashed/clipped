"""
Vertical Wave template — rotating record with a reactive circular waveform behind it.
Output: 1080×1920 (9:16).

Layout:
  - Background: blurred + darkened album art
  - Middle: reactive circular waveform (avectorscope polar)
  - Middle: crisp circular spinning record (overlayed on waveform)
  - Bottom: metadata text that fades in mid-video and out 5s before end
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
        wave_sz = 820
        art_sz  = 720
        
        steps: list[str] = []

        # ── 1. Circular Waveform ──────────────────────────────────────────────
        # avectorscope in polar mode creates a circular reactive visual
        steps.append(
            f"[0:a]avectorscope=s={wave_sz}x{wave_sz}:m=polar:zoom=2:draw=line:rc=0:gc=229:bc=255:rf=0:gf=229:bf=255,"
            f"format=rgba,"
            f"colorchannelmixer=aa=0.7[wave]"
        )

        if assets.cover:
            # ── 2. Background ─────────────────────────────────────────────────
            steps.append(
                f"[1:v]scale=1080:1920:force_original_aspect_ratio=increase,"
                f"crop=1080:1920,"
                f"gblur=sigma=40,"
                f"eq=brightness=-0.3:saturation=0.8[bg]"
            )

            # ── 3. Spinning Record ────────────────────────────────────────────
            steps.append(
                f"[1:v]scale={art_sz}:{art_sz}[art];"
                f"[art]format=rgba,"
                f"geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':"
                f"a='if(lte(pow(X-W/2,2)+pow(Y-H/2,2),pow(W/2,2)),255,0)'[fg];"
                f"[fg]rotate=t*{speed}:c=none[spinner]"
            )

            # ── 4. Composition ────────────────────────────────────────────────
            # Center of the screen (1080/2, 1920/2) = (540, 960)
            # Offset upwards slightly for vertical feel
            y_off = 960 - 250
            
            # bg -> wave -> spinner
            steps.append(f"[bg][wave]overlay=(W-w)/2:{y_off}-(w-720)/2[mid_wave]")
            steps.append(f"[mid_wave][spinner]overlay=(W-w)/2:{y_off}[outv]")
        else:
            steps.append(f"color=s=1080x1920:c=#0a0a0a[bg]")
            steps.append(f"[bg][wave]overlay=(W-w)/2:960-w/2[outv]")

        graph = ";".join(steps)
        return graph + ";" + self._drawtext_overlay(assets, duration)

    def _drawtext_overlay(self, assets: "MediaAssets", duration: float, link_in: str = "[outv]", link_out: str = "[v]") -> str:
        if not self.has_drawtext():
            return f"{link_in}null{link_out}"

        title  = self._escape(assets.track_title)
        artist = self._escape(assets.artist_name)

        # Timing: start at middle, end 5s before finish
        t_start = duration / 2
        t_end   = duration - 5
        
        # Fade durations
        f_dur = 1.0
        
        # Alpha expression:
        # Fade in: if(lt(t, t_start+f_dur), (t-t_start)/f_dur, 1)
        # Fade out: if(gt(t, t_end-f_dur), 1-(t-(t_end-f_dur))/f_dur, ...)
        # Combined:
        alpha = (
            f"if(lt(t,{t_start}),0,"
            f"if(lt(t,{t_start+f_dur}),(t-{t_start})/{f_dur},"
            f"if(lt(t,{t_end-f_dur}),1,"
            f"if(lt(t,{t_end}),1-(t-({t_end-f_dur}))/{f_dur},0))))"
        )

        return (
            f"{link_in}"
            # Track title
            f"drawtext=text='{title}':fontcolor=white:fontsize=80:fontweight=bold"
            f":x=(w-text_w)/2:y=1400:enable='between(t,{t_start},{t_end})':alpha='{alpha}',"
            # Artist
            f"drawtext=text='{artist}':fontcolor=0x00E5FF:fontsize=50"
            f":x=(w-text_w)/2:y=1500:enable='between(t,{t_start+0.5},{t_end})':alpha='{alpha}'"
            f"{link_out}"
        )
