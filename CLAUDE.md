# Clipped - Media Automation Toolkit

## Overview
Clipped is a high-leverage media toolkit for automated audio clipping, multi-template video generation, platform-aware export, and metadata-aware workflows on macOS.

## Architecture

### Core Modules
- **`clipped_src/main.py`** - CLI entry point with Typer commands
- **`clipped_src/audio.py`** - Audio clipping from files/YouTube URLs
- **`clipped_src/video.py`** - Video generation coordinator
- **`clipped_src/platforms.py`** - Platform export profiles (Instagram, TikTok, etc.)
- **`clipped_src/templates/`** - Video template implementations
- **`clipped_src/config.py`** - Configuration management
- **`clipped_src/utils.py`** - Shared utilities

### Template System
Each video template is a self-contained module in `templates/`:
- `spinner.py` - Rotating record animation
- `fade.py` - Crossfade image sequence
- `static.py` - Centered album art
- `vertical.py` - 9:16 vertical format
- `minimal.py` - Dark gradient with typography
- `cinematic.py` - 21:9 letterbox with Ken Burns

### Platform Profiles
Export configurations in `platforms.py` with dimensions, duration limits, codecs, and suggested templates.

## Key Dependencies
- **FFmpeg** - Video/audio processing engine
- **yt-dlp** - YouTube URL downloading
- **Rich** - Terminal UI and progress bars
- **Typer** - CLI framework
- **Mutagen** - Audio metadata handling

## Development Notes
- Virtual environment in `.venv/`
- Config stored in `~/.config/clipped/config.toml`
- KM macros in `macros/` for hotkey integration
- Training data in `clipped_training_data.jsonl`

## File Structure
```
clipped_src/          # Main Python package
├── main.py          # CLI commands
├── audio.py         # Audio processing
├── video.py         # Video generation
├── platforms.py     # Export profiles
├── templates/       # Video templates
├── config.py        # Configuration
└── utils.py         # Utilities

macros/              # Keyboard Maestro
bin/                 # Executable wrapper
docs/                # Documentation
.claude/             # AI assistant config
```
