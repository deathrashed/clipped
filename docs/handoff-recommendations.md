## What needs to be built next — Polish the Existing Web Clipped Workflow

The showcase already has the correct foundation. It is not a static gallery and it should not be redesigned as a media browser.

It is already meant to be a browser-based companion to the Clipped repo:

text choose audio source choose/upload assets set clip range choose template choose platform preview/simulate copy CLI command view generated examples

The next phase should improve and finish the existing workflow rather than replacing it.

---

## Current implementation already present

The page already includes:

text Audio source selector Provided demo audio YouTube URL option Custom local audio upload Start/end range inputs Template selector Platform selector Logo background removal toggle Cover art upload/path override Logo upload/path override Artist image upload/path override Background image/video upload/path override Render simulation terminal Preview video area Generated video showcase Generated audio showcase Template smoke-test showcase CLI command builder Copy command buttons Reference/help section

Do not rebuild these from scratch. Refactor, tighten, and extend them.

---

## Priority 1 — Fix desktop layout scaling

The current site feels like it is stuck in a mobile-style layout on desktop.

The problem is mainly layout density, not the feature set.

Fix:

text Narrow centered container Oversized cards Too much vertical stacking Only 1–2 showcase columns Top nav buttons taking too much space

Desktop should use a wider workstation layout.

Suggested structure:

text ┌────────────────────┬─────────────────────────────────────┐ │ Vertical Sidebar   │ Main Workflow Area                  │ │                    │                                     │ │ Source             │ Existing simulator / builder /      │ │ Assets             │ preview / examples                  │ │ Range              │                                     │ │ Template           │                                     │ │ Platform           │                                     │ │ Preview            │                                     │ │ Export             │                                     │ └────────────────────┴─────────────────────────────────────┘

Desktop CSS target:

css body {   padding: 0; }  .app-shell {   display: grid;   grid-template-columns: 260px minmax(0, 1fr);   min-height: 100vh; }  .container, .main-workspace {   max-width: 1800px;   width: 100%; }

Keep mobile controls large, but desktop controls should be denser.

---

## Priority 2 — Add vertical sidebar navigation

Replace the top button row with a persistent sidebar on desktop.

Sidebar items:

text Clipped Simulator Source Assets Clip Range Template Platform Preview Generated Clips Template Tests CLI Builder Docs GitHub

Mobile should use a hamburger drawer.

The sidebar should highlight the current section while scrolling.

---

## Priority 3 — Improve existing simulator instead of replacing it

The current simulator is the heart of the site.

Improve it into a clearer step-based workflow:

text 1. Source 2. Assets 3. Range 4. Template 5. Platform 6. Preview 7. Command / Export

Keep the existing fields, but group them better.

The user should immediately understand:

text Use Riley's demo audio or upload my own file or paste a YouTube URL then customize images/logos/template/platform

---

## Priority 4 — Make upload controls more visual

Current upload/path fields work, but they are plain form inputs.

Upgrade each asset override into a visual asset card:

text Cover Art Logo Artist Image Background Media

Each card should show:

text Upload button Current filename/path Thumbnail preview Clear button Use default button Accepted file types

For image uploads, show dimensions after selection.

For background media, show whether the file is image or video.

---

## Priority 5 — Finish YouTube URL workflow

The YouTube URL option already exists in the simulator, but it needs real backend processing.

Keep it inside the existing Audio Source section.

Do not make a totally separate app.

Expected flow:

text Audio Source: Use YouTube URL Paste URL Set start/end Choose template/platform/assets Generate

Backend:

text Browser → Netlify Function → yt-dlp → ffmpeg → result file/blob → browser download/preview

Scope:

text single videos only no playlists no accounts/login no background queue UI beyond basic status

Status labels:

text Queued Downloading Extracting Rendering Ready Error

---

## Priority 6 — Make generated clips act as examples/presets

The generated video/audio showcase should stay, but its purpose should be clearer.

Each generated card should have:

text Play/preview Use as preset Copy CLI command Use same template Use same platform Use same timing Download

This makes the showcase useful for visitors who want to generate something similar.

---

## Priority 7 — Improve template selection

The template dropdown already exists, but templates need visual previews.

Add a template picker panel using the existing smoke-test renders.

Each template card should show:

text Template name Preview Renderer: Remotion or FFmpeg Aspect ratio Best platform Short description Use template button

Keep the dropdown for compact/advanced use.

---

## Priority 8 — Improve CLI command builder sync

The command builder already exists and should become the source of truth.

When users change:

text source start/end template platform cover logo artist image background clean-logo style waveform dry-run

the command should update live.

Add:

text Copy command Copy JSON config Open GitHub docs

---

## Priority 9 — Fix mobile vs desktop behavior

Implement proper breakpoints.

Desktop:

text sidebar layout wide workspace multi-column forms dense cards 4–6 card grids where appropriate

Tablet:

text collapsible sidebar 2-column cards stacked simulator sections

Mobile:

text hamburger menu single-column workflow sticky Preview/Generate action bar large tap targets no horizontal overflow

---

## Priority 10 — Small quality fixes

Fix or improve:

text Remove dead Back to README link if it does not work on Netlify Fix oversized spacing on desktop Reduce excessive card height Improve form grouping Make preview area more prominent Make generated command easier to see Add "Reset all" button Add "Load demo" button Add "Random template" button Add "Use selected generated clip as source" button

---

## Success criteria

The finished site should feel like:

text a visual web interface for the Clipped repo

not:

text a generic dashboard a media browser a static showcase

A visitor should be able to:

text open the site pick Riley's demo audio or upload their own optionally paste a YouTube URL upload cover/logo/artist/background assets choose a template choose a platform preview/simulate the result copy the exact CLI command download/generated output when backend support is available
