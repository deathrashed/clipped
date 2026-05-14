"""
Cinematic template — 21:9 ultrawide letterbox with a slow zoom (Ken Burns) on artwork.
Output: 1920×816. Cinematic, dramatic.

Layout:
  - Artwork: fills width, slow pan/zoom via zoompan filter
  - Letterbox bars: top and bottom 18% black bars
  - Metadata: white text on lower letterbox bar
"""
from __future__ import annotations
from .base import VideoTemplate, TemplateInfo
from ..utils import MediaAssets


class CinematicTemplate(VideoTemplate):
    info = TemplateInfo(
        name="cinematic",
        label="Cinematic (21:9 Ken Burns)",
        description="Ultrawide letterbox with a slow zoom on artwork. Dramatic and filmic.",
        aspect=(1920, 816),
        ideal_for=["YouTube", "Video essays", "Archive"],
    )

    def get_inputs(self, assets: MediaAssets) -> list[str]:
        inputs = [str(assets.audio_path)]
        if assets.cover:
            inputs.append(str(assets.cover))
        return inputs

    def get_filter_graph(self, assets: MediaAssets, duration: float) -> str:
        if assets.cover:
            # Duration for zoompan (in frames at 25fps)
            total_frames = max(250, int(duration * 25))
            graph = (
                # Scale art to 1920×1920, then slow zoom from 1.0→1.08 over duration
                f"[1:v]scale=1920:1920:force_original_aspect_ratio=increase,crop=1920:1920,"
                f"zoompan=z='min(zoom+0.0002,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                f":d={total_frames}:s=1920x1920:fps=25[zoomed];"
                # Crop to 1920×816 from centre
                "[zoomed]crop=1920:816[outv]"
            )
        else:
            graph = "color=s=1920x816:c=black[outv]"

        return graph + ";" + self._drawtext_overlay(assets)

    def _drawtext_overlay(self, assets: "MediaAssets", link_in: str = "[outv]", link_out: str = "[v]") -> str:
        """Cinematic lower-third text overlay."""
        if not self.has_drawtext():
            return f"{link_in}null{link_out}"

        title  = self._wrap_text(assets.track_title, width=36, max_lines=2)
        artist = self._wrap_text(assets.artist_name, width=28, max_lines=1)
        album  = self._wrap_text(assets.album_name, width=30, max_lines=1)
        artist_album = f"{artist}  ·  {album}"

        title_src       = self._drawtext_source(title, prefix="title")
        artist_album_src = self._drawtext_source(artist_album, prefix="artist_album")

        return (
            f"{link_in}"
            f"drawtext={title_src}:fontcolor=white:fontsize=42:expansion=none"
            f":x=80:y=690:enable='gt(t,1)':alpha='if(lt(t,2),t-1,1)',"
            f"drawtext={artist_album_src}:fontcolor=0xAAAAAA:fontsize=26:expansion=none"
            f":x=80:y=752:enable='gt(t,1.5)':alpha='if(lt(t,2.5),t-1.5,1)'"
            f"{link_out}"
        )
