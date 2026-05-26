# Clipped CLI Reference

## Templates

| Name | Label | Size | Ideal For |
| --- | --- | --- | --- |
| cinematic | Cinematic (21:9 Ken Burns) | 1920×816 | YouTube, Video essays, Archive |
| fade | Fade (Crossfade Sequence) | 1080×1080 | Full-track previews, Story posts, YouTube |
| minimal | Minimal (Dark Typographic) | 1080×1080 | Twitter/X, Archive, Bandcamp |
| reel | Dynamic Reel (Logo -> Spinner -> Artist) | 1080×1920 | Instagram Reels, TikTok, YouTube Shorts |
| spinner | Spinner (Rotating Record) | 1080×1080 | Instagram Feed, Archive, Twitter/X |
| static | Static (Centered Artwork) | 1080×1080 | Archive uploads, SoundCloud, Bandcamp |
| vertical | Vertical Spinner (9:16 Reel) | 1080×1920 | Instagram Reels, TikTok, YouTube Shorts |
| vertical_wave | Vertical Wave (9:16 Reel + Circular Wave) | 1080×1920 | Instagram Reels, TikTok, YouTube Shorts |
| waveformbar | Waveform Bar (Live Audio Visual) | 1080×1080 | Instagram Feed, Twitter/X, SoundCloud, YouTube |

## Platforms

| Name | Label | Size | Max Duration | Format |
| --- | --- | --- | --- | --- |
| default | Default (1:1 Square) | 1080×1080 | none | mp4 |
| instagram | Instagram Reel (9:16) | 1080×1920 | 60s | mp4 |
| tiktok | TikTok (9:16) | 1080×1920 | 60s | mp4 |
| youtube_shorts | YouTube Shorts (9:16) | 1080×1920 | 60s | mp4 |
| vertical_full | Vertical Full Length (9:16) | 1080×1920 | none | mp4 |
| twitter | Twitter / X (16:9) | 1280×720 | 140s | mp4 |
| discord | Discord (MP3, <8 MB) | -×- | none | mp3 |
| youtube | YouTube / Archive (16:9) | 1920×1080 | none | mp4 |
| bandcamp | Bandcamp / SoundCloud (1:1) | 1080×1080 | none | mp4 |

## Presets

| Preset | Overrides |
| --- | --- |
| instagram | default_template=reel, default_platform=instagram |
| tiktok | default_template=reel, default_platform=tiktok |
| youtube_shorts | default_template=reel, default_platform=youtube_shorts |
| vertical_full | default_template=reel, default_platform=vertical_full |
| archive | default_template=static, default_platform=default |
| cinematic | default_template=cinematic, default_platform=youtube |
| discord | default_platform=discord |
| waveformbar | default_template=waveformbar, default_platform=default |

## Examples

```bash
clipped --help
clipped audio track.mp3 30 45
clipped video myaudio.mp3 --template spinner --platform default
clipped video myaudio.mp3 --template reel --platform instagram --start 2:45 --end 3:45
clipped video myaudio.mp3 --template reel --platform vertical_full
clipped config show
clipped doctor
clipped test templates sample.mp3 --dry-run
clipped batch video --input-dir ./audio --template spinner --platform default --dry-run
clipped watch --input-dir ./audio --type video --dry-run
```
