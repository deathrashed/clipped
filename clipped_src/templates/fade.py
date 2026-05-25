"""
Fade template — sequential crossfade image sequence with metadata text overlays.
Output: 1080×1080 (square).
Supports custom sequence [(path, duration), ...] or auto-discovery.
"""
from __future__ import annotations
from .base import VideoTemplate, TemplateInfo
from ..utils import MediaAssets


class FadeTemplate(VideoTemplate):
    info = TemplateInfo(
        name="fade",
        label="Fade (Crossfade Sequence)",
        description="Multi-image crossfade with animated metadata overlays.",
        aspect=(1080, 1080),
        ideal_for=["Full-track previews", "Story posts", "YouTube"],
    )

    def __init__(self, config: dict | None = None, sequence: list[tuple] | None = None):
        super().__init__(config)
        self.sequence = sequence  # list of (Path, float) or None for auto

    def get_inputs(self, assets: MediaAssets) -> list[str]:
        inputs = [str(assets.audio_path)]
        if self.sequence:
            for path, _ in self.sequence:
                inputs.append(str(path))
        else:
            if assets.logo:   inputs.append(str(assets.logo))
            if assets.artist: inputs.append(str(assets.artist))
            if assets.cover:  inputs.append(str(assets.cover))
        return inputs

    def get_filter_graph(self, assets: MediaAssets, duration: float) -> str:
        if self.sequence:
            valid_indices = list(range(1, len(self.sequence) + 1))
            durations = [d for _, d in self.sequence]
        else:
            valid_indices = []
            if assets.logo:   valid_indices.append(len(valid_indices) + 1)
            if assets.artist: valid_indices.append(len(valid_indices) + 1)
            if assets.cover:  valid_indices.append(len(valid_indices) + 1)
            durations = None

        if not valid_indices:
            return "color=s=1080x1080:c=black[outv];" + self._drawtext_overlay(assets)

        all_filters = []
        for i, idx in enumerate(valid_indices):
            all_filters.append(
                f"[{idx}:v]scale=1080:1080:force_original_aspect_ratio=decrease,"
                f"pad=1080:1080:(ow-iw)/2:(oh-ih)/2,format=rgba[v{i}]"
            )

        num = len(valid_indices)
        if durations:
            starts = [0.0]
            for d in durations[:-1]:
                starts.append(starts[-1] + d)
        else:
            # Keep auto transitions inside short clips. The old 5s minimum made
            # a 3s smoke render schedule later images at 5s/10s, which can make
            # FFmpeg sit on an effectively unreachable graph.
            img_dur = duration / num if duration < num * 5 else max(5, duration / num)
            starts = [i * img_dur for i in range(num)]

        if num == 1:
            all_filters.append("[v0]copy[outv]")
        else:
            prev_link = "[v0]"
            for i in range(1, num):
                start_t = starts[i]
                current_link = f"[tmp{i}]" if i < num - 1 else "[outv]"
                all_filters.append(
                    f"[v{i}]fade=in:st={start_t}:d=1[v{i}f]"
                )
                all_filters.append(
                    f"{prev_link}[v{i}f]overlay=0:0:enable='gt(t,{start_t})'{current_link}"
                )
                prev_link = current_link

        all_filters.append(self._drawtext_overlay(assets))
        return ";".join(all_filters)
