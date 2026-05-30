"""
Spinner Story template — 1:1 square video with a sequential story:
1. Logo fade in/out (processed via rmbg background removal)
2. Rotating record spinner (centered and moved up slightly)
3. Artist photo reveal at 75% duration (fetched via ArtistImageFetcher)
"""
from __future__ import annotations
from .base import VideoTemplate, TemplateInfo
from ..utils import MediaAssets


class SpinnerStoryTemplate(VideoTemplate):
    info = TemplateInfo(
        name="spinner_story",
        label="Spinner Story (Logo -> Spinner -> Artist)",
        description="Sequential 1:1 square video featuring logo, spinner, and artist photo.",
        aspect=(1080, 1080),
        ideal_for=["Instagram Feed", "Archive", "Twitter/X"],
    )

    def get_inputs(self, assets: MediaAssets) -> list[str]:
        inputs = [str(assets.audio_path)]
        if assets.cover:
            inputs.append(str(assets.cover))
        if assets.logo:
            inputs.append(str(assets.logo))
        if assets.artist:
            inputs.append(str(assets.artist))
        return inputs

    def get_filter_graph(self, assets: MediaAssets, duration: float) -> str:
        speed = self.config.get("spinner_speed", 0.5)  # rev/sec

        cover_idx = 1 if assets.cover else None
        logo_idx = (1 + (1 if assets.cover else 0)) if assets.logo else None
        artist_idx = (1 + (1 if assets.cover else 0) + (1 if assets.logo else 0)) if assets.artist else None

        steps: list[str] = []

        # ── Background: blurred and dimmed ────────────────────────────────────
        if assets.cover:
            steps.append(
                f"[{cover_idx}:v]scale=1080:1080:force_original_aspect_ratio=increase,"
                f"crop=1080:1080,gblur=sigma=40,eq=brightness=-0.3:saturation=0.6[bg]"
            )
        else:
            steps.append("color=s=1080x1080:c=#0d0d0d[bg]")

        current_v = "[bg]"

        # ── Timings & Orchestration ──────────────────────────────────────────
        logo_fade_dur = min(1.0, max(0.25, duration * 0.08))
        if assets.logo:
            t_logo_end = min(4.0, max(logo_fade_dur * 2, duration * 0.25))
            t_logo_fade_out = max(logo_fade_dur, t_logo_end - logo_fade_dur)
            t_spin_start = t_logo_end
        else:
            t_logo_end = 0.0
            t_spin_start = 0.0

        if assets.artist:
            t_art_start = duration * 0.75
            if t_art_start < t_spin_start + 1.0:
                t_art_start = min(duration - 1.0, t_spin_start + 1.0)
            t_spin_fade_out = t_art_start
            t_spin_end = t_spin_fade_out + 1.0
        else:
            t_art_start = duration
            t_spin_fade_out = max(t_spin_start, duration - 1.5)
            t_spin_end = duration

        # ── Stage 1: Logo Fade In/Out ────────────────────────────────────────
        if assets.logo:
            steps.append(
                f"[{logo_idx}:v]scale=700:700:force_original_aspect_ratio=decrease,"
                f"pad=700:700:(ow-iw)/2:(oh-ih)/2:color=black@0,format=rgba,"
                f"fade=t=in:st=0.5:d={logo_fade_dur}:alpha=1,"
                f"fade=t=out:st={t_logo_fade_out}:d={logo_fade_dur}:alpha=1[logo_ov]"
            )
            steps.append(
                f"{current_v}[logo_ov]overlay=(W-w)/2:(H-h)/2"
                f":enable='between(t,0.5,{t_logo_end})'[v_logo]"
            )
            current_v = "[v_logo]"

        # ── Stage 2: Spinning Record ─────────────────────────────────────────
        if assets.cover:
            steps.append(
                f"[{cover_idx}:v]scale=800:800:force_original_aspect_ratio=decrease,"
                f"pad=800:800:(ow-iw)/2:(oh-ih)/2:color=black@0[art];"
                f"[art]format=rgba,"
                f"geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':"
                f"a='if(lte(pow(X-W/2,2)+pow(Y-H/2,2),pow(W/2,2)),255,0)'[fg_circle];"
                f"[fg_circle]rotate=t*{speed}:c=none,"
                f"fade=t=in:st={t_spin_start}:d=1.0:alpha=1,"
                f"fade=t=out:st={t_spin_fade_out}:d=1.0:alpha=1[spinner_ov]"
            )
            steps.append(
                f"{current_v}[spinner_ov]overlay=(W-w)/2:(H-h)/2-70"
                f":enable='between(t,{t_spin_start},{t_spin_end})'[v_spin]"
            )
            current_v = "[v_spin]"

        # ── Stage 3: Artist Photo Reveal ──────────────────────────────────────
        if assets.artist:
            t_art_fade_out = max(t_art_start + 1.0, duration - 1.5)
            steps.append(
                f"[{artist_idx}:v]scale=800:800:force_original_aspect_ratio=decrease,"
                f"pad=800:800:(ow-iw)/2:(oh-ih)/2:color=black@0,format=rgba,"
                f"fade=t=in:st={t_art_start}:d=1.0:alpha=1,"
                f"fade=t=out:st={t_art_fade_out}:d=1.0:alpha=1[artist_ov]"
            )
            steps.append(
                f"{current_v}[artist_ov]overlay=(W-w)/2:(H-h)/2-70"
                f":enable='gte(t,{t_art_start})'[v_art]"
            )
            current_v = "[v_art]"

        graph = ";".join(steps)
        t_text_start = t_spin_start if assets.logo else 1.0
        return graph + ";" + self._drawtext_overlay(
            assets,
            duration=duration,
            t_text_start=t_text_start,
            link_in=current_v
        )

    def _drawtext_overlay(
        self,
        assets: MediaAssets,
        duration: float,
        t_text_start: float,
        link_in: str = "[outv]",
        link_out: str = "[v]",
    ) -> str:
        if not self.has_drawtext():
            return f"{link_in}null{link_out}"

        title_text  = self._wrap_text(assets.track_title, width=28, max_lines=2)
        artist_text = self._wrap_text(assets.artist_name, width=28, max_lines=2)
        album_text  = self._wrap_text(assets.album_name,  width=32, max_lines=2)

        title_src  = self._drawtext_source(title_text,  prefix="title")
        artist_src = self._drawtext_source(artist_text, prefix="artist")
        album_src  = self._drawtext_source(album_text,  prefix="album")

        title_lines  = self._line_count(title_text)
        artist_lines = self._line_count(artist_text)

        w, h = self.info.aspect
        title_fs  = 42
        artist_fs = 30
        album_fs  = 24
        gap       = 10
        lh_factor = 1.15

        h_title  = title_lines  * title_fs  * lh_factor
        h_artist = artist_lines * artist_fs * lh_factor

        # Shifted further down (h-150) to avoid overlap with large centered art/spinners.
        y_title  = int(h - 150 - (h_title - (title_fs * lh_factor)))
        y_artist = int(y_title + h_title + gap)
        y_album  = int(y_artist + h_artist + gap)

        t_end = max(t_text_start + 3.0, duration - 1.5)
        
        alpha_title  = self.get_fade_alpha(t_text_start,       t_end, 1.0)
        alpha_artist = self.get_fade_alpha(t_text_start + 0.5, t_end, 1.0)
        alpha_album  = self.get_fade_alpha(t_text_start + 1.0, t_end, 1.0)

        common = ":text_align=center:expansion=none"

        return (
            f"{link_in}"
            f"drawtext={title_src}:fontcolor=white:fontsize={title_fs}{common}"
            f":x=(w-text_w)/2:y={y_title}:enable='between(t,{t_text_start},{t_end})':alpha='{alpha_title}',"
            f"drawtext={artist_src}:fontcolor=0xAAAAAA:fontsize={artist_fs}{common}"
            f":x=(w-text_w)/2:y={y_artist}:enable='between(t,{t_text_start + 0.5},{t_end})':alpha='{alpha_artist}',"
            f"drawtext={album_src}:fontcolor=0x888888:fontsize={album_fs}{common}"
            f":x=(w-text_w)/2:y={y_album}:enable='between(t,{t_text_start + 1.0},{t_end})':alpha='{alpha_album}'"
            f"{link_out}"
        )
