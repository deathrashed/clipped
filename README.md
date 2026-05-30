<div align="center">
  <img src="assets/icon.png" alt="Clipped icon" width="144">

  <h1>CLIPPED</h1>

  <p><strong>Metadata-aware audio clipping and video generation for macOS music workflows.</strong></p>

  <p>
    <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.12+-111111?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.12+"></a>
    <a href="https://ffmpeg.org/"><img src="https://img.shields.io/badge/ffmpeg-required-111111?style=for-the-badge&logo=ffmpeg&logoColor=white" alt="FFmpeg required"></a>
    <a href="https://github.com/remotion-dev/remotion"><img src="https://img.shields.io/badge/Remotion-required-111111?style=for-the-badge&logo=https://raw.githubusercontent.com/remotion-dev/remotion/main/packages/convert/public/pwa-icon-192.png" alt="Remotion required"></a>
    <a href="https://github.com/deathrashed/rmbg"><img src="https://img.shields.io/badge/rmbg-optional-111111?style=for-the-badge&logo=https://raw.githubusercontent.com/deathrashed/rmbg/main/assets/rmbg-icon.png" alt="rmbg optional"></a>
    <a href="https://www.apple.com/macos/"><img src="https://img.shields.io/badge/macOS-automation-111111?style=for-the-badge&logo=apple&logoColor=white" alt="macOS automation"></a>
    <a href="CHANGELOG.md"><img src="https://img.shields.io/badge/version-2.0.0-2563eb?style=for-the-badge" alt="Version 2.0.0"></a>
  </p>

  <p>
    <a href="#quick-start">Quick Start</a> |
    <a href="#examples">Examples</a> |
    <a href="#video-templates">Templates</a> |
    <a href="#keyboard-maestro">Keyboard Maestro</a> |
    <a href="#configuration">Configuration</a>
  </p>
</div>

---

## <img src="https://api.iconify.design/mdi:format-list-bulleted.svg?color=%2311c866" height="22"> Table of Contents

- [Quick Start](#quick-start)
- [Examples](#examples)
- [Interactive Showcase](#interactive-showcase)
- [What It Does](#what-it-does)
- [Core Technologies](#core-technologies)
- [Core Workflows](#core-workflows)
- [Video Templates](#video-templates)
- [Platform Profiles](#platform-profiles)
- [Keyboard Maestro](#keyboard-maestro)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Developer Commands](#developer-commands)
- [Adding a Template](#adding-a-template)
- [Troubleshooting](#troubleshooting)

## <img src="https://api.iconify.design/mdi:rocket-launch-outline.svg?color=%2311c866" height="22"> Quick Start

```bash
git clone https://github.com/deathrashed/clipped.git ~/Scripts/Riley/clipped
cd ~/Scripts/Riley/clipped
cd src/remotion && npm install && cd ..
./install.sh
clipped --version
```

The codebase lives at `~/Scripts/Riley/clipped`. Generated audio and video stay in `~/Music/clipped/_audio` and `~/Music/clipped/_video` so the working tree does not fill up with exports.

<details>
<summary><strong>Installing & Managing Dependencies on macOS</strong></summary>

Clipped relies on several core system and programming environment dependencies. Run these commands to install or repair your local setup:

- **System Packages (Homebrew)**:
  Ensure FFmpeg and yt-dlp are installed:
  ```bash
  brew install ffmpeg yt-dlp
  ```
- **Python Setup (uv)**:
  Clipped uses the high-performance Python tool `uv` to manage environments. If you need to install or update dependencies:
  ```bash
  # Verify uv is installed
  uv --version
  
  # Run doctor checks inside virtualenv
  uv run clipped doctor
  ```
- **Node & Remotion Setup (npm)**:
  Remotion requires Node 16+ and npm. To clean install or resolve version mismatches in the Remotion package:
  ```bash
  cd src/remotion
  rm -rf node_modules package-lock.json
  npm install
  cd ../..
  ```
- **Optional Tools (rmbg)**:
  To strip background colors from logo assets automatically:
  ```bash
  brew install deathrashed/rmbg/rmbg
  ```
</details>

## <img src="https://api.iconify.design/mdi:play-box-multiple-outline.svg?color=%2311c866" height="22"> Examples

The FFmpeg templates are the primary video renderer. The flagship vertical template is the FFmpeg `reel` template, featuring a sequential story (logo reveal -> spinner -> full artwork zoom) with high-energy vertical styling. Remotion is also supported for highly polished visual compositions like `pulse_reel`, `gallery_square`, and `record_square`.

<table>
  <tr>
    <td width="50%" align="center">
      <video src="assets/examples/200-stab-wounds-masters-of-morbidity-reel.mp4" controls muted playsinline width="100%"></video>
      <br>
      <strong>200 Stab Wounds - Masters of Morbidity</strong>
    </td>
    <td width="50%" align="center">
      <video src="assets/examples/suicideboys-paris-reel.mp4" controls muted playsinline width="100%"></video>
      <br>
      <strong>SuicideboyS - Paris</strong>
    </td>
  </tr>
</table>

```bash
clipped video "track.mp3" --template reel --platform instagram --start 2:45 --end 3:45
clipped video "track.mp3" --template gallery_square --platform default --start 0 --end 4:20
```

## <img src="https://api.iconify.design/mdi:television-play.svg?color=%2311c866" height="22"> Web Showcase & Clipper Simulator

Clipped features a premium, local-first **Interactive Web Showcase & Clipper Simulator** located in the [showcase/index.html](showcase/index.html) folder.

* 🚀 **Launch Link**: [Open Showcase in Browser](file:///Users/rd/Scripts/Riley/clipped/showcase/index.html) (Click to open directly)
* 📂 **Manual Access**: Double-click [showcase/index.html](showcase/index.html) in your Finder/File Manager.

### What it is
The showcase is a standalone, offline-friendly HTML portal that provides a visual dashboard of your entire Clipped environment. Because it is built with vanilla CSS/JS, it works entirely offline—no servers or databases needed. You can run it simply by clicking the launch link above or opening the file in your browser.

### Showcase Sections
* **Interactive Clipper Simulator**: A browser-native CLI simulator. Select audio inputs, templates, background settings, and custom overrides (upload your own covers/logos) to generate the exact CLI commands. Click "Run Render Simulation" to watch a live simulated render in the mock terminal, which opens a browser-native preview of the final video.
* **My Video Clips**: Displays all custom vertical and square videos generated and saved to your project directory (`_video/`). These cards include relative player links and the exact CLI commands used to generate them.
* **My Audio Clips**: A library of custom clipped audio tracks saved in your project directory (`_audio/`). Play tracks directly inside the browser.
* **Template Test Renders (Smoke Tests)**: The reference library displaying smoke test videos for all 12 Remotion and FFmpeg templates, along with their command details.

### Synchronization
* **Automatic Sync**: Every time you render a video or clip an audio file using the Clipped CLI, a hook registers the clip in `showcase/clips.json` and updates the database, causing it to appear instantly in your showcase.
* **Manual Sync**: If you manually clean, modify, or add files to the `_audio/` and `_video/` folders, you can rebuild the showcase catalog index by running:
  ```bash
  uv run scripts/sync_showcase.py
  ```

## <img src="https://api.iconify.design/mdi:information-outline.svg?color=%2311c866" height="22"> What It Does

| Area | Details |
| --- | --- |
| Audio clipping | Clip local files or YouTube URLs by seconds or `M:SS` timestamps. |
| Video rendering | Generate Remotion-first reels and square templates, with FFmpeg kept for legacy templates and audio-only exports. |
| Metadata | Reads track, artist, cover art, folder images, and logo assets where available. |
| Platform exports | Apply size, duration, and format profiles for Instagram, TikTok, YouTube, Discord, Twitter/X, Bandcamp, and full-length vertical reels. |
| Automation | Includes Keyboard Maestro macros for Swinsian, Finder, clipboard URLs, and prompt-driven reel creation. |
| Validation | `doctor`, template smoke tests, dry runs, and progress output help catch missing dependencies early. |

## <img src="https://api.iconify.design/mdi:memory.svg?color=%2311c866" height="22"> Core Technologies

### <img src="https://raw.githubusercontent.com/deathrashed/gupload/main/Uploads/Images/remotion-icon.png" height="20"> Programmatic Video Rendering with Remotion

Clipped leverages **[Remotion](https://github.com/remotion-dev/remotion)**, a framework that allows programmatically creating videos in React and TypeScript.
- **Dynamic Waveforms & Visualizers**: Remotion parses custom audio frequency data to drive real-time, canvas-drawn audio waveforms and elements (like `SpectrumBars`, `RadialBars`, and `WaveRibbon`).
- **Headless Chromium Renders**: Render jobs are packaged as props JSON structures inside `src/remotion/` and compiled dynamically. Headless Chromium (running via Puppeteer) renders frame-perfect h264/AAC videos according to platform specifications.

### <img src="https://raw.githubusercontent.com/deathrashed/gupload/main/Uploads/Images/rmbg-icon.png" height="20"> Logo Background Cleaning with rmbg
To ensure brand logos do not overlay with solid backdrops, Clipped integrates with the **[rmbg](https://github.com/deathrashed/rmbg)** command-line background remover tool.
- **Automatic Transparency Processing**: Corner-pixel analysis detects black/white backdrops, stripping solid colors to produce transparent PNGs.
- **Dynamic Asset Staging**: Cleaned logo assets are temporarily staged into the active Remotion job rendering folder, preventing modification of your primary assets.
- **Fail-Safe Fallback**: Skip processing for existing transparent logos, and gracefully fallback to the original logo if cleaning encounters errors.

### <img src="https://api.iconify.design/mdi:apple.svg?color=%23ae42ff" height="20"> macOS Automation via Keyboard Maestro & AppleScript
Clipped is built for speed on macOS by integrating native scripting layers:
- **Swinsian Selected-Track Detection**: AppleScript queries the Swinsian audio player to retrieve track names, artists, playback positions, and local file paths.
- **Global Hotkey Triggers**: Using Keyboard Maestro macros (`macros/`), users can mark start/end timestamps and compile a vertical reel directly from active Swinsian playback or selected Finder elements without manual typing.

### <img src="https://api.iconify.design/simple-icons:ffmpeg.svg?color=%23ae42ff" height="20"> Lossless Metadata-Aware Audio Clipping

Rather than stripping files of their identity, the clipping engine keeps files intact:
- **Artwork & Tag Preservation**: Uses `mutagen` to extract and copy original ID3/FLAC metadata, embedded covers, track numbers, and album tags.
- **Lossless Trimming**: Employs FFmpeg stream copying where possible to prevent re-encoding quality degradation, formatting the output name automatically with the source range (e.g. `(2.41 - 3.06)`).

### <img src="https://api.iconify.design/mdi:share-variant.svg?color=%23ae42ff" height="20"> Platform-Aware Profiles & Target Optimization
A profile engine resolves size, duration, and encoding targets automatically:
- **Dynamic Resolution Adapting**: Handles target aspect ratios (`1:1` for Bandcamp, `9:16` for Instagram/TikTok, `16:9` for YouTube).
- **Smart Bitrate Capping**: Compresses video to meet strict file-size constraints (such as Discord's `<8MB` limit) using dynamic audio/video bitrate adjustments.

## <img src="https://api.iconify.design/mdi:lan.svg?color=%2311c866" height="22"> Core Workflows

### <img src="https://api.iconify.design/mdi:console-line.svg?color=%23ae42ff" height="18"> Interactive TUI

```bash
clipped
```

### <img src="https://api.iconify.design/mdi:music-note.svg?color=%23ae42ff" height="18"> Audio Clip

```bash
clipped audio "track.mp3" 2:45 3:45
clipped audio "https://youtube.com/watch?v=..." 0:30 1:15
```

### <img src="https://api.iconify.design/mdi:video-outline.svg?color=%23ae42ff" height="18"> Video Render

```bash
clipped video "track.mp3" --template reel --platform instagram --start 2:45 --end 3:45
clipped video "track.mp3" --template gallery_square --platform default --style cinematic --waveform bars
clipped video "clip.mp3" --template spinner --platform default
clipped video "track.mp3" --template vertical_wave --platform vertical_full --dry-run
```

### <img src="https://api.iconify.design/mdi:tune-variant.svg?color=%23ae42ff" height="18"> Presets

```bash
clipped --preset instagram
clipped video "track.mp3" --preset instagram
```

## <img src="https://api.iconify.design/mdi:movie-open-outline.svg?color=%2311c866" height="22"> Video Templates

```bash
clipped templates
```

| Name | Label | Size | Best For |
| --- | --- | --- | --- |
| `reel` | Dynamic Reel (Logo -> Spinner -> Artist) | 1080x1920 | vertical flagship vertical reels (Instagram, TikTok, Shorts, `vertical_full`) |
| `pulse_reel` | Pulse Reel | 1080x1920 | Remotion vertical template with rich sequencing, visual accents, and typography |
| `gallery_square` | Gallery Square | 1080x1080 | Polished Remotion square artwork posts and archive clips |
| `record_square` | Record Square | 1080x1080 | Remotion spinning-record posts with radial audio accents |
| `vertical` | Vertical Spinner | 1080x1920 | Classic vertical album-art spinner and square final artwork reveal |
| `vertical_wave` | Vertical Wave | 1080x1920 | Vertical spinner with circular audio-reactive waveform styling |
| `spinner` | Spinner | 1080x1080 | Square rotating record posts and archive clips |
| `waveformbar` | Waveform Bar | 1080x1080 | Square cover panel with live waveform strip |
| `static` | Static Artwork | 1080x1080 | Simple centered album art videos |
| `minimal` | Minimal | 1080x1080 | Dark typographic square layouts |
| `fade` | Fade Sequence | 1080x1080 | Logo, artist image, and cover crossfades |
| `cinematic` | Cinematic | 1920x816 | Wide YouTube/archive style renders |

## <img src="https://api.iconify.design/mdi:cellphone-link.svg?color=%2311c866" height="22"> Platform Profiles

```bash
clipped platforms
```

| Name | Label | Size | Max Duration | Format |
| --- | --- | --- | --- | --- |
| `default` | Default Square | 1080x1080 | none | MP4 |
| `instagram` | Instagram Reel | 1080x1920 | 60s | MP4 |
| `tiktok` | TikTok | 1080x1920 | 60s | MP4 |
| `youtube_shorts` | YouTube Shorts | 1080x1920 | 60s | MP4 |
| `vertical_full` | Vertical Full Length | 1080x1920 | none | MP4 |
| `twitter` | Twitter/X | 1280x720 | 140s | MP4 |
| `discord` | Discord Audio | audio only | none | MP3 |
| `youtube` | YouTube/Archive | 1920x1080 | none | MP4 |
| `bandcamp` | Bandcamp/SoundCloud | 1080x1080 | none | MP4 |

## <img src="https://api.iconify.design/mdi:keyboard-outline.svg?color=%2311c866" height="22"> Keyboard Maestro

Import the main macro bundle:

```bash
open macros/clipped.kmmacros
```

Import the focused Swinsian dynamic reel macro:

```bash
open macros/clipped-swinsian.kmmacros
```

| Macro | Trigger | Purpose |
| --- | --- | --- |
| `Clipped: Interactive Clip & Generate Video` | Palette/manual | Prompt for source, range, template, and platform, then render in Terminal. |
| `Clipped: Mark Start` | `Command-Shift-[` | Mark the current Swinsian playback position. |
| `Clipped: Mark End + Clip` | `Command-Shift-]` | Mark the end position and create the clip. |
| `Clipped: Generate Spinner Video (Last Clip)` | `Command-Shift-V` | Render the latest clip/source with the spinner template. |
| `Clipped: Generate Instagram Reel (Last Clip)` | `Command-Shift-I` | Render the latest clip/source as a dynamic Instagram reel. |
| `Clipped: Clip YouTube URL from Clipboard` | `Command-Shift-U` | Start a YouTube clipping workflow from the clipboard URL. |
| `Utility: Clipped Dynamic Reel` | user-assigned | In the Swinsian group, prompts for start/end and renders the selected track with `reel` + `vertical_full`. |

See [macros/SETUP.md](macros/SETUP.md) for setup notes and customization.

## <img src="https://api.iconify.design/mdi:cog-outline.svg?color=%2311c866" height="22"> Configuration

`~/.config/clipped/config.toml` is created on first run.

```toml
[general]
audio_dir         = "~/Music/clipped/_audio"
video_dir         = "~/Music/clipped/_video"
copy_to_clipboard = true
auto_fade         = true
fade_duration     = 0.5
spinner_speed     = 0.5
default_template  = "gallery_square"
default_platform  = "default"
remotion_style    = "classic"
remotion_motion   = "medium"
remotion_waveform = "radial"
```

Named presets can override the general defaults:

```toml
[preset.instagram]
default_template = "reel"
default_platform = "instagram"

[preset.vertical_full]
default_template = "reel"
default_platform = "vertical_full"
```

## <img src="https://api.iconify.design/mdi:file-tree.svg?color=%2311c866" height="22"> Project Structure

```text
~/Scripts/Riley/clipped/
├── assets/                       # Static shared assets
├── bin/                          # Compiled binaries / wrappers
│   └── clipped
├── config/                       # Configuration templates
│   └── config.example.toml
├── data/                         # Persistent non-code data
│   ├── metadata.json
│   ├── templates.manifest.json
│   └── fixtures/
├── docs/                         # Documentation (including docs/ai/)
├── macros/                       # Keyboard Maestro import bundles
├── media/                        # All media assets
│   ├── examples/                 # Demo reels
│   └── tests/                    # Test fixtures & outputs
├── src/                          # All source code
│   ├── clipped/                  # Python package
│   │   ├── audio.py
│   │   ├── config.py
│   │   ├── main.py
│   │   ├── platforms.py
│   │   ├── remotion_engine.py
│   │   ├── video.py
│   │   └── templates/
│   └── remotion/                 # TypeScript/Remotion React app
│       ├── package.json
│       └── src/
├── tests/                        # Test orchestration & scripts
├── install.sh
└── README.md
```

## <img src="https://api.iconify.design/mdi:code-braces.svg?color=%2311c866" height="22"> Developer Commands

| Command | Purpose |
| --- | --- |
| `clipped doctor` | Verify FFmpeg, config, templates, platform profiles, and paths. |
| `clipped config` | View or update `~/.config/clipped/config.toml`. |
| `clipped test templates` | Smoke-test installed templates against a sample audio file. |
| `clipped remotion studio` | Open Remotion Studio for local template development. |
| `clipped remotion doctor` | Run Remotion typecheck, composition listing, and still smoke render. |
| `clipped batch` | Process directories of audio or video inputs. |
| `clipped watch` | Watch a folder and process new audio files. |
| `clipped docs generate` | Regenerate CLI docs from the current command surface. |

<details>
<summary><strong>Handy CLI Command Cheatsheet</strong></summary>

Here are some helpful development commands for managing, extending, and fixing Clipped:

- **Checking CLI Structure & Code Integrity**:
  ```bash
  ~/Scripts/.config/python/run.sh -m compileall -q src/clipped
  ```
- **Managing Configs**:
  ```bash
  # View active settings
  clipped config
  # Print config schema
  clipped config --schema
  ```
- **Re-generating CLI Documentation**:
  ```bash
  clipped docs generate
  ```
- **Validating Keyboard Maestro Macros**:
  ```bash
  plutil -lint macros/*.kmmacros
  ```
</details>

<details>
<summary><strong>Dependencies & Tooling References</strong></summary>

Refer to these resources for documentation and customization guides:

- **Video Engine**: [Remotion Documentation](https://www.remotion.dev/)
- **Clipping Engine**: [Mutagen ID3/Metadata Docs](https://mutagen.readthedocs.io/)
- **Downloader**: [yt-dlp GitHub Repository](https://github.com/yt-dlp/yt-dlp)
- **Background Cleaner**: [rmbg Background Remover](https://github.com/deathrashed/rmbg)
- **macOS Automation**: [Keyboard Maestro Wiki](https://wiki.keyboardmaestro.com/)
- **Audio Workflows**: [Swinsian AppleScript Support](https://swinsian.com/)
</details>

## <img src="https://api.iconify.design/mdi:plus-circle-outline.svg?color=%2311c866" height="22"> Adding a Template

For Remotion templates, add a manifest entry in `data/templates.manifest.json`, add the React composition in `src/remotion/src/templates/`, and compose from the shared Remotion components. Run `clipped templates`, `cd src/remotion && npm run typecheck`, and a short smoke render.

For legacy FFmpeg templates, create `src/clipped/templates/mytemplate.py`, subclass `VideoTemplate`, implement `get_inputs()` and `get_filter_graph()`, then run `clipped templates` and a short smoke render.

## <img src="https://api.iconify.design/mdi:alert-circle-outline.svg?color=%2311c866" height="22"> Troubleshooting

| Symptom | Check |
| --- | --- |
| `clipped` is not found | Re-run `./install.sh` and confirm `~/Scripts/Riley/clipped/bin` is on `PATH`. |
| Video has no cover/logo | Render from the original source track, not only a flattened MP3 clip, so folder artwork and logo context are available. |
| Reel is trimmed to 60 seconds | Use `--platform vertical_full` for vertical reels without the Instagram/TikTok duration cap. |
| Keyboard Maestro macro fails instantly | Open the macro action and confirm `CLIPPED_BIN` points to `~/Scripts/Riley/clipped/bin/clipped`. |
| FFmpeg hangs or fails | Run `clipped doctor`, then retry with `--dry-run` to inspect the generated FFmpeg command. |
| Remotion render fails before starting | Run `cd src/remotion && npm install`, then `clipped remotion doctor`. |

---

Last updated: 2026-05-26
