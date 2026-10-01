# Sister Go TUI Plan for Clipped

## Objective
Build a new Go-based sister app in its own project folder, separate from the current Python-heavy Clipped repo, while preserving the workflow that matters most:
- source images from existing files, local paths, URLs, or fetchers
- choose metadata fields and text styling
- build a render sequence with durations, fades, order, and effects
- save audio clip and video output outside the repo in the standard external output folders
- keep the TUI fast and pleasant using Bubble Tea + Lip Gloss + Bubbles

## Core decision
The new app will live in a sibling repo, not inside this repository, for example:
- /Users/rd/Scripts/Riley/clipped-go
- or /Users/rd/Scripts/Riley/clipped-tui

This repo remains the full legacy/experimental system. The new app is the slim, focused production tool.

## Output contract
The Go app must preserve the current Clipped output convention:
- Audio output: ~/Music/clipped/_audio
- Video output: ~/Music/clipped/_video
- Naming: keep the same sanitized basename structure used today to preserve compatibility with existing file organization and automation expectations
- Output paths must be configurable, but default to the same external music/clipped directories
- The app must not write generated files into the repo itself unless the user explicitly overrides the output destination

## Design principles
1. Keep the repo thin: only the app shell, template definitions, source selection logic, render orchestration, and metadata options live in the Go repo.
2. Reuse proven behavior from the existing system where it is stable: image cleanup heuristics, metadata parsing, slug naming, and template structure.
3. Only trigger background cleanup (like rmbg) when the source truly needs it; do not blindly reprocess already-clean transparent images.
4. Make the TUI feel polished and responsive using Bubble Tea and adaptive layouts.
5. Preserve automation viability: CLI flags, presets, and scriptable batches should work alongside the interactive panel-driven UI.

## TUI architecture
Use the production-friendly viewing structure described in the Bubble Tea guidance:
- primary shell view with sections for source, metadata, sequence, review, and render status
- modal dialogs for browse local files, pick templates, and manage preset values
- keyboard-driven navigation with clear focus states and deterministic actions
- background render worker with progress updates and graceful cancellation
- status bar / review summary showing output path, scene count, duration, and render state

### High-level views
- Home / Dashboard
  - quick actions: new project, open preset, render, run preview
- Source Setup
  - existing image
  - local file path
  - remote URL
  - fetch from Metal Archives / metadata fetcher
  - custom asset source map
- Metadata Setup
  - title, artist, year, genre, custom text
  - uppercase/bold/color/font/alignment selection
  - preview text rendered in real time
- Scene Builder
  - asset list
  - per-scene duration
  - fade in/out timing
  - ordering and drag-like reordering
  - optional effects per scene
- Output & Render
  - output path selection
  - template selection
  - render start / preview / export
  - log panel and failure warnings

## Data model
The app should model a single render job as a structured object, not as ad hoc CLI flags.

### Render job
- Job ID
- Output directory
- Base naming slug
- Template profile
- Audio source
- Scene list
- Metadata config
- Render options
- Cleanup policy
- Status

### Scene
- Source type: existing / local / url / fetched
- Source path or URL
- Duration
- Fade in
- Fade out
- Transition / effect type
- Text overlay config
- Optional cover art or logo

### Metadata config
- Title
- Artist
- Year
- Genre
- Custom fields
- Font selection
- Color palette
- Text case transform
- Bold / italic / alignment settings

## Functional requirements
### 1. Asset source selection
- choose from existing images already in a project or library directory
- select a local file path and import it as source material
- accept URL inputs directly
- optionally fetch artist logo or artwork from Metal Archives or similar sources
- allow user to skip cleanup if the image is already transparent or already processed

### 2. Render settings
- choose output path overrides
- set global default fade in / fade out values
- set default image duration
- override duration per scene
- reorder scenes
- add scene-level effects or transitions

### 3. Metadata formatting
- toggle metadata fields on/off
- choose if track title, artist, year, genre, or custom text are displayed
- support formatting such as uppercase, bold, color, font, and layout tweaks
- maintain consistent preview rendering before export

### 4. Automation support
- save presets of common settings
- allow command-line runs for non-interactive batches
- support automation from Swinsian-like input flows or shell scripts
- allow a config file to persist defaults and recent jobs

## Repo split strategy
### Go sister repo will own
- TUI app shell
- state models and presets
- source resolution and import logic
- metadata formatting and preview
- render job builder and scene sequence logic
- shelling out to ffmpeg / other system tools when needed
- external output routines

### Existing Python repo continues to own
- full legacy rendering stack if still needed
- heavy asset-fetch logic and broader template experimentation
- large Node/Remotion implementation if it remains useful for specific projects
- the active working libraries that are not needed in the slim version yet

This keeps the sister repo focused while preserving the original repo as the fallback/legacy environment.

## Build phases
### Phase 1: Project skeleton and TUI shell
- create sibling Go repo
- initialize Go module and standard CLI/TUI structure
- scaffold Bubble Tea app with key navigation and base views
- implement dark theme, focus states, and status bar

### Phase 2: Source management and presets
- implement source picker for local file, URL, and fetcher-based assets
- add config/preset persistence
- add output path defaults and validation

### Phase 3: Metadata and scene builder
- add metadata selection and formatting controls
- add scene sequence editing, durations, fades, ordering, and effects
- add live preview for metadata text overlays

### Phase 4: Render orchestration
- create render job execution layer
- orchestrate ffmpeg rendering and output naming
- generate and save audio clip alongside final video
- add job status and error path handling

### Phase 5: Automation and QA
- CLI invocation support for scriptable runs
- preset-driven batch automation
- smoke tests for naming, output folder creation, and metadata formatting
- ensure no writes happen inside the repo by default

## Risk and constraint handling
- Do not push cleanup policy into every asset; only run rmbg when image analysis says it is needed
- Keep naming stable so old automation continues to work
- Keep the app independent from the heavy Node/Remotion stack unless a later milestone needs it
- Make the TUI responsive even when background processing is active

## Definition of done
The first version of the Go app is complete when all of the following are true:
- a new sibling repo exists and runs as a standalone Go TUI
- the app can build scenes from local files, URLs, and fetched assets
- metadata fields and styling are configurable
- fade timing, duration, ordering, and effects can be edited per scene
- output defaults to the external ~/Music/clipped folders
- render jobs keep the expected naming structure and save both the audio and final clip
- the tool can be run interactively or via CLI presets for automation

## Immediate next step
Create the sibling repo scaffold, define the initial app models, and implement the first interactive views: dashboard, asset source picker, scene builder, and render summary. After that, fill in the metadata styling and render execution layer.

## Build status (2026-08-04)
Implemented at `/Users/rd/Scripts/Riley/clipped-go` (module `clippedtui`):
- Phases 1–4 core complete: TUI shell (dashboard/sources/metadata/sequence/output/render), source resolution (local/URL/Metal Archives fetch + conditional rmbg cleanup), metadata styling + preview, scene builder (duration/fades/order/dup/remove), ffmpeg render + audio clip, config/preset persistence.
- Naming mirrors Python `get_output_path` (`Template ⋅ Artist - Title.ext`); outputs default to external `~/Music/clipped/_audio|_video|_fetched`.
- `go build ./...` and `go test ./...` pass (audio, job, metadata, source, render, ui).
- Remaining: CLI/preset automation entry point (`--render` non-interactive), full template parity with the legacy repo's richer templates, and a `go.work`/workspace entry so gopls resolves the sibling module in VS Code.

## Build status (wizard milestone, 2026-08-04)
- **Guided new-clip wizard** matching `bin/clipped`: audio source menu (Swinsian current track / Finder picker / manual path) → clip window (start → end seconds) → metadata summary (via `ffprobe`: title/artist/album/year/genre/duration) → image setup (cover art incl. folder art + embedded artwork, band logo, band photo, extras — each via Finder / path / URL / Metal Archives fetch) → "Done" builds scenes and opens the metadata editor.
- **Reel/vertical render** now mirrors `reel.py`/`vertical.py`: blurred darkened cover background (gblur + eq), spinning circular record, square-art reveal, band-logo fade, Arial title/artist drawtext at 1080×1920, driven by the clip window; audio is trimmed to `[start,end]` with fades.
- New `internal/audio` package (Swinsian/Finder AppleScript + ffprobe metadata); job gains clip window + scene roles (cover/logo/photo/extra).
- Tests cover the wizard flow, audio metadata parsing (fake ffprobe), clip/scene roles, and the reel filter graph.

## UI milestone (2026-08-04)
- **Header redesign**: ASCII-art CLIPPED banner + tab bar (`dashboard • sources • metadata • sequence • output • render`) inside one rounded bordered box; consistent footer (per-view key hints + a single status bar showing status / job / view / template).
- **Template picker** in the Output view (enter on the Template row or `t`): curated catalog of every **FFmpeg** template from the legacy repo (label, description, aspect); selecting sets the template + canvas. **Remotion templates are deliberately excluded.**
- **`M:SS` time input**: clip window, scene durations/fades, and output defaults accept `0:58` / `1:58` / `1:02:03` (mirrors Clipped `parse_time`); `FormatClock` shows the clip window as a clock.
- New `internal/templates` catalog package; `internal/job/time.go` for parse/format.

## Wizard & UI revamp milestone (2026-08-04)
Per the approved design (`clipped-go/docs/superpowers/specs/2026-08-04-wizard-ui-revamp-design.md`):
- **Render bug fixed**: `RenderVideo`/`RenderAudio` no longer set `cmd.Stdout`/`cmd.Stderr` (conflicted with `StdoutPipe` → "exec: Stdout already set").
- **Responsive centered layout**: `model.uiWidth()` = `clamp(termWidth−6, 60, 120)`; header/panels/status bar scale together; screen centered via `renderScreen`; help wraps at binding boundaries.
- **Semantic colors**: cyan labels, white values, green/dim toggles, blue paths, gold numbers/times, pink templates/cursors across all views.
- **Template-first wizard**: step 0 picks the template (canvas auto-set); `templates.RequiredAssets` maps each template to the assets asked for (Reel → logo+cover).
- **Asset sourcing**: per-asset **Local (auto)** (`audio.FindArtistAssets`: `cover.jpg` in album dir, `logo.png`/`artist.jpg` in parent artist dir) with candidate picker + Finder fallback; **Fetch online (Metal Archives)** with **rmbg only on fetched logos**; **Custom…** (URL/path/Finder).
- **Font picker**: curated overlay fonts + "browse all system fonts" with type-ahead filter; stores `Style.Font` + `Style.FontPath` (drawtext uses the picked font, Arial fallback).
- New `internal/fonts` package; `TextStyle.FontPath`; tests cover asset detection, fonts, template asset mapping, wizard template step, font picker.
