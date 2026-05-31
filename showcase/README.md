# Clipped Live Producer & Showcase

Welcome to the official web portal for **Clipped**, a specialized tool for metadata-aware audio clipping and dynamic video rendering.

Live at: [**clipped-showcase.netlify.app**](https://clipped-showcase.netlify.app)

---

## 🚀 Overview
The Clipped Showcase is a **Live Producer** for the **Clipped Ecosystem**. While the core toolkit is a powerful macOS CLI, this web interface allows anyone to generate high-quality audio clips and video reels directly from their browser, powered by a robust serverless backend.

### What it's used for:
*   **Audio Trimming**: High-precision clipping of audio segments from local files or YouTube.
*   **Video Production**: Instantly transforming audio clips into social-media-ready reels and posts.
*   **Professional Branding**: Automating the visual "identity" of a track using metadata and asset discovery.

---

## 🧠 The Clipped Engine: How it Works
The core logic of Clipped (both in the CLI and on this site) is built around **intelligent asset composition**.

### 1. Source Processing & Metadata
Clipped supports **YouTube URLs** and **Local File Uploads**. 
*   **Extraction**: It doesn't just grab the audio; it parses the file's ID3 tags and metadata.
*   **Intelligence**: It automatically identifies the **Title**, **Artist**, and **Album Art** to populate visual overlays without manual input.
*   **Overrides**: You have full control—manually set your own cover, logo, or background if the defaults aren't what you need.

### 2. Visual Asset Composition
Clipped creates complex visual scenes by layering multiple assets:
*   **Album Cover**: The primary visual focus, often used for spinners or panels.
*   **Artist Image**: Often used as a blurred background or a stylized secondary layer.
*   **Artist Logo**: Placed as a professional watermark or branding element.

### 3. Professional Polish with `rmbg`
To ensure logos look professional, Clipped includes **background removal (rmbg)** integration. It can take a square album cover, identify the primary subject, and remove the background to create a **transparent logo** for use in high-end templates like `pulse_reel`.

### 4. Output Versatility
*   **Audio Clips**: Clean, trimmed MP3s for sampling or sharing.
*   **Video Templates**: A diverse registry of visual styles:
    *   `reel`: Vertical flagship with dynamic metadata and reveals.
    *   `gallery_square`: Polished, blurred-background album posts.
    *   `metal_vhs`: Gritty, retro-inspired aesthetic with scanlines.
    *   `record_square`: Dynamic spinning record with audio waveforms.

---

## 🛠 Technical Architecture

### 1. Frontend (`showcase/public/`)
Built with **Vanilla JavaScript and CSS** for maximum speed. It communicates with Netlify Functions to trigger and monitor render jobs.
*   **Live Mapping**: Demo selections are mapped to hosted assets for instant backend processing.
*   **Terminal Simulation**: A real-time log that streams actual status updates from the backend engine.

### 2. Backend Functions (`showcase/netlify/functions/`)
A sophisticated serverless pipeline designed to bypass Lambda execution limits.
*   **Binary Manager**: Automatically downloads static Linux builds of **FFmpeg** and **yt-dlp** to `/tmp` on demand.
*   **Netlify Blobs**: Uses persistent storage to manage job parameters, status, and the final generated media.

---

## 📦 Relationship to the Core Repo
The `showcase/` directory is an **isolated web port** of the larger Clipped project. While the website provides public access, the full repository is a comprehensive toolkit for professional music workflows on macOS.

### Core Toolkit Features:
*   **High-Precision Audio Clipping**: The primary engine for extracting lossless segments from local files or YouTube, preserving all ID3/FLAC metadata.
*   **Intelligent Asset Discovery**: Automatically scans directories for `Artist.jpg`, `Logo.png`, and `Cover.jpg` to build visual scenes without manual config.
*   **Pro-Level Background Removal**: Integrated with **`rmbg`** to instantly strip backgrounds from logos for clean, transparent overlays.
*   **macOS Deep Integration**: Includes **Swinsian** selected-track detection and **Keyboard Maestro** macros for one-click reel creation from your active music player.
*   **Interactive TUI**: A full terminal user interface (`clipped`) for bulk processing and template management.
*   **Remotion & FFmpeg Hybrid**: Combines the raw power of FFmpeg for fast renders with the pixel-perfect React-based composition of Remotion.

---

## 🔄 Deployment & Sync Workflow
The showcase is designed to stay perfectly in sync with your local Clipped environment. The deployment process is automated through a series of specialized scripts.

### 1. The Trigger: `deploy_showcase.sh`
Located at the repo root, this script is your one-stop command for going live.
*   **Action**: Navigates to the `showcase/` base directory and runs `npx netlify deploy --build --prod`.
*   **Efficiency**: It leverages Netlify's **delta upload** system, pushing only the changes (new clips or UI tweaks) to ensure lightning-fast updates.

### 2. The Stager: `build_showcase.sh`
Triggered by the Netlify deployment, this script prepares the production environment.
*   **Asset Collection**: It crawls your local repository and stages the following into the `dist/` folder:
    *   `_audio/` and `_video/`: Your actual generated media.
    *   `assets/`: Branding and UI icons.
    *   `tests/videos/`: Reference smoke test renders for the Library tab.
*   **Isolation**: It ensures that only the necessary public assets are uploaded, keeping the private CLI code safe.

### 3. The Brain: `sync_showcase.py`
The most critical part of the build, this Python script rebuilds the showcase "database".
*   **Media Crawling**: It scans your media folders and parses filenames (e.g., `Reel ⋅ Artist - Title (2.41 - 3.06).mp4`) into structured metadata.
*   **Database Generation**: It generates `clips.json` and `clips-list.js` which power the frontend gallery and filtering.
*   **HTML Injection**: It dynamically injects static HTML cards for every clip directly into `index.html`, ensuring the site is fast and SEO-friendly even without a database.
*   **Option Mapping**: It updates the "Simulator" dropdowns so your latest audio clips are immediately available as sources.

### 🚀 How to Sync
Simply run the following from your terminal:
```bash
./scripts/deploy_showcase.sh
```
This single command handles the sync, the build, and the global deployment to [**clipped-showcase.netlify.app**](https://clipped-showcase.netlify.app).
