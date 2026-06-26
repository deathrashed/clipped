# Clipped Showcase Handoff

## Current Production State

Production is live at:

- https://clipped-showcase.netlify.app
- Production deploy ID: `6a1c88dfef132d752c11c01f`
- Accepted draft deploy ID: `6a1c8800ab8214870e8411b6`
- Build logs: https://app.netlify.com/projects/clipped-showcase/deploys/6a1c88dfef132d752c11c01f

This pass used `showcase/public/wow.html` as the visual reference and refactored the Tool page to be a compact audio editor instead of a template-heavy production studio.

## What Changed

- Kept the `wow.html` dark developer visual system: compact panels, mono labels, green accents, subtle borders, and the same two-column workspace feel.
- Simplified the Tool page left column into three panels:
  - Source + Metadata
  - Waveform + Player + Trim
  - Output
- Moved artist/title metadata directly under source selection.
- Made the waveform the main editor surface:
  - full left-column width
  - 168px high
  - visible selected region
  - visible start/end handles
  - persistent gold playhead line
- Added the visible native editor player directly under the waveform:

```html
<audio id="editor-audio" controls preload="metadata"></audio>
```

- Selecting a library clip now sets `editor-audio.src`, loads the waveform, updates start/end, and updates metadata.
- Removed the default Tool template grid, platform chip grid, large asset section, and fake audio cover preview.
- Replaced Tool template/platform grids with compact dropdowns.
- In Audio MP3 mode, the template dropdown is disabled and the cloud payload sends `template: null`.
- In Video MP4 CLI-only mode, the template dropdown is enabled and Generate routes to Toolkit/docs instead of submitting a cloud render.
- Right rail now focuses on Current Selection, Job Lifecycle, Rendered Output, and Recent Clips.
- Library audio cards keep native audio controls at full card width.

## Verification Performed

- `node --check` on extracted inline JS from `showcase/public/index.html`
- `./scripts/build_showcase.sh`
- `~/Scripts/.config/python/run.sh -m compileall -q src/clipped`
- `plutil -lint macros/*.kmmacros`
- `./bin/clipped doctor`
- `./bin/clipped templates`
- `./bin/clipped platforms`
- `npx --yes netlify-cli status`
- Netlify draft deploy: `https://6a1c8800ab8214870e8411b6--clipped-showcase.netlify.app`
- Netlify production deploy: `https://clipped-showcase.netlify.app`
- Hosted Playwright acceptance on production:
  - loaded 68 audio clips, 17 videos, 12 templates
  - waveform measured 920px x 168px at 1440px viewport
  - playhead was visible at 3px width with 0.85 opacity
  - selected overlay used lightweight `rgba(4, 213, 143, 0.12)`
  - native `#editor-audio` had controls and `preload="metadata"`
  - selecting a real library clip loaded `editor-audio.src`, metadata, trim range, and waveform
  - Generate Audio sent `format: "audio"` and `template: null`
  - rendered output panel showed a native audio control and download link
  - Video MP4 mode enabled the template dropdown and changed Generate to CLI docs
  - Library page rendered 68 native audio players with usable width
  - no page errors during the checked path

## Known Boundaries

- Cloud MP4 rendering remains intentionally disabled. Use the local Clipped CLI for video output.
- Local upload is still preview-only in the browser.
- A headless browser sometimes logs a media `ERR_HTTP2_PROTOCOL_ERROR` while probing audio/video resources; the production acceptance run had no JavaScript page errors.
