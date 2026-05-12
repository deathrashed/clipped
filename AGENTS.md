# Clipped

macOS media toolkit for automated audio clipping and multi-template video generation.

## Stack

- Python 3.11+ (CLI/TUI via Typer + Rich)
- FFmpeg (encoding, audio/video processing)
- yt-dlp (YouTube audio extraction)
- macOS native (AppleScript file picker, `afplay`, clipboard)

## Commands

| Command | Purpose |
|---------|---------|
| `clipped` | Interactive TUI |
| `clipped --version` | Show version |
| `clipped audio <src> <start> <end>` | Clip audio from file or YouTube URL |
| `clipped video <src>` | Generate video with template/platform |
| `clipped templates` | List video templates |
| `clipped platforms` | List platform profiles |
| `.venv/bin/python -m clipped_src.main --help` | Dev entrypoint |

## Architecture

```
clipped_src/
├── main.py        — CLI/TUI entrypoint (Typer)
├── audio.py       — AudioClipper: clipping, URL download, FFmpeg encode
├── video.py       — Video coordinator: assets → template → platform → FFmpeg
├── templates/     — 9 VideoTemplate subclasses (spinner, fade, vertical, etc.)
├── platforms.py   — PlatformProfile dataclasses (Instagram, TikTok, etc.)
├── progress.py   — FFmpeg progress bar via Rich
├── config.py     — XDG config (config.toml) + presets
└── utils.py       — Metadata parsing (mutagen/ffprobe), asset discovery
```

## Adding a Template

1. Create `clipped_src/templates/mytemplate.py` — subclass `VideoTemplate`, set `info = TemplateInfo(...)`, implement `get_inputs()` and `get_filter_graph()`
2. Add to `REGISTRY` in `clipped_src/templates/registry.py`
3. Done — appears in TUI, `clipped templates`, and `--template` flag

## Adding a Platform

1. Add entry to `PLATFORMS` dict in `clipped_src/platforms.py`
2. Set: `name`, `label`, `width`, `height`, `max_duration`, `output_format`, `crf`

## Config

`~/.config/clipped/config.toml` — `[general]` settings + `[preset.*]` named presets. Shipped presets: `instagram`, `tiktok`, `archive`, `cinematic`, `discord`.

## Issue Workflow

Use GitHub issues. Engineering skills (triage, diagnose, to-issues) are configured via `docs/agents/`.
