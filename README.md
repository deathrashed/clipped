<div align="center">
<h1>📀 CLIPPED</h1>

[![PYTHON](https://img.shields.io/badge/language%20—%20python-black?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FFMPEG](https://img.shields.io/badge/engine%20—%20ffmpeg-black?style=for-the-badge&logo=ffmpeg&logoColor=white)](https://ffmpeg.org/)
[![PLATFORM](https://img.shields.io/badge/System%20—%20macOS-black?style=for-the-badge&logo=apple&logoColor=white)](https://www.apple.com/macos/)
[![VERSION](https://img.shields.io/badge/version-2.0.0-blue?style=for-the-badge)](CHANGELOG.md)

**A high-leverage media toolkit for automated audio clipping, multi-template video generation, platform-aware export, and metadata-aware workflows.**

[Quick Start](#-quick-start) • [Templates](#-video-templates) • [Platforms](#-platform-profiles) • [Presets](#-named-presets) • [Library](#-clip-library) • [Hotkeys](#-keyboard-maestro-hotkeys)

</div>

---

## ⚡ Quick Start

```bash
git clone https://github.com/deathrashed/clipped.git ~/Music/clipped
cd ~/Music/clipped
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
clipped               # interactive TUI
clipped --version     # v2.0.0
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **✂️ Precision Clipping** | Clip audio from local files or YouTube URLs with sample-accurate times |
| **🎬 6 Video Templates** | Spinner, Fade, Static, Vertical (9:16), Minimal, Cinematic — each a self-contained module |
| **📤 8 Platform Profiles** | Instagram, TikTok, YouTube Shorts, Twitter/X, Discord, YouTube, Bandcamp, Default |
| **⚙️ Named Presets** | `--preset instagram` skips all menus and uses the right template + platform |
| **📊 Live Progress Bar** | Real-time FFmpeg encoding progress (no more silent hangs) |
| **🎹 KM Macro Bundle** | Double-click `macros/clipped.kmmacros` — 5 hotkeys, ready to use |
| ** macOS Native** | AppleScript file picker, `afplay` preview, clipboard copy, Swinsian integration |
| **⚡ Dry Run** | `--dry-run` prints the exact FFmpeg command without processing |

---

## 🎬 Video Templates

```
clipped templates
```

| Name | Label | Size | Ideal For |
|------|-------|------|-----------|
| `spinner` | Spinner (Rotating Record) | 1080×1080 | Instagram Feed, Archive, Twitter/X |
| `fade` | Fade (Crossfade Sequence) | 1080×1080 | Full-track previews, Story posts, YouTube |
| `static` | Static (Centered Artwork) | 1080×1080 | Archive uploads, SoundCloud, Bandcamp |
| `vertical` | Vertical Spinner (9:16 Reel) | 1080×1920 | Instagram Reels, TikTok, YouTube Shorts |
| `minimal` | Minimal (Dark Typographic) | 1080×1080 | Twitter/X, Archive, Bandcamp |
| `cinematic` | Cinematic (21:9 Ken Burns) | 1920×816 | YouTube, Video essays, Archive |

---

## 📤 Platform Profiles

```
clipped platforms
```

| Name | Label | Size | Max Duration | Format |
|------|-------|------|--------------|--------|
| `default` | Default (1:1 Square) | 1080×1080 | — | MP4 |
| `instagram` | Instagram Reel (9:16) | 1080×1920 | 60s | MP4 |
| `tiktok` | TikTok (9:16) | 1080×1920 | 60s | MP4 |
| `youtube_shorts` | YouTube Shorts (9:16) | 1080×1920 | 60s | MP4 |
| `twitter` | Twitter / X (16:9) | 1280×720 | 140s | MP4 |
| `discord` | Discord (MP3, <8 MB) | audio only | — | MP3 |
| `youtube` | YouTube / Archive (16:9) | 1920×816 | — | MP4 |
| `bandcamp` | Bandcamp / SoundCloud (1:1) | 1080×1080 | — | MP4 |

---

## ⚙️ Named Presets

Presets in `~/.config/clipped/config.toml` override `[general]` keys:

```toml
[preset.instagram]
default_template = "vertical"
default_platform = "instagram"

[preset.discord]
default_platform = "discord"
```

**Usage:**

```bash
clipped --preset instagram          # TUI with instagram defaults
clipped video track.mp3 --preset instagram   # non-interactive
```

Shipped presets: `instagram`, `tiktok`, `archive`, `cinematic`, `discord`.

---

## 🎹 Keyboard Maestro Hotkeys

```bash
open macros/clipped.kmmacros    # double-click to import all 5 macros
```

| Hotkey | Action |
|--------|--------|
| `⌘⇧[` | Mark start in Swinsian |
| `⌘⇧]` | Mark end + clip immediately |
| `⌘⇧V` | Spinner video from last clip |
| `⌘⇧I` | Instagram Reel from last clip |
| `⌘⇧U` | Clip YouTube URL from clipboard |

See [`macros/SETUP.md`](macros/SETUP.md) for prerequisites and customisation.

---

## 🛠 Key Workflows

### Live clipping (fastest path)
1. Press `⌘⇧[` at the moment you want the clip to start
2. Press `⌘⇧]` when done — clip is processed and copied to clipboard

### Full pipeline
```bash
clipped                     # TUI: choose action, template, platform
```

### Non-interactive
```bash
clipped audio track.mp3 62 75              # clip 62s–75s
clipped video clip.mp3 --template vertical --platform instagram
clipped video clip.mp3 --preset instagram  # same, via preset
clipped video clip.mp3 --dry-run           # preview FFmpeg command
```

---

## 📁 Structure

```
~/Music/clipped/
├── bin/
│   └── clipped                 # Global entry point shim
├── clipped_src/
│   ├── __init__.py             # Package version
│   ├── main.py                 # TUI / Typer CLI entrypoint
│   ├── audio.py                # Audio engine (clipping, hotkeys)
│   ├── video.py                # Video engine (coordinates templates + platforms)
│   ├── library.py              # Clip library (JSONL append-only store)
│   ├── platforms.py            # Platform export profiles
│   ├── progress.py             # FFmpeg progress bar
│   ├── config.py               # XDG config + presets
│   ├── utils.py                # Asset discovery, metadata parsing
│   └── templates/
│       ├── __init__.py
│       ├── base.py             # VideoTemplate ABC
│       ├── spinner.py
│       ├── fade.py
│       ├── static.py
│       ├── vertical.py         # 9:16 for Reels / TikTok
│       ├── minimal.py          # Dark typographic
│       ├── cinematic.py        # 21:9 Ken Burns
│       └── registry.py         # Template registry
├── macros/
│   ├── clipped.kmmacros        # Keyboard Maestro macro bundle
│   └── SETUP.md
├── requirements.txt
├── CHANGELOG.md
└── README.md
```

---

## ⚙️ Configuration

`~/.config/clipped/config.toml` — generated on first run.

```toml
[general]
audio_dir         = "~/Music/clipped/_audio"
video_dir         = "~/Music/clipped/_video"
copy_to_clipboard = true
auto_fade         = true
fade_duration     = 0.5
spinner_speed     = 0.5          # revolutions / second
default_template  = "spinner"
default_platform  = "default"
```

---

## Adding a New Template

1. Create `clipped_src/templates/mytemplate.py` — subclass `VideoTemplate`, set `info = TemplateInfo(...)`, implement `get_inputs()` and `get_filter_graph()`.
2. Add it to `REGISTRY` in `clipped_src/templates/registry.py`.
3. Done — it appears in the TUI, `clipped templates`, and `--template` flag immediately.

---

*Last updated: 2026-05-12 · v2.0.0*
