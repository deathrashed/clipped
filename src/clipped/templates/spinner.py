"""
Spinner template — classic rotating circular record crop on black background.
Output: 1080×1080 (square, ideal for Instagram feed / archive).
"""
from __future__ import annotations
from .base import VideoTemplate, TemplateInfo
from ..utils import MediaAssets


class SpinnerTemplate(VideoTemplate):
    info = TemplateInfo(
        name="spinner",
        label="Spinner (Rotating Record)",
        description="Classic spinning vinyl record on a black background.",
        aspect=(1080, 1080),
        ideal_for=["Instagram Feed", "Archive", "Twitter/X"],
        safe_duration_hint=15.0,
    )

    def get_inputs(self, assets: MediaAssets) -> list[str]:
        inputs = [str(assets.audio_path)]
        if assets.cover:
            inputs.append(str(assets.cover))
        return inputs

    def get_filter_graph(self, assets: MediaAssets, duration: float) -> str:
        speed = self.config.get("spinner_speed", 0.5)  # rev/sec

        if assets.cover:
            graph = (
                "[1:v]scale=1080:1080:force_original_aspect_ratio=increase,"
                "crop=1080:1080,gblur=sigma=40,eq=brightness=-0.3:saturation=0.6[bg];"
                "[1:v]scale=800:800:force_original_aspect_ratio=decrease,"
                "pad=800:800:(ow-iw)/2:(oh-ih)/2:color=black@0[art];"
                "[art]format=rgba,"
                "geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':"
                f"a='if(lte(pow(X-W/2,2)+pow(Y-H/2,2),pow(W/2,2)),255,0)'[fg];"
                f"[fg]rotate=t*{speed}:c=none[fr];"
                "[bg][fr]overlay=(W-w)/2:(H-h)/2-70[outv]"
            )
        else:
            graph = "color=s=1080x1080:c=black[outv]"

        return graph + ";" + self._drawtext_overlay(assets)
