# Clipped Agent Guide

Clipped is a macOS-first Python CLI for audio clipping, metadata-aware video rendering, platform export profiles, Swinsian workflows, and Keyboard Maestro automation.

This file is the single source of truth for assistant guidance. Claude, Gemini, and other local agents should read this file rather than maintaining tool-specific root notes.

## Tech Stack

- Python 3.12+
- Typer, Rich, and Questionary for the CLI/TUI
- FFmpeg and ffprobe for audio/video processing
- Node, npm, Remotion, React, and TypeScript for primary video rendering
- yt-dlp for YouTube ingestion
- Mutagen for metadata and embedded artwork
- Keyboard Maestro, AppleScript, and Swinsian for macOS automation

## Repository Map

- `src/clipped/`: Python package and CLI implementation.
- `src/clipped/main.py`: Typer CLI entry point and interactive TUI.
- `src/clipped/audio.py`: local/YouTube clipping plus Swinsian mark-start/mark-end helpers.
- `src/clipped/video.py`: video render coordinator.
- `src/clipped/remotion_engine.py`: Python bridge that prepares Remotion render jobs and calls the local Remotion app.
- `src/clipped/config.py`: config loading, migration, presets, and output path checks.
- `src/clipped/platforms.py`: export profiles such as Instagram, TikTok, YouTube, Discord, and `vertical_full`.
- `src/clipped/templates/`: FFmpeg template modules discovered by `templates/registry.py`.
- `src/remotion/`: Remotion app, manifest, React templates, and reusable visual components.
- `src/clipped/utils.py`: metadata, artwork/logo discovery, time parsing, and output-name sanitizing.
- `bin/clipped`: local executable wrapper.
- `macros/`: Keyboard Maestro import bundles.
- `docs/`: architecture and generated CLI reference.
- `assets/`: README icon and committed demo media.
- `scripts/`: maintenance and generation helpers.
- `tests/`: local smoke/validation scripts.

## Template System

Templates are discovered through `src/clipped/templates/registry.py`.

Remotion templates are declared in `data/templates.manifest.json` and rendered by the `src/remotion/` app. FFmpeg templates subclass `VideoTemplate`, set `TemplateInfo`, and live in `src/clipped/templates/`.

Active templates:

- `pulse_reel`: Remotion vertical flagship reel with logo, record motion, metadata, waveform, and cover reveal.
- `gallery_square`: Remotion square artwork presentation inspired by polished blurred-background album posts.
- `record_square`: Remotion square spinning-record composition with radial audio accents.
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

`media/tests/` contains test assets and generated smoke test outputs.

Remotion job assets live under `src/remotion/public/jobs/` only while rendering and must stay ignored. Remotion generated output belongs in the configured video output directory unless the user explicitly passes `--output`.

## Repository Notes

- `macros/clipped.kmmacros` is the main Keyboard Maestro bundle.
- `macros/clipped-swinsian.kmmacros` is the focused Swinsian selected-track dynamic reel import.
- Keyboard Maestro files are plist XML; validate them with `plutil -lint`.
- FFmpeg filter graph changes need real short render checks, not only Python syntax checks.
- Remotion composition IDs must be hyphenated (`gallery-square`), while Clipped template IDs stay underscored (`gallery_square`).
- Remotion package versions should stay pinned and aligned across all `remotion` and `@remotion/*` packages.

## Validation

Use these checks after source or macro changes:

```bash
~/Scripts/.config/python/run.sh -m compileall -q src/clipped
plutil -lint macros/*.kmmacros
./bin/clipped doctor
./bin/clipped templates
./bin/clipped platforms
cd src/remotion && npm run typecheck
cd src/remotion && npm run compositions
cd src/remotion && npm run still:smoke
```

For render-sensitive template changes, run a short real render with a representative audio file and inspect at least one frame near each transition.
