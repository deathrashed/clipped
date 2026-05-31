# Clipped Toolkit & Showcase Documentation

Welcome to **Clipped**. This document explains what the toolkit is, how the cloud and local environments differ, and how to maintain the project architecture.

---

## 1. What is Clipped?

Clipped is a dual-environment motion graphics and audio clipping utility:
1. **The CLI Toolkit (Local):** A robust Python and Remotion-powered video generator capable of complex FFmpeg processing, template rendering, and asset extraction.
2. **The Showcase (Cloud):** A Netlify SPA frontend for browsing generated assets, reading documentation, and performing lightweight cloud audio clipping.

---

## Current Status

**Cloud:**
- Audio clipping: Available
- Library: Available
- Showcase: Available
- Downloads: Available
- Video rendering: Coming soon

**Local CLI:**
- Audio clipping: Available
- FFmpeg templates: Available
- Remotion templates: Available
- Asset extraction: Available

## 2. Cloud vs Local Capabilities

To manage serverless limits and AWS dependencies, the capabilities are strictly divided:

| Capability | Cloud (Netlify) | Local (CLI) |
| :--- | :--- | :--- |
| **Audio Clipping (MP3)** | ✅ Available | ✅ Available |
| **Waveform Generation** | ✅ Available (Canvas) | ✅ Available |
| **FFmpeg Video Renders** | ❌ Coming Soon | ✅ Available |
| **Remotion MP4 Renders** | ❌ Coming Soon | ✅ Available |
| **Asset Extraction (rmbg)** | ❌ Local Only | ✅ Available |

> **Note:** Cloud MP4 rendering is currently unavailable. Use the Clipped CLI for video generation.
> Cloud Netlify functions enforce a strict 15-minute execution limit and currently lack the headless Chromium dependencies required for Remotion template execution.

---

## 3. How Rendering Works

### Cloud Audio Rendering Pipeline
1. **Request:** The frontend (`clip-request.js`) validates the requested URL and timing parameters, creates a UUID, and stores the initial job state in Netlify Blobs.
2. **Background Execution:** `clip-job-background.js` takes over. It uses an embedded `yt-dlp` binary to extract the raw audio from the URL.
3. **Processing:** An embedded `ffmpeg` binary trims the track based on start/end parameters and applies a user-provided fade in/out (defaults to 0.3s).
4. **Storage:** The output binary is stored directly into Netlify Blobs with a strict `{ ttl: 3600 }` to prevent memory leaks.
5. **Retrieval:** The frontend polls `clip-status.js` until completion, then streams the file via `clip-download.js`.

### Local Video Rendering Pipeline
1. **Initialization:** The `bin/clipped` executable coordinates Python scripts (`src/clipped/video.py`, `src/clipped/audio.py`).
2. **Rendering:** Calls out to Remotion for heavy Chromium-based composition (`pulse_reel`, `gallery_square`) or uses native FFmpeg filters for hardware-accelerated static renders (`vertical_wave`, `spinner`).

---

## 4. How `clips.json` Works

The showcase gallery is not manually hardcoded. It is fully data-driven.

When you run `uv run scripts/sync_showcase.py`:
1. The script recursively scans the `_audio/`, `_video/`, and `tests/videos/` directories.
2. It filters out broken, local-only paths (e.g., `/tmp/`).
3. It parses the filenames using regex to extract metadata (`template`, `artist`, `title`, `start`, `end`).
4. It generates `showcase/public/clips.json`.
5. The frontend fetches this JSON on load to dynamically build the Library, Showcase, and Smoke Test galleries.

---

## 5. Local Installation

To unlock full video rendering capabilities, install the CLI locally:

### Prerequisites
- Python 3.10+
- Node.js 18+
- FFmpeg (available in PATH)

### Installation
```bash
git clone https://github.com/deathrashed/clipped.git
cd clipped
./install.sh
```

### Core Commands
```bash
# Verify system dependencies
clipped doctor

# View available video templates
clipped templates

# Extract an audio segment
clipped audio "track.mp3" 1:30 2:15

# Render a full video reel
clipped video "track.mp3" --template reel --platform instagram
```

---

## 6. How to Add Templates

1. **Create the Template:** Add your new Remotion composition or FFmpeg command profile to the local source (`tests/videos/remotion` or `tests/videos/ffmpeg`).
2. **Update the Parser:** If the template introduces a new aspect ratio or category, update `sync_showcase.py` mapping rules.
3. **Generate Smoke Tests:** Run the local test suite `clipped video` against your new template.
4. **Sync:** Run `scripts/sync_showcase.py` to ingest the new smoke test MP4 into `clips.json`.
5. **Deploy:** Run `scripts/deploy_showcase.sh` to push the new frontend and binary assets to Netlify.

---

## 7. FAQ & Troubleshooting

**Q: Why does my YouTube cloud extraction fail randomly?**
**A:** Netlify Functions share AWS datacenter IPs. `yt-dlp` requests from datacenters are frequently rate-limited or blocked by YouTube's "Sign in to confirm you're not a bot" protections. Try a shorter clip, an alternate URL, or use the local CLI.

**Q: I deployed new videos but they show up as 404 broken links.**
**A:** Check your `clips.json` payload. If the source file was located in your local `/tmp/` directory when `sync_showcase.py` was run, it will not exist on Netlify. Always stage finalized videos inside the local `_video/` directory before syncing.

**Q: The site is leaking Netlify blob storage quota!**
**A:** Ensure `ttl: 3600` is present on all `store.set()` calls in `clip-job-background.js`. This guarantees transient artifacts are flushed after one hour.

**Q: Can I re-enable Cloud MP4 generation?**
**A:** Only if you refactor the Netlify background function to install Node, run npm installs, and bootstrap headless Chromium. Due to Lambda file-size limitations (50MB zipped), this requires advanced layer/binary management and is currently not supported out-of-the-box.
