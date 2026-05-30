"""
Static template — clean centered artwork on a solid black background.
Output: 1080×1080 (square). High-fidelity, no motion.
"""
from __future__ import annotations
from .base import VideoTemplate, TemplateInfo
from ..utils import MediaAssets


class StaticTemplate(VideoTemplate):
    info = TemplateInfo(
        name="static",
        label="Static (Centered Artwork)",
        description="Clean album art on black. High-fidelity, no motion.",
        aspect=(1080, 1080),
        ideal_for=["Archive uploads", "SoundCloud", "Bandcamp"],
    )

    def get_inputs(self, assets: MediaAssets) -> list[str]:
        inputs = [str(assets.audio_path)]
        if assets.cover:
            inputs.append(str(assets.cover))
        return inputs

    def get_filter_graph(self, assets: MediaAssets, duration: float) -> str:
        if assets.cover:
            graph = (
                "[1:v]scale=1080:1080:force_original_aspect_ratio=decrease,"
                "pad=1080:1080:(ow-iw)/2:(oh-ih)/2[outv]"
            )
        else:
            graph = "color=s=1080x1080:c=black[outv]"

        return graph + ";" + self._drawtext_overlay(assets)
