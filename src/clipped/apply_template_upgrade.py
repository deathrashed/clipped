from pathlib import Path
import shutil
import re

ROOT = Path.cwd()
TPL = next((p for p in [
    ROOT / "templates",
    ROOT / "clipped" / "templates",
    ROOT / "src" / "clipped" / "templates",
] if p.exists()), None)

if not TPL:
    raise SystemExit("Could not find clipped templates folder")

print(f"Using templates folder: {TPL}")

def write(name: str, text: str):
    path = TPL / name
    if path.exists():
        shutil.copy2(path, path.with_suffix(path.suffix + ".bak"))
    path.write_text(text.strip() + "\n", encoding="utf-8")
    print("wrote", name)

POLISH = r'''
from __future__ import annotations
from pathlib import Path

FONT_FILE = "/System/Library/Fonts/Supplemental/Arial.ttf"

def font(template):
    return f":fontfile='{template._escape_path(FONT_FILE)}'" if Path(FONT_FILE).exists() else ""

def meta(assets, name, default=""):
    return str(getattr(assets, name, "") or default)

def year(assets):
    return meta(assets, "year") or meta(getattr(assets, "metadata", object()), "year")

def genre(assets):
    return meta(assets, "genre") or meta(getattr(assets, "metadata", object()), "genre")

def bg_cover(idx, w, h, label="bg", blur=42, bright=-0.36, sat=0.65):
    return (
        f"[{idx}:v]scale={w}:{h}:force_original_aspect_ratio=increase,"
        f"crop={w}:{h},gblur=sigma={blur},eq=brightness={bright}:saturation={sat}[{label}]"
    )

def solid(w, h, label="bg", color="#07070a"):
    return f"color=s={w}x{h}:c={color}[{label}]"

def square(idx, size, label):
    return (
        f"[{idx}:v]scale={size}:{size}:force_original_aspect_ratio=decrease,"
        f"pad={size}:{size}:(ow-iw)/2:(oh-ih)/2:color=black@0,format=rgba[{label}]"
    )

def circle(idx, size, speed, label):
    return (
        f"[{idx}:v]scale={size}:{size}:force_original_aspect_ratio=decrease,"
        f"pad={size}:{size}:(ow-iw)/2:(oh-ih)/2:color=black@0,format=rgba,"
        f"geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':"
        f"a='if(lte(pow(X-W/2,2)+pow(Y-H/2,2),pow(W/2,2)),255,0)',"
        f"rotate=t*{speed}:c=none[{label}]"
    )

def readable(template, align="center"):
    return (
        f"{font(template)}:text_align={align}:expansion=none"
        ":shadowcolor=black@0.85:shadowx=0:shadowy=4"
        ":borderw=2:bordercolor=black@0.55"
    )
'''

SPINNER = r'''
from __future__ import annotations
from .base import VideoTemplate, TemplateInfo
from .polish import bg_cover, solid, square, circle, readable
from ..utils import MediaAssets

class SpinnerTemplate(VideoTemplate):
    info = TemplateInfo(
        name="spinner",
        label="Spinner Story",
        description="Square album-art spinner with staged reveal and readable lower card.",
        aspect=(1080, 1080),
        ideal_for=["Instagram Feed", "Archive", "Twitter/X"],
    )

    def get_inputs(self, assets: MediaAssets) -> list[str]:
        inputs = [str(assets.audio_path)]
        if assets.cover:
            inputs.append(str(assets.cover))
        return inputs

    def get_filter_graph(self, assets: MediaAssets, duration: float) -> str:
        speed = self.config.get("spinner_speed", 0.55)

        if not assets.cover:
            graph = solid(1080, 1080, "outv")
            return graph + ";" + self._text(assets, 1.0, duration)

        t_spin = 0.5
        t_text = min(2.8, max(1.1, duration * 0.2))
        t_reveal = min(max(4.0, duration * 0.68), max(4.0, duration - 1.4))

        steps = [
            bg_cover(1, 1080, 1080, "bg", 36, -0.38, 0.58),
            circle(1, 620, speed, "disc_raw"),
            "[disc_raw]fade=t=in:st=0.5:d=0.8:alpha=1,fade=t=out:st=%s:d=0.9:alpha=1[disc]" % t_reveal,
            "[bg][disc]overlay=(W-w)/2:105:enable='between(t,%s,%s)'[v1]" % (t_spin, t_reveal + 0.9),
            square(1, 650, "cover_raw"),
            "[cover_raw]fade=t=in:st=%s:d=0.9:alpha=1[cover]" % t_reveal,
            "[v1][cover]overlay=(W-w)/2:95:enable='gte(t,%s)'[outv]" % t_reveal,
        ]

        return ";".join(steps) + ";" + self._text(assets, t_text, duration)

    def _text(self, assets, start, end, link_in="[outv]", link_out="[v]"):
        if not self.has_drawtext():
            return f"{link_in}null{link_out}"

        title = self._wrap_text(assets.track_title, 24, 2)
        artist = self._wrap_text(assets.artist_name, 26, 1)
        title_src = self._drawtext_source(title, "title")
        artist_src = self._drawtext_source(artist, "artist")
        lines = self._line_count(title)
        y = int(790 - ((lines - 1) * 56))
        common = readable(self)

        return (
            f"{link_in}"
            f"drawtext={title_src}:fontcolor=white:fontsize=54{common}:x=(w-text_w)/2:y={y}:enable='between(t,{start},{end})':alpha='{self.get_fade_alpha(start,end,0.9)}',"
            f"drawtext={artist_src}:fontcolor=0xC8C8C8:fontsize=34{common}:x=(w-text_w)/2:y=920:enable='between(t,{start+0.45},{end})':alpha='{self.get_fade_alpha(start+0.45,end,0.9)}'"
            f"{link_out}"
        )
'''

VINYL = r'''
from __future__ import annotations
from .base import VideoTemplate, TemplateInfo
from .polish import bg_cover, solid, square, circle, readable, year, genre
from ..utils import MediaAssets

class VinylSleeveTemplate(VideoTemplate):
    info = TemplateInfo(
        name="vinyl_sleeve",
        label="Vinyl Sleeve",
        description="Album cover sleeve with spinning record reveal. Uses album art, not artist image.",
        aspect=(1080, 1920),
        ideal_for=["Reels", "TikTok", "Music promos"],
    )

    def get_inputs(self, assets: MediaAssets) -> list[str]:
        inputs = [str(assets.audio_path)]
        if assets.cover:
            inputs.append(str(assets.cover))
        return inputs

    def get_filter_graph(self, assets: MediaAssets, duration: float) -> str:
        if not assets.cover:
            return solid(1080, 1920, "outv") + ";" + self._text(assets, 1, duration)

        speed = self.config.get("vinyl_speed", 0.75)
        steps = [
            bg_cover(1,1080,1920,"bg",46,-0.38,0.64),
            circle(1,760,speed,"disc_raw"),
            square(1,760,"sleeve_raw"),
            "[disc_raw]fade=t=in:st=0.6:d=0.8:alpha=1[disc]",
            "[sleeve_raw]fade=t=in:st=1.0:d=0.8:alpha=1[sleeve]",
            "[bg][disc]overlay=x='120+min(max(t-1.2,0)*95,190)':y=350[v1]",
            "[v1][sleeve]overlay=x='90-min(max(t-2.2,0)*12,30)':y=350[outv]",
        ]
        return ";".join(steps) + ";" + self._text(assets, 2.2, duration)

    def _text(self, assets, start, end, link_in="[outv]", link_out="[v]"):
        if not self.has_drawtext():
            return f"{link_in}null{link_out}"

        title = self._wrap_text(assets.track_title, 24, 2)
        artist = self._wrap_text(assets.artist_name, 26, 1)
        detail = " · ".join(x for x in [year(assets), genre(assets)] if x)

        title_src = self._drawtext_source(title, "title")
        artist_src = self._drawtext_source(artist, "artist")
        detail_src = self._drawtext_source(detail, "detail")
        lines = self._line_count(title)
        y = int(1240 - ((lines - 1) * 68))
        common = readable(self)

        return (
            f"{link_in}"
            f"drawtext={title_src}:fontcolor=white:fontsize=66{common}:x=(w-text_w)/2:y={y}:enable='between(t,{start},{end})':alpha='{self.get_fade_alpha(start,end,1)}',"
            f"drawtext={artist_src}:fontcolor=0xCFCFCF:fontsize=44{common}:x=(w-text_w)/2:y=1415:enable='between(t,{start+0.4},{end})':alpha='{self.get_fade_alpha(start+0.4,end,1)}',"
            f"drawtext={detail_src}:fontcolor=0x9E9E9E:fontsize=30{common}:x=(w-text_w)/2:y=1495:enable='between(t,{start+0.8},{end})':alpha='{self.get_fade_alpha(start+0.8,end,1)}'"
            f"{link_out}"
        )
'''

NEON = r'''
from __future__ import annotations
from .base import VideoTemplate, TemplateInfo
from .polish import bg_cover, solid, square, readable, year, genre
from ..utils import MediaAssets

class NeonPulseTemplate(VideoTemplate):
    info = TemplateInfo(
        name="neon_pulse",
        label="Neon Pulse",
        description="Animated glow, waveform accent, album cover reveal, and compact metadata.",
        aspect=(1080,1920),
        ideal_for=["EDM", "Metal", "Reels", "TikTok"],
    )

    def get_inputs(self, assets: MediaAssets) -> list[str]:
        inputs = [str(assets.audio_path)]
        if assets.cover:
            inputs.append(str(assets.cover))
        return inputs

    def get_filter_graph(self, assets: MediaAssets, duration: float) -> str:
        if not assets.cover:
            base = solid(1080,1920,"v1")
        else:
            base = ";".join([
                bg_cover(1,1080,1920,"bg",54,-0.44,0.95),
                square(1,760,"art_raw"),
                "[art_raw]scale=w='760+18*sin(t*2.8)':h='760+18*sin(t*2.8)':eval=frame[art_p]",
                "[art_p]gblur=sigma=22,colorchannelmixer=aa=0.55[glow]",
                "[bg][glow]overlay=(W-w)/2:330[v0]",
                "[v0][art_p]overlay=(W-w)/2:350[v1]",
            ])

        steps = [base]
        steps.append(
            "[0:a]aformat=channel_layouts=mono,"
            "showwaves=s=900x180:mode=cline:rate=30:colors=0x00E5FFFF,"
            "format=rgba,colorkey=0x000000:0.25:0.12,gblur=sigma=1,"
            "fade=t=in:st=1.5:d=0.8:alpha=1[wave]"
        )
        steps.append("[v1][wave]overlay=(W-w)/2:1180[outv]")
        return ";".join(steps) + ";" + self._text(assets, 1.8, duration)

    def _text(self, assets, start, end, link_in="[outv]", link_out="[v]"):
        if not self.has_drawtext():
            return f"{link_in}null{link_out}"

        title = self._wrap_text(assets.track_title, 23, 2)
        artist = self._wrap_text(assets.artist_name, 25, 1)
        detail = " · ".join(x for x in [year(assets), genre(assets)] if x)

        title_src = self._drawtext_source(title, "title")
        artist_src = self._drawtext_source(artist, "artist")
        detail_src = self._drawtext_source(detail, "detail")
        lines = self._line_count(title)
        y = int(1345 - ((lines - 1) * 62))
        common = readable(self)

        return (
            f"{link_in}"
            f"drawtext={title_src}:fontcolor=0x00E5FF:fontsize=62{common}:x=(w-text_w)/2:y={y}:enable='between(t,{start},{end})':alpha='{self.get_fade_alpha(start,end,1)}',"
            f"drawtext={artist_src}:fontcolor=white:fontsize=42{common}:x=(w-text_w)/2:y=1495:enable='between(t,{start+0.35},{end})':alpha='{self.get_fade_alpha(start+0.35,end,1)}',"
            f"drawtext={detail_src}:fontcolor=0xAEEFFF:fontsize=28{common}:x=(w-text_w)/2:y=1565:enable='between(t,{start+0.7},{end})':alpha='{self.get_fade_alpha(start+0.7,end,1)}'"
            f"{link_out}"
        )
'''

METADATA = r'''
from __future__ import annotations
from .base import VideoTemplate, TemplateInfo
from .polish import bg_cover, solid, square, readable, year, genre
from ..utils import MediaAssets

class MetadataCardTemplate(VideoTemplate):
    info = TemplateInfo(
        name="metadata_card",
        label="Metadata Card",
        description="Detailed album-art card using title, artist, album, year and genre.",
        aspect=(1080,1920),
        ideal_for=["Archives", "Library previews", "Reels"],
    )

    def get_inputs(self, assets: MediaAssets) -> list[str]:
        inputs = [str(assets.audio_path)]
        if assets.cover:
            inputs.append(str(assets.cover))
        return inputs

    def get_filter_graph(self, assets: MediaAssets, duration: float) -> str:
        if assets.cover:
            graph = ";".join([
                bg_cover(1,1080,1920,"bg",48,-0.42,0.55),
                square(1,620,"cover"),
                "[cover]fade=t=in:st=0.7:d=0.9:alpha=1[cover_f]",
                "[bg][cover_f]overlay=80:255[outv]",
            ])
        else:
            graph = solid(1080,1920,"outv")
        return graph + ";" + self._text(assets, 1.2, duration)

    def _text(self, assets, start, end, link_in="[outv]", link_out="[v]"):
        if not self.has_drawtext():
            return f"{link_in}null{link_out}"

        album = getattr(assets, "album_name", "") or ""
        rows = [
            ("TRACK", assets.track_title),
            ("ARTIST", assets.artist_name),
            ("ALBUM", album),
            ("YEAR", year(assets)),
            ("GENRE", genre(assets)),
        ]

        common = readable(self, "left")
        out = link_in
        y = 960
        for i, (label, value) in enumerate(rows):
            if not value:
                continue
            label_src = self._drawtext_source(label, f"label{i}")
            value_src = self._drawtext_source(self._wrap_text(value, 26, 2), f"value{i}")
            st = start + i * 0.25
            out += (
                f"drawtext={label_src}:fontcolor=0x8E8E8E:fontsize=24{common}:x=80:y={y}:enable='between(t,{st},{end})':alpha='{self.get_fade_alpha(st,end,0.7)}',"
                f"drawtext={value_src}:fontcolor=white:fontsize={50 if i == 0 else 36}{common}:x=80:y={y+36}:enable='between(t,{st+0.1},{end})':alpha='{self.get_fade_alpha(st+0.1,end,0.7)}',"
            )
            y += 140 if i == 0 else 115

        return out.rstrip(",") + link_out
'''

FADE_PREMIUM = r'''
from __future__ import annotations
from .base import VideoTemplate, TemplateInfo
from .polish import bg_cover, solid, square, readable, year, genre
from ..utils import MediaAssets

class FadePremiumTemplate(VideoTemplate):
    info = TemplateInfo(
        name="fade_premium",
        label="Fade Premium",
        description="Logo/artist/album sequence with album cover as final hero image.",
        aspect=(1080,1080),
        ideal_for=["Instagram Feed", "Archive"],
    )

    def get_inputs(self, assets: MediaAssets) -> list[str]:
        inputs = [str(assets.audio_path)]
        if assets.logo:
            inputs.append(str(assets.logo))
        if assets.artist:
            inputs.append(str(assets.artist))
        if assets.cover:
            inputs.append(str(assets.cover))
        return inputs

    def get_filter_graph(self, assets: MediaAssets, duration: float) -> str:
        idx = 1
        logo_idx = idx if assets.logo else None
        if assets.logo: idx += 1
        artist_idx = idx if assets.artist else None
        if assets.artist: idx += 1
        cover_idx = idx if assets.cover else None

        if cover_idx:
            steps = [bg_cover(cover_idx,1080,1080,"bg",36,-0.40,0.58)]
        else:
            steps = [solid(1080,1080,"bg")]

        current = "bg"

        if logo_idx:
            steps.append(
                f"[{logo_idx}:v]scale=720:260:force_original_aspect_ratio=decrease,format=rgba,"
                f"fade=t=in:st=0.4:d=0.7:alpha=1,fade=t=out:st=2.8:d=0.7:alpha=1[logo]"
            )
            steps.append(f"[{current}][logo]overlay=(W-w)/2:145[v1]")
            current = "v1"

        if artist_idx:
            steps.append(
                f"[{artist_idx}:v]scale=760:430:force_original_aspect_ratio=increase,crop=760:430,"
                f"format=rgba,fade=t=in:st=3.0:d=0.8:alpha=1,fade=t=out:st=5.4:d=0.8:alpha=1[artistimg]"
            )
            steps.append(f"[{current}][artistimg]overlay=(W-w)/2:130[v2]")
            current = "v2"

        if cover_idx:
            steps.append(square(cover_idx,620,"cover_raw"))
            steps.append("[cover_raw]fade=t=in:st=5.6:d=0.9:alpha=1[cover]")
            steps.append(f"[{current}][cover]overlay=(W-w)/2:90[outv]")
        else:
            steps.append(f"[{current}]null[outv]")

        return ";".join(steps) + ";" + self._text(assets, 2.8, duration)

    def _text(self, assets, start, end, link_in="[outv]", link_out="[v]"):
        if not self.has_drawtext():
            return f"{link_in}null{link_out}"

        title = self._wrap_text(assets.track_title, 24, 2)
        artist = self._wrap_text(assets.artist_name, 26, 1)
        detail = " · ".join(x for x in [year(assets), genre(assets)] if x)

        title_src = self._drawtext_source(title, "title")
        artist_src = self._drawtext_source(artist, "artist")
        detail_src = self._drawtext_source(detail, "detail")
        common = readable(self)
        lines = self._line_count(title)
        y = int(735 - ((lines - 1) * 54))

        return (
            f"{link_in}"
            f"drawtext={title_src}:fontcolor=white:fontsize=52{common}:x=(w-text_w)/2:y={y}:enable='between(t,{start},{end})':alpha='{self.get_fade_alpha(start,end,0.8)}',"
            f"drawtext={artist_src}:fontcolor=0xD0D0D0:fontsize=34{common}:x=(w-text_w)/2:y=870:enable='between(t,{start+0.4},{end})':alpha='{self.get_fade_alpha(start+0.4,end,0.8)}',"
            f"drawtext={detail_src}:fontcolor=0x9E9E9E:fontsize=24{common}:x=(w-text_w)/2:y=925:enable='between(t,{start+0.8},{end})':alpha='{self.get_fade_alpha(start+0.8,end,0.8)}'"
            f"{link_out}"
        )
'''

POSTER = r'''
from __future__ import annotations
from .base import VideoTemplate, TemplateInfo
from .polish import bg_cover, solid, square, readable, year, genre
from ..utils import MediaAssets

class PosterTemplate(VideoTemplate):
    info = TemplateInfo(
        name="poster",
        label="Concert Poster",
        description="Animated poster layout with album cover reveal and metadata.",
        aspect=(1080,1920),
        ideal_for=["Promos", "Stories", "Reels"],
    )

    def get_inputs(self, assets: MediaAssets) -> list[str]:
        inputs = [str(assets.audio_path)]
        if assets.cover:
            inputs.append(str(assets.cover))
        return inputs

    def get_filter_graph(self, assets: MediaAssets, duration: float) -> str:
        if assets.cover:
            graph = ";".join([
                bg_cover(1,1080,1920,"bg",38,-0.48,0.5),
                square(1,600,"cover_raw"),
                "[cover_raw]fade=t=in:st=1.4:d=0.9:alpha=1[cover]",
                "[bg][cover]overlay=x=(W-w)/2:y='790-min(max(t-1.4,0)*35,55)'[outv]",
            ])
        else:
            graph = solid(1080,1920,"outv")
        return graph + ";" + self._text(assets, 0.5, duration)

    def _text(self, assets, start, end, link_in="[outv]", link_out="[v]"):
        if not self.has_drawtext():
            return f"{link_in}null{link_out}"

        artist = self._wrap_text(assets.artist_name.upper(), 22, 1)
        title = self._wrap_text(assets.track_title.upper(), 16, 3)
        detail = " · ".join(x for x in [year(assets), genre(assets)] if x)

        artist_src = self._drawtext_source(artist, "artist")
        title_src = self._drawtext_source(title, "title")
        detail_src = self._drawtext_source(detail, "detail")
        common = readable(self)

        return (
            f"{link_in}"
            f"drawtext={artist_src}:fontcolor=0xCFCFCF:fontsize=38{common}:x=(w-text_w)/2:y=205:enable='between(t,{start},{end})':alpha='{self.get_fade_alpha(start,end,0.8)}',"
            f"drawtext={title_src}:fontcolor=white:fontsize=78{common}:x=(w-text_w)/2:y=280:enable='between(t,{start+0.35},{end})':alpha='{self.get_fade_alpha(start+0.35,end,0.8)}',"
            f"drawtext={detail_src}:fontcolor=0xAAAAAA:fontsize=30{common}:x=(w-text_w)/2:y=1495:enable='between(t,{start+1.4},{end})':alpha='{self.get_fade_alpha(start+1.4,end,0.8)}'"
            f"{link_out}"
        )
'''

ARTIST_FOCUS = r'''
from __future__ import annotations
from .base import VideoTemplate, TemplateInfo
from .polish import bg_cover, solid, square, readable, year, genre
from ..utils import MediaAssets

class ArtistFocusTemplate(VideoTemplate):
    info = TemplateInfo(
        name="artist_focus",
        label="Artist Focus",
        description="Artist image hero background, album cover card, logo, year and genre.",
        aspect=(1080,1920),
        ideal_for=["Artist promos", "Reels", "TikTok"],
    )

    def get_inputs(self, assets: MediaAssets) -> list[str]:
        inputs = [str(assets.audio_path)]
        if assets.artist:
            inputs.append(str(assets.artist))
        if assets.logo:
            inputs.append(str(assets.logo))
        if assets.cover:
            inputs.append(str(assets.cover))
        return inputs

    def get_filter_graph(self, assets: MediaAssets, duration: float) -> str:
        idx = 1
        artist_idx = idx if assets.artist else None
        if assets.artist: idx += 1
        logo_idx = idx if assets.logo else None
        if assets.logo: idx += 1
        cover_idx = idx if assets.cover else None

        steps = []

        if artist_idx:
            frames = max(150, int(duration * 25))
            steps.append(
                f"[{artist_idx}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
                f"zoompan=z='min(zoom+0.00014,1.08)':d={frames}:s=1080x1920:fps=25,"
                f"eq=brightness=-0.22:saturation=0.82[base]"
            )
        elif cover_idx:
            steps.append(bg_cover(cover_idx,1080,1920,"base",48,-0.38,0.65))
        else:
            steps.append(solid(1080,1920,"base"))

        cur = "base"

        if logo_idx:
            steps.append(
                f"[{logo_idx}:v]scale=700:250:force_original_aspect_ratio=decrease,format=rgba,"
                f"fade=t=in:st=0.8:d=1:alpha=1[logo]"
            )
            steps.append(f"[{cur}][logo]overlay=(W-w)/2:150[v1]")
            cur = "v1"

        if cover_idx:
            steps.append(square(cover_idx,360,"cover_raw"))
            steps.append("[cover_raw]fade=t=in:st=2.2:d=0.9:alpha=1[cover]")
            steps.append(f"[{cur}][cover]overlay=80:1250[outv]")
        else:
            steps.append(f"[{cur}]null[outv]")

        return ";".join(steps) + ";" + self._text(assets, 2.4, duration)

    def _text(self, assets, start, end, link_in="[outv]", link_out="[v]"):
        if not self.has_drawtext():
            return f"{link_in}null{link_out}"

        artist = self._wrap_text(assets.artist_name.upper(), 22, 1)
        title = self._wrap_text(assets.track_title, 22, 2)
        detail = " · ".join(x for x in [getattr(assets, "album_name", ""), year(assets), genre(assets)] if x)

        artist_src = self._drawtext_source(artist, "artist")
        title_src = self._drawtext_source(title, "title")
        detail_src = self._drawtext_source(detail, "detail")
        common = readable(self, "left")

        return (
            f"{link_in}"
            f"drawtext={artist_src}:fontcolor=0xD8D8D8:fontsize=30{common}:x=480:y=1265:enable='between(t,{start},{end})':alpha='{self.get_fade_alpha(start,end,0.8)}',"
            f"drawtext={title_src}:fontcolor=white:fontsize=52{common}:x=480:y=1310:enable='between(t,{start+0.3},{end})':alpha='{self.get_fade_alpha(start+0.3,end,0.8)}',"
            f"drawtext={detail_src}:fontcolor=0xBBBBBB:fontsize=26{common}:x=480:y=1445:enable='between(t,{start+0.6},{end})':alpha='{self.get_fade_alpha(start+0.6,end,0.8)}'"
            f"{link_out}"
        )
'''

CINEMATIC = r'''
from __future__ import annotations
from .base import VideoTemplate, TemplateInfo
from .polish import solid, readable, year, genre
from ..utils import MediaAssets

class CinematicTemplate(VideoTemplate):
    info = TemplateInfo(
        name="cinematic",
        label="Cinematic",
        description="Real cinematic crop with slow zoom, dark lower band and staged lower-third.",
        aspect=(1920,1080),
        ideal_for=["YouTube", "Archive", "Promos"],
    )

    def get_inputs(self, assets: MediaAssets) -> list[str]:
        inputs = [str(assets.audio_path)]
        if assets.cover:
            inputs.append(str(assets.cover))
        return inputs

    def get_filter_graph(self, assets: MediaAssets, duration: float) -> str:
        if assets.cover:
            frames = max(150, int(duration * 25))
            graph = (
                f"[1:v]scale=2160:2160:force_original_aspect_ratio=increase,crop=2160:2160,"
                f"zoompan=z='min(zoom+0.00016,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                f"d={frames}:s=1920x1080:fps=25,eq=brightness=-0.08:saturation=0.9[scene];"
                f"color=s=1920x230:c=black@0.72,format=rgba[band];"
                f"[scene][band]overlay=0:850[outv]"
            )
        else:
            graph = solid(1920,1080,"outv")
        return graph + ";" + self._text(assets, 1.0, duration)

    def _text(self, assets, start, end, link_in="[outv]", link_out="[v]"):
        if not self.has_drawtext():
            return f"{link_in}null{link_out}"

        title = self._wrap_text(assets.track_title, 40, 2)
        artist = self._wrap_text(assets.artist_name, 35, 1)
        detail = " · ".join(x for x in [getattr(assets, "album_name", ""), year(assets), genre(assets)] if x)

        title_src = self._drawtext_source(title, "title")
        artist_src = self._drawtext_source(artist, "artist")
        detail_src = self._drawtext_source(detail, "detail")
        common = readable(self, "left")

        return (
            f"{link_in}"
            f"drawtext={title_src}:fontcolor=white:fontsize=52{common}:x=90:y=875:enable='between(t,{start},{end})':alpha='{self.get_fade_alpha(start,end,1)}',"
            f"drawtext={artist_src}:fontcolor=0xD0D0D0:fontsize=34{common}:x=92:y=970:enable='between(t,{start+0.35},{end})':alpha='{self.get_fade_alpha(start+0.35,end,1)}',"
            f"drawtext={detail_src}:fontcolor=0x999999:fontsize=26{common}:x=92:y=1020:enable='between(t,{start+0.7},{end})':alpha='{self.get_fade_alpha(start+0.7,end,1)}'"
            f"{link_out}"
        )
'''

WAVEFORM = r'''
from __future__ import annotations
from .base import VideoTemplate, TemplateInfo
from .polish import bg_cover, solid, square, readable, year, genre
from ..utils import MediaAssets

class WaveformStageTemplate(VideoTemplate):
    info = TemplateInfo(
        name="waveform_stage",
        label="Waveform Stage",
        description="Album cover plus real audio waveform hero and metadata.",
        aspect=(1080,1920),
        ideal_for=["Audio previews", "Reels", "TikTok"],
    )

    def get_inputs(self, assets: MediaAssets) -> list[str]:
        inputs = [str(assets.audio_path)]
        if assets.cover:
            inputs.append(str(assets.cover))
        return inputs

    def get_filter_graph(self, assets: MediaAssets, duration: float) -> str:
        if assets.cover:
            base = ";".join([
                bg_cover(1,1080,1920,"bg",52,-0.42,0.72),
                square(1,600,"cover"),
                "[cover]fade=t=in:st=1.1:d=0.9:alpha=1[cover_f]",
                "[bg][cover_f]overlay=(W-w)/2:930[v1]",
            ])
        else:
            base = solid(1080,1920,"v1")

        steps = [base]
        steps.append(
            "[0:a]aformat=channel_layouts=mono,"
            "showwaves=s=940x440:mode=p2p:rate=30:colors=0x00E5FFFF,"
            "format=rgba,colorkey=0x000000:0.25:0.12,gblur=sigma=1.1,"
            "fade=t=in:st=0.8:d=1:alpha=1[wave]"
        )
        steps.append(
            "[0:a]aformat=channel_layouts=mono,"
            "showwaves=s=940x440:mode=p2p:rate=30:colors=0x7A00FFFF,"
            "format=rgba,colorkey=0x000000:0.25:0.12,gblur=sigma=10,"
            "fade=t=in:st=0.8:d=1:alpha=1[glow]"
        )
        steps.append("[v1][glow]overlay=(W-w)/2:430[v2]")
        steps.append("[v2][wave]overlay=(W-w)/2:430[outv]")
        return ";".join(steps) + ";" + self._text(assets, 0.8, duration)

    def _text(self, assets, start, end, link_in="[outv]", link_out="[v]"):
        if not self.has_drawtext():
            return f"{link_in}null{link_out}"

        title = self._wrap_text(assets.track_title, 22, 2)
        artist = self._wrap_text(assets.artist_name, 24, 1)
        detail = " · ".join(x for x in [year(assets), genre(assets)] if x)

        title_src = self._drawtext_source(title, "title")
        artist_src = self._drawtext_source(artist, "artist")
        detail_src = self._drawtext_source(detail, "detail")
        common = readable(self)

        return (
            f"{link_in}"
            f"drawtext={title_src}:fontcolor=white:fontsize=64{common}:x=(w-text_w)/2:y=175:enable='between(t,{start},{end})':alpha='{self.get_fade_alpha(start,end,1)}',"
            f"drawtext={artist_src}:fontcolor=0xCFCFCF:fontsize=42{common}:x=(w-text_w)/2:y=330:enable='between(t,{start+0.3},{end})':alpha='{self.get_fade_alpha(start+0.3,end,1)}',"
            f"drawtext={detail_src}:fontcolor=0xAAAAAA:fontsize=28{common}:x=(w-text_w)/2:y=390:enable='between(t,{start+0.6},{end})':alpha='{self.get_fade_alpha(start+0.6,end,1)}'"
            f"{link_out}"
        )
'''

write("polish.py", POLISH)
write("spinner.py", SPINNER)
write("vinyl_sleeve.py", VINYL)
write("neon_pulse.py", NEON)
write("metadata_card.py", METADATA)
write("fade_premium.py", FADE_PREMIUM)
write("poster.py", POSTER)
write("artist_focus.py", ARTIST_FOCUS)
write("cinematic.py", CINEMATIC)
write("waveform_stage.py", WAVEFORM)

registry = TPL / "registry.py"
if registry.exists():
    txt = registry.read_text(encoding="utf-8")

    imports = {
        "VinylSleeveTemplate": "from .vinyl_sleeve import VinylSleeveTemplate",
        "NeonPulseTemplate": "from .neon_pulse import NeonPulseTemplate",
        "MetadataCardTemplate": "from .metadata_card import MetadataCardTemplate",
        "FadePremiumTemplate": "from .fade_premium import FadePremiumTemplate",
        "PosterTemplate": "from .poster import PosterTemplate",
        "ArtistFocusTemplate": "from .artist_focus import ArtistFocusTemplate",
        "WaveformStageTemplate": "from .waveform_stage import WaveformStageTemplate",
    }

    for cls, imp in imports.items():
        if imp not in txt:
            txt = imp + "\n" + txt

    m = re.search(r"(TEMPLATES\s*=\s*\[)(.*?)(\])", txt, flags=re.S)
    if m:
        body = m.group(2)
        for cls in imports:
            if cls not in body:
                body += f"\n    {cls},"
        txt = txt[:m.start(2)] + body + txt[m.end(2):]

    registry.write_text(txt, encoding="utf-8")
    print("patched registry.py best-effort")

print("\nDone.")
print("Backups saved as .py.bak")
