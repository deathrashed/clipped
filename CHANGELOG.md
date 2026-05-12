# Changelog

All notable changes to Clipped are documented here.
Format: [Semantic Versioning](https://semver.org/).

---

## [2.0.0] — 2026-05-12

### Added

#### Video Templates (new module: `clipped_src/templates/`)
- **Spinner** (`spinner`) — 1:1 rotating record on black. Refactored into `templates/spinner.py`.
- **Fade** (`fade`) — crossfade image sequence. Refactored into `templates/fade.py`.
- **Static** (`static`) — centered album art. Refactored into `templates/static.py`.
- **Vertical** (`vertical`) — NEW. 9:16 rotating record on blurred art background. For Reels / TikTok.
- **Minimal** (`minimal`) — NEW. Dark gradient canvas with centered artwork and typographic overlay.
- **Cinematic** (`cinematic`) — NEW. 21:9 letterbox with Ken Burns slow zoom. For YouTube / film.
- Template registry (`templates/registry.py`) — single source of truth for all templates.
- Abstract base class (`templates/base.py`) — `VideoTemplate` ABC with shared helpers.

#### Platform Export Profiles (new module: `clipped_src/platforms.py`)
- `default`, `instagram`, `tiktok`, `youtube_shorts`, `twitter`, `discord`, `youtube`, `bandcamp`
- Each profile carries dimensions, max duration, max file size, codec settings, and suggested template.
- `discord` platform routes to audio-only MP3 export (8 MB size warning).
- Platform dimension override: if profile size differs from template native, auto-scales output.

#### Clip Library (new module: `clipped_src/library.py`)
- Append-only JSONL store at `~/.config/clipped/library.jsonl`.
- Tracks: source, timestamps, output paths, artist/album/title, platform, template, date.
- `clipped browse [QUERY]` command with Rich table display and interactive re-render prompt.

#### FFmpeg Progress Bar (new module: `clipped_src/progress.py`)
- Real-time Rich progress bar during video encoding via `-progress pipe:1`.
- Shows percentage, elapsed time, and ETA.
- Replaces silent `subprocess.run(capture_output=True)` that appeared to hang.

#### Named Presets
- `[preset.*]` sections in `config.toml` (e.g. `[preset.instagram]`).
- `--preset NAME` flag on `clipped` and `clipped video` commands.
- Shipped presets: `instagram`, `tiktok`, `archive`, `cinematic`, `discord`.

#### Keyboard Maestro Macro Bundle (`macros/clipped.kmmacros`)
- `⌘⇧[` — Mark Start in Swinsian
- `⌘⇧]` — Mark End + Clip
- `⌘⇧V` — Spinner video from last clip
- `⌘⇧I` — Instagram Reel from last clip
- `⌘⇧U` — Clip YouTube URL from clipboard

#### New CLI Commands
- `clipped templates` — list all video templates with sizes and ideal platforms.
- `clipped platforms` — list all platform profiles with specs.
- `clipped browse [QUERY]` — search clip library.
- `clipped --version` / `clipped -V` — show version.
- `clipped audio --dry-run` / `clipped video --dry-run` — print FFmpeg command, don't run.

#### Small Gems
- **Clip duration warning**: prints a yellow warning for clips > 120s (catches M:SS vs seconds confusion).
- **Timestamp display during preview**: "▶ Playing: 62.4s – 75.2s (12.8s)" shown before `afplay`.
- **Output directory safety check**: warns if configured `audio_dir`/`video_dir` parent doesn't exist (unmounted drive).
- **`spinner_speed`** in config: revolutions/second, default 0.5 (was hard-coded).
- **`default_template`** and **`default_platform`** general config keys.

### Changed
- `video.py` refactored from monolithic class into a thin coordinator delegating to templates + platforms.
- `config.py` extended with `get_preset()`, `validate_output_dirs()`, and full preset support.
- `audio.py` timestamps added to preview loop; library recording added to `_finalize`.
- `main.py` TUI redesigned with richer choices and template/platform pickers.
- Template descriptions surfaced in TUI picker.

### Fixed
- `missing_ok=True` on hotkey state file cleanup (Python 3.8+ guard was incorrect).
- Fade template input index calculation when only some asset types are present.

---

## [1.0.0] — 2026-05-11

Initial release covering audio clipping, Spinner/Fade/Static video generation,
Swinsian hotkey integration, yt-dlp ingestion, and interactive adjust-offset loop.
