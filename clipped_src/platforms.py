"""
Platform export profiles for Clipped.

Each profile defines the target dimensions, max duration, file size,
and preferred output format for a social/distribution platform.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PlatformProfile:
    name: str                        # Internal key
    label: str                       # Display name
    width: Optional[int]             # None = preserve template size
    height: Optional[int]
    max_duration: Optional[float]    # seconds; None = no limit
    max_size_mb: Optional[float]     # None = no limit
    output_format: str               # "mp4" | "mp3"
    video_codec: str = "libx264"
    audio_codec: str = "aac"
    audio_bitrate: str = "192k"
    crf: int = 23                    # H.264 quality (lower = better)
    ideal_templates: list[str] = field(default_factory=list)
    notes: str = ""


# ── Platform definitions ───────────────────────────────────────────────────────

PLATFORMS: dict[str, PlatformProfile] = {
    "default": PlatformProfile(
        name="default",
        label="Default (1:1 Square)",
        width=1080, height=1080,
        max_duration=None, max_size_mb=None,
        output_format="mp4",
        ideal_templates=["spinner", "static", "minimal", "fade"],
    ),
    "instagram": PlatformProfile(
        name="instagram",
        label="Instagram Reel (9:16)",
        width=1080, height=1920,
        max_duration=60, max_size_mb=None,
        output_format="mp4",
        ideal_templates=["reel", "vertical", "vertical_wave"],
        notes="Clips longer than 60s will be trimmed.",
    ),
    "tiktok": PlatformProfile(
        name="tiktok",
        label="TikTok (9:16)",
        width=1080, height=1920,
        max_duration=60, max_size_mb=None,
        output_format="mp4",
        ideal_templates=["reel", "vertical", "vertical_wave"],
    ),
    "youtube_shorts": PlatformProfile(
        name="youtube_shorts",
        label="YouTube Shorts (9:16)",
        width=1080, height=1920,
        max_duration=60, max_size_mb=None,
        output_format="mp4",
        ideal_templates=["reel", "vertical", "vertical_wave"],
    ),
    "vertical_full": PlatformProfile(
        name="vertical_full",
        label="Vertical Full Length (9:16)",
        width=1080, height=1920,
        max_duration=None, max_size_mb=None,
        output_format="mp4",
        ideal_templates=["reel", "vertical", "vertical_wave"],
        notes="No duration cap. Useful for local exports and long-form vertical reels.",
    ),
    "twitter": PlatformProfile(
        name="twitter",
        label="Twitter / X (16:9)",
        width=1280, height=720,
        max_duration=140, max_size_mb=512,
        output_format="mp4",
        crf=26,
        ideal_templates=["spinner", "static", "minimal"],
    ),
    "discord": PlatformProfile(
        name="discord",
        label="Discord (MP3, <8 MB)",
        width=None, height=None,
        max_duration=None, max_size_mb=8,
        output_format="mp3",
        ideal_templates=[],
        notes="Audio only. Video template is ignored.",
    ),
    "youtube": PlatformProfile(
        name="youtube",
        label="YouTube / Archive (16:9)",
        width=1920, height=1080,
        max_duration=None, max_size_mb=None,
        output_format="mp4",
        crf=18,
        ideal_templates=["cinematic", "fade"],
    ),
    "bandcamp": PlatformProfile(
        name="bandcamp",
        label="Bandcamp / SoundCloud (1:1)",
        width=1080, height=1080,
        max_duration=None, max_size_mb=None,
        output_format="mp4",
        ideal_templates=["static", "minimal"],
    ),
}


def get_profile(name: str) -> PlatformProfile:
    profile = PLATFORMS.get(name)
    if profile is None:
        raise ValueError(
            f"Unknown platform '{name}'. Available: {list(PLATFORMS.keys())}"
        )
    return profile


def list_platforms() -> list[PlatformProfile]:
    return list(PLATFORMS.values())


def suggested_template(platform_name: str) -> str:
    """Return the first ideal template for a platform, or 'spinner' as fallback."""
    profile = PLATFORMS.get(platform_name)
    if profile and profile.ideal_templates:
        return profile.ideal_templates[0]
    return "spinner"
