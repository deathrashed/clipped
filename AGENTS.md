# Clipped Agent Guide

Clipped is a macOS-first Python CLI for audio clipping, metadata-aware video rendering, platform export profiles, Swinsian workflows, and Keyboard Maestro automation.

This file is the single source of truth for assistant guidance. Claude, Gemini, and other local agents should read this file rather than maintaining tool-specific root notes.

## Tech Stack

- Python 3.12+
- Typer, Rich, and Questionary for the CLI/TUI
- FFmpeg and ffprobe for audio/video processing
- yt-dlp for YouTube ingestion
- Mutagen for metadata and embedded artwork
- Keyboard Maestro, AppleScript, and Swinsian for macOS automation

## Repository Map

- `clipped_src/`: Python package and CLI implementation.
- `clipped_src/main.py`: Typer CLI entry point and interactive TUI.
- `clipped_src/audio.py`: local/YouTube clipping plus Swinsian mark-start/mark-end helpers.
- `clipped_src/video.py`: video render coordinator.
- `clipped_src/config.py`: config loading, migration, presets, and output path checks.
- `clipped_src/platforms.py`: export profiles such as Instagram, TikTok, YouTube, Discord, and `vertical_full`.
- `clipped_src/templates/`: FFmpeg template modules discovered by `templates/registry.py`.
- `clipped_src/utils.py`: metadata, artwork/logo discovery, time parsing, and output-name sanitizing.
- `bin/clipped`: local executable wrapper.
- `macros/`: Keyboard Maestro import bundles.
- `docs/`: architecture and generated CLI reference.
- `assets/`: README icon and committed demo media.
- `scripts/`: maintenance and generation helpers.
- `tests/`: local smoke/validation scripts.

## Template System

Templates subclass `VideoTemplate`, set `TemplateInfo`, and are discovered dynamically through `clipped_src/templates/registry.py`.

Active templates:

- `reel`: dynamic logo, spinner, metadata text, and final square-art reveal for vertical reels.
- `vertical`: classic vertical spinner and square final artwork reveal.
- `vertical_wave`: vertical spinner with circular waveform styling.
- `spinner`: square rotating record.
- `waveformbar`: square cover panel with waveform strip.
- `static`: static centered artwork.
- `minimal`: dark typographic layout.
- `fade`: image crossfade sequence.
- `cinematic`: wide Ken Burns-style render.

## Generated Output

Generated clips belong outside the repository by default:

- `~/Music/clipped/_audio`
- `~/Music/clipped/_video`

Do not add `_audio/`, `_video/`, `.venv/`, `__pycache__/`, `.DS_Store`, `.specstory/`, `.vscode/`, or local assistant state to version control.

`assets/examples/` is the exception for committed README demo videos.

## Repository Notes

- `macros/clipped.kmmacros` is the main Keyboard Maestro bundle.
- `macros/clipped-swinsian.kmmacros` is the focused Swinsian selected-track dynamic reel import.
- Keyboard Maestro files are plist XML; validate them with `plutil -lint`.
- FFmpeg filter graph changes need real short render checks, not only Python syntax checks.
- If changing package layout, prefer the standard `src/clipped/` layout. Do not rename the package itself to `src`.

## Validation

Use these checks after source or macro changes:

```bash
python3 -m compileall -q clipped_src
plutil -lint macros/*.kmmacros
./bin/clipped doctor
./bin/clipped templates
./bin/clipped platforms
```

For render-sensitive template changes, run a short real render with a representative audio file and inspect at least one frame near each transition.
