# Clipped CLI Reference

## Overview
This document describes the available Clipped commands and example workflows.

## Command groups

- `clipped audio` — clip audio from a file or YouTube URL
- `clipped video` — generate video from audio using templates and platforms
- `clipped templates` — list available video templates
- `clipped platforms` — list supported platform profiles
- `clipped config` — manage Clipped configuration
- `clipped doctor` — run diagnostics and verify the environment
- `clipped test` — run QA smoke tests for templates
- `clipped batch` — process multiple audio files in a directory
- `clipped docs` — generate CLI documentation from live config

## Examples

```bash
clipped --help
clipped audio track.mp3 30 45
clipped video myaudio.mp3 --template spinner --platform default
clipped video vertical myaudio.mp3 --preset instagram
clipped config show
clipped config edit
clipped doctor
clipped test templates sample.mp3 --dry-run
clipped batch video --input-dir ./audio --template spinner --platform default --dry-run
clipped watch --input-dir ./audio --type video --dry-run
clipped docs generate --output docs/CLI.md
```

## Templates and platforms
Use `clipped templates` and `clipped platforms` to see the current available options.

## Configuration
The config file is stored at `~/.config/clipped/config.toml`.

### Config commands
- `clipped config show` — display current settings
- `clipped config edit` — open the config file in your editor
- `clipped config init` — create a default config file if missing
- `clipped config reset` — reset config to defaults

## Notes
- `--dry-run` is supported for batch, test, and docs generation commands.
- Watch mode polls a directory and processes new audio files as they appear.
