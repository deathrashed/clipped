# Changelog

All notable changes to Clipped are documented here.
Format: [Semantic Versioning](https://semver.org/).

---

## [2.1.0] — 2026-05-13

### Removed
- **Clip library** — `library.py`, `clipped browse` command, and all library references stripped. JSONL history and interactive browse/re-render removed entirely.
- **Interactive preview/offset loop** — removed (was tied to library feature).

### Fixed
- `reel.py` geq mask: replaced `X/2` and `Y` with proper `W/2` and `H` scope constants. Extracted 15+ magic numbers to named constants. Removed Helvetica Neue font. Rewrote `_drawtext_pro` method.
- `vertical_wave.py`: removed unused `duration` parameter from `_drawtext_overlay`.
- `main.py`: fixed indentation corruption in `_interactive_video` source selection block.
- `platforms.py`: YouTube height corrected to 1080 (was 816, breaking 16:9 aspect).
- 13 total bugs across 8 files: undefined variables, wrong method signatures, invalid regex escapes, missing context managers, crash on missing cover art.

### Added
- **macOS notifications** on FFmpeg/audio completion via `osascript`.
- **`--output`/`-o` flag** on both `audio` and `video` commands for custom output paths.
- **`_swinsian_current_track()`** extracted to `audio.py` with 5s timeout and error handling (replaces fragile inline AppleScript in `main.py`).
- Swinsian track shown in TUI source selection.
- `process_clip` / `process_video` accept `output_path` parameter.
- 300s timeout on yt-dlp; zero-length clip raises `ValueError`.

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
