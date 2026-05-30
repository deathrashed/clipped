# Remotion-First Clipped Implementation Summary

## Overview

Clipped now has a Remotion-first video rendering system while preserving the existing FFmpeg renderer for legacy templates and Discord/audio-only exports.

The architecture is intentionally hybrid:

- Python still owns the CLI/TUI, metadata extraction, platform profiles, output paths, audio prep, and macOS automation.
- Remotion owns the richer visual rendering layer for new templates.
- FFmpeg remains available for existing templates and utility audio/video operations.

All implementation files live inside `/Users/rd/Scripts/Riley/clipped`. Generated videos still go to configured output directories such as `~/Music/clipped/_video`, unless the user explicitly passes `--output`.

## What Was Added

### Remotion App

Added a top-level Remotion project at `src/remotion/`.

Important files:

- `src/remotion/package.json`: pinned Remotion, React, TypeScript, and related creative packages.
- `src/remotion/package-lock.json`: locked npm dependency graph.
- `src/remotion/remotion.config.ts`: Remotion defaults for codec/image behavior.
- `src/remotion/tsconfig.json`: strict TypeScript config.
- `src/remotion/templates.manifest.json`: shared cross-language template manifest.
- `src/remotion/src/index.ts`: Remotion entrypoint.
- `src/remotion/src/Root.tsx`: registers all Remotion compositions.
- `src/remotion/src/default-props.json`: safe preview/default props.
- `src/remotion/src/types.ts`: TypeScript props/types contract.

The first three Remotion templates are:

- `pulse_reel`: vertical reel template.
- `gallery_square`: polished square artwork presentation.
- `record_square`: square spinning-record template with radial audio accents.

Their React implementation files live in:

- `src/remotion/src/templates/PulseReel.tsx`
- `src/remotion/src/templates/GallerySquare.tsx`
- `src/remotion/src/templates/RecordSquare.tsx`

Reusable Remotion components live in `src/remotion/src/components/`:

- `Artwork.tsx`: blurred background, framed artwork, circular record artwork.
- `AudioLayer.tsx`: renders prepared audio.
- `Metadata.tsx`: title/artist/album/year/genre text blocks and lower-third metadata.
- `Texture.tsx`: grain/texture overlay.
- `Waveform.tsx`: bars, ring, and radial audio-reactive visualizers.
- `Stage3D.tsx`: placeholder visual stage wrapper for cinematic/3D-style compositions.

Shared helper modules live in `src/remotion/src/lib/`:

- `palette.ts`: palette resolution and motion factors.
- `text.ts`: metadata text cleanup/formatting helpers.

## Python Integration

### Render Bridge

Added `src/clipped/remotion_engine.py`.

This file is the Python-to-Remotion bridge. It:

- Creates a temporary Remotion job directory under `src/remotion/public/jobs/`.
- Prepares audio with FFmpeg into a render-ready `audio.wav`.
- Applies start/end trimming and fade-in/fade-out before Remotion sees the audio.
- Copies cover/logo/artist/extra image assets into the job directory.
- Writes a props JSON file for Remotion.
- Invokes `npx --no-install remotion render`.
- Cleans up job files after successful render unless `CLIPPED_KEEP_REMOTION_JOBS=1` is set.
- Supports `--dry-run` by printing the FFmpeg prep command and Remotion render command.

Important detail: asset staging uses plain file-content copy instead of metadata-preserving copy, because macOS/external-drive file flags caused copy permission errors.

### Render Coordinator

Updated `src/clipped/video.py`.

`process_video()` now works as a coordinator:

1. Resolve media assets and metadata.
2. Load config and platform profile.
3. Calculate/clamp duration.
4. Use FFmpeg immediately for `mp3`/Discord exports.
5. Instantiate the selected template.
6. If `template.info.engine == "remotion"`, dispatch to `render_remotion_video()`.
7. Otherwise, run the existing FFmpeg filter-graph path.

This preserves existing behavior for legacy templates while making Remotion the normal path for new templates.

### Template Registry

Updated `src/clipped/templates/base.py` and `src/clipped/templates/registry.py`.

`TemplateInfo` now supports:

- `engine`
- `category`
- `composition_id`
- `capabilities`
- `options`
- `defaults`

The registry now loads:

- Existing FFmpeg `VideoTemplate` subclasses from `src/clipped/templates/`.
- Remotion metadata-only templates from `src/remotion/templates.manifest.json`.

Remotion templates are manifest-driven. They do not need Python subclasses.

Important naming detail:

- Clipped template IDs stay underscored, for example `gallery_square`.
- Remotion composition IDs must be hyphenated, for example `gallery-square`.

The manifest maps between those two names.

### CLI And TUI

Updated `src/clipped/main.py`.

The user does not normally choose a render engine. They choose templates and options. The selected template decides whether it uses Remotion or FFmpeg.

The TUI now:

- Shows Remotion templates first.
- Groups legacy FFmpeg templates separately.
- Prompts for Remotion options only when the selected template supports them.
- Keeps existing video/audio workflows intact.

New Remotion-related CLI options were added to `clipped video`:

- `--style`
- `--motion`
- `--waveform`
- `--palette`
- `--scene-pack`
- `--effects`
- `--captions`
- `--seed`

Example commands:

```bash
clipped video track.mp3 --template pulse_reel --platform instagram
clipped video track.mp3 --template gallery_square --platform default --style cinematic --waveform bars
clipped video track.mp3 --template record_square --platform bandcamp --waveform ring
clipped video track.mp3 --template spinner --platform default
```

### Remotion Commands

Added `src/clipped/remotion_cmd.py`.

New commands:

```bash
clipped remotion install
clipped remotion studio
clipped remotion doctor
```

`clipped remotion doctor` runs:

- Remotion TypeScript typecheck.
- Composition listing.
- Still-render smoke test.

### Doctor / QA / Batch / Watch

Updated:

- `src/clipped/doctor.py`
- `src/clipped/qa.py`
- `src/clipped/batch.py`

`clipped doctor` now checks:

- Node
- npm
- npx
- Remotion app existence
- installed Remotion package version
- one-frame Remotion still render

Batch/watch video flows can pass basic Remotion options.

Template QA now uses the shared default-platform resolver so Remotion templates are tested against sensible platforms.

## Defaults And Presets

Updated:

- `src/clipped/config.py`
- `config.example.toml`
- `src/clipped/platforms.py`

New defaults:

- `default_template = "gallery_square"`
- `default_platform = "default"`

New Remotion config keys:

- `remotion_style`
- `remotion_motion`
- `remotion_waveform`
- `remotion_palette`
- `remotion_scene_pack`
- `remotion_effects`
- `remotion_captions`
- `remotion_fps`

Preset changes:

- `instagram`, `tiktok`, `youtube_shorts`, `vertical_full` now use `pulse_reel`.
- `archive` now uses `gallery_square`.
- `waveformbar` now uses `record_square`.
- Discord remains audio-only.
- Legacy templates are still selectable directly.

Platform profile suggestions now prefer Remotion templates, while keeping old FFmpeg templates as fallback choices.

## Docs And Repo Guidance

Updated:

- `.gitignore`
- `AGENTS.md`
- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/CLI.md`

`.gitignore` now ignores:

- `.cache/`
- `src/remotion/node_modules/`
- `src/remotion/out/`
- `src/remotion/dist/`
- `src/remotion/public/jobs/`

`AGENTS.md` now documents Remotion as part of the tech stack, explains the manifest-driven template system, and lists Remotion validation commands.

`docs/ARCHITECTURE.md` now includes ADR-0011 for Remotion-first rendering.

## How A Remotion Render Works

For a command like:

```bash
clipped video track.mp3 --template gallery_square --platform default --start 0 --end 10
```

the flow is:

1. Python resolves metadata and assets through `MediaAssets`.
2. `process_video()` loads `gallery_square` from the registry.
3. The registry identifies it as `engine = "remotion"`.
4. Python calculates platform dimensions and duration.
5. `remotion_engine.py` creates a job directory.
6. FFmpeg prepares a trimmed/faded `audio.wav`.
7. Cover/logo/artist images are copied into the job directory.
8. Python writes `props.json`.
9. Python calls:

```bash
npx --no-install remotion render src/index.ts gallery-square output.mp4 --props props.json ...
```

10. Remotion renders the MP4.
11. Python copies the output path to clipboard and sends macOS notification as before.
12. Job assets are cleaned up.

## Props Contract

The props JSON includes:

- `version`
- `templateId`
- `compositionId`
- `platformName`
- `width`
- `height`
- `fps`
- `durationSeconds`
- `durationFrames`
- `assets`
- `metadata`
- `audio`
- `options`
- `encoding`

The important nested fields are:

```json
{
  "assets": {
    "audioSrc": "jobs/.../audio.wav",
    "coverSrc": "jobs/.../cover.jpg",
    "logoSrc": "jobs/.../logo.png",
    "artistImageSrc": "jobs/.../artist.jpg",
    "extraImageSrcs": []
  },
  "metadata": {
    "artist": "...",
    "title": "...",
    "album": "...",
    "trackNumber": 1,
    "year": "...",
    "genre": "...",
    "sourceFilename": "..."
  },
  "options": {
    "style": "classic",
    "motion": "medium",
    "waveform": "radial",
    "palette": "auto",
    "scene_pack": "story",
    "effects": "texture",
    "captions": "off",
    "seed": ""
  }
}
```

Remotion uses `staticFile()` to load staged job assets.

## How To Add A New Remotion Template

1. Add an entry to `src/remotion/templates.manifest.json`.
2. Use an underscored Clipped template name, for example `my_new_template`.
3. Use a hyphenated Remotion composition ID, for example `my-new-template`.
4. Create the template React component in `src/remotion/src/templates/`.
5. Register it in the `components` map in `src/remotion/src/Root.tsx`.
6. Reuse shared components from `src/remotion/src/components/`.
7. Add platform profile suggestions in `src/clipped/platforms.py` if it should be recommended.
8. Run validation:

```bash
cd remotion
npm run typecheck
npm run compositions
npm run still:smoke
cd ..
./bin/clipped templates
./bin/clipped video sample.mp3 --template my_new_template --start 0 --end 5
```

For most future templates, Python should not need changes. Add to the manifest, add a React composition, and register it in `Root.tsx`.

## How To Add New Template Options

1. Add the option to the template entry in `src/remotion/templates.manifest.json`.
2. Add a default value under `defaults`.
3. If it is a global default, add it to `src/clipped/config.py` and `config.example.toml`.
4. If the TUI should prompt for it, update `_build_remotion_config()` in `src/clipped/main.py`.
5. Add the prop typing in `src/remotion/src/types.ts`.
6. Consume it in the relevant Remotion component/template.

Good options should be high-level taste controls, not tiny implementation details.

Examples:

- Good: `style = "zine"`
- Good: `motion = "high"`
- Good: `palette = "red"`
- Avoid: `title_y_offset = 1421`

## Validation Performed

These passed:

```bash
python3 -m compileall -q src/clipped
plutil -lint macros/*.kmmacros
./bin/clipped templates
./bin/clipped platforms
./bin/clipped doctor
./bin/clipped remotion doctor
cd remotion && npm install
cd remotion && npm run typecheck
cd remotion && npm run compositions
cd remotion && npm run still:smoke
```

Smoke videos rendered successfully:

```text
~/Music/clipped/_video/remotion-gallery-square-smoke.mp4
~/Music/clipped/_video/remotion-record-square-smoke.mp4
~/Music/clipped/_video/remotion-pulse-reel-smoke.mp4
```

Contact sheets were generated and visually inspected. The engine works, but the current visuals are only first-pass prototypes.

## Known Current Design Issue

The Remotion outputs are functional but not yet visually tuned. They prove the engine, props, audio visualization, asset staging, and render path. They should now be redesigned toward the user’s taste.

Likely next improvements:

- Better typography scale and placement.
- Less generic waveform treatment.
- More tasteful square layouts based on the polished `generic-sq.txt` reference.
- Stronger `pulse_reel` story arc.
- Better intro/outro timing.
- Better palette extraction or curated palettes.
- More aggressive and genre-appropriate metal visual language.
- More polished style variants: `classic`, `brutal`, `neon`, `zine`, `cinematic`.
- Cleaner handling of logos and artist photos.
- Avoid UI-looking panels when the output should feel like a designed music visual.

## Current Dirty Tree Note

The repository was already dirty before this implementation. Existing `_video/tests` deletes/additions and `_audio` artifacts were left alone. The Remotion implementation changed source/docs/config files and added the `src/remotion/` app plus two Python Remotion modules.

---

# Next Handoff: Remotion Visual Engine Roadmap

## Current Direction

The next phase is not just adding premade templates. Build a reusable Remotion visual engine where effects, visualizers, media objects, lyrics, backgrounds, artwork treatments, and scene blocks are shared between templates.

Templates should mostly define layout, timing, and preset defaults. The CLI/TUI should stay preset-first; advanced effect intensity controls should live in Remotion preset/config files.

The current Remotion outputs are functional prototypes and should not be treated as final visual quality.

## User Visual Taste References

Use these reference videos as the visual target language:

- `/Volumes/Eksternal/Audio/Hip-Hop/D/DJ EFN/2015 - Another Time/04. Lane 2 Lane (feat. Don Logan & Denzel Curry).mp4`
  - Square 1080x1080, 30fps.
  - Blurred/zoomed album-art background.
  - Centered cover with rounded corners.
  - White/soft border.
  - Clean, focused, professional card look.
- `/Users/rd/Music/clipped/_video/Cannibal Corpse - Condemnation Contagion reel.mp4`
  - Vertical 1080x1920.
  - Blurred artwork background.
  - Logo/record/cover reveal sequence.
  - Simple centered metadata.
- `/Users/rd/Movies/Ritual Fog - Demented Procession (fire).mp4`
  - Vertical 1080x1920, 60fps.
  - Dark high-contrast procedural fire/smoke scene.
- `/Users/rd/Movies/Leaf Dog - Hide Those Eyes (fluid).mp4`
  - Square 1080x1080, 60fps.
  - Black particle/star field.
  - Metallic fluid/blob center object.
  - Small typography and synced lyric-style lines.

## Inspiration Sources

External reference folder:

```text
/Users/rd/Downloads/remotion-research-inspiration/
```

Important files and folders:

- `summary-handoff.md`
- `en.md`
- `web-assets.md`
- `advanced-remotion-beautiful-elements-code-pack.md`
- `remotion-effects-elements-code-reference.md`
- `remotion-music-elements-pack-v2-advanced-scenes.md`
- `remotion-music-elements-pack-vinyl-lyrics-speakers-genre.md`
- `template.md`
- `waveforms/`
- `remotion-templates.md`
- `SwiftClip/`
- `template-audiogram/`
- `template-music-visualization/`
- `remotion-templates/templates/`

Do not commit the inspiration folder. Use it as reference material only.

## Shared Engine Structure

Intended new Remotion folders:

```text
src/remotion/src/audio/
src/remotion/src/hooks/
src/remotion/src/effects/
src/remotion/src/visualizers/
src/remotion/src/components/music/
src/remotion/src/components/vinyl/
src/remotion/src/components/lyrics/
src/remotion/src/components/speakers/
src/remotion/src/components/media/
src/remotion/src/scenes/
src/remotion/src/presets/
```

Layer model for templates:

```text
Background
Environment FX
Primary Visualizer
Artwork / Media
Reactive FX
Text / Captions / Lyrics
Overlay FX
Post FX
```

## Audio, Visualizers, Effects, And Scene Blocks

Missing reusable systems to build:

- Shared audio core: FFT, RMS, bass/mid/treble bands, windowed analysis, `mapBand()` helpers, fallback synthetic motion.
- Visualizers: bars, mirror spectrum, radial bars, ring, ribbon, oscilloscope, flower, particles, pulse rings, speaker cone.
- Effects: blurred artwork background, bordered artwork card, grain, vignette, scanlines, CRT, VHS, chromatic aberration, beat flash, light sweep, reactive halo, camera shake, film burn, fire/smoke, fluid/blob, particle/star field, neon/aurora/tunnel backgrounds.
- Media objects: vinyl record, spinning CD/disc, half-vinyl card, turntable, album depth stack, record crate, speaker cones, cassette/VU meters.
- Text/lyrics: premium lower third, stacked poster text, reactive glow text, metal title plate, word-highlight lyrics, one-word impact lyrics.

## Assets, Web Media, And YouTube

Future asset priority order:

1. Explicit CLI/config file path or URL.
2. Embedded audio artwork.
3. Album-folder images: `cover`, `front`, `folder`, `artist`, `logo`, booklet/extra images.
4. Cached/downloaded web-selected images.
5. Generated fallback visuals.

Planned options:

- `--cover PATH_OR_URL`
- `--logo PATH_OR_URL`
- `--artist-image PATH_OR_URL`
- `--extra-image PATH_OR_URL`, repeatable
- `--background PATH_OR_URL`
- `--media PATH_OR_URL`, repeatable
- `--media-mode background|overlay|picture_in_picture|gallery|texture|scene_source`

Media support:

- Remote image URLs should download/cache before render.
- Local videos should support `mp4`, `mov`, `mkv`, and `webm`.
- YouTube/video URLs should use `yt-dlp`, cache locally, optionally trim, then pass to Remotion as video assets.
- Remotion should render prepared image/video assets through `staticFile()`, `<Img>`, and `<Video>`.

## Synced Lyrics And Captions

Future support:

- `.lrc`
- `.srt`
- `.vtt`
- JSON timed words/lines
- simple text fallback

Planned options:

- `--lyrics PATH`
- `--captions-file PATH`
- `--captions off|metadata|lyrics|lower_third|impact`

Missing lyrics should fall back to metadata captions without failing the render.

## Logo Background Removal

Use `/Users/rd/Scripts/Riley/rmbg/bin/rmbg` for optional logo background cleanup.

Purpose: online logos often have black/white/solid backgrounds; cleaned transparent PNGs look more professional.

Requirements:

- Never modify originals by default.
- Stage cleaned logo PNGs into Remotion job assets and set `assets.logoSrc` to the cleaned file.
- If image already has alpha, skip cleanup.
- If corner pixels are mostly black or white, auto-select background color.
- If cleanup fails, warn and fall back to the original logo.

Planned options/config:

- `--clean-logo`
- `--logo-bg black|white|auto|#RRGGBB`
- `--logo-fuzz PERCENT`
- `remotion_clean_logos = true`
- `remotion_logo_bg = "auto"`
- `remotion_logo_fuzz = 15`
- `rmbg_path = "/Users/rd/Scripts/Riley/rmbg/bin/rmbg"`

Doctor should eventually check `rmbg_path` and ImageMagick `magick`.

## Template Roadmap

Rebuild existing templates first:

1. `gallery_square`: Lane 2 Lane style, blurred album background, centered rounded bordered cover, subtle shadow, optional folder/web images, optional ribbon/bars.
2. `record_square`: vinyl/CD/spinning media, grooves, radial/ring visualizer, halo, light sweep, metadata.
3. `pulse_reel`: Cannibal-style vertical sequence with blurred art/video background, logo/artist image, spinning media, cover reveal, safe-area metadata, optional lyrics.

Add new templates after shared modules exist:

- `premium_glass`
- `vinyl_share`
- `turntable_square`
- `metal_vhs`
- `crt_scope`
- `fire_scene`
- `fluid_scene`
- `speaker_stage`
- `doom_monolith`
- `black_metal_frost`
- `record_store_share`
- `media_story`
- `youtube_backdrop`

## Manifest Options

Intended future manifest controls:

- `style`: `classic`, `cinematic`, `brutal`, `neon`, `zine`, `doom`, `frost`, `vhs`, `hiphop`
- `waveform`: `none`, `bars`, `mirror`, `radial`, `ring`, `ribbon`, `oscilloscope`, `flower`, `particles`
- `scene_pack`: `art_focus`, `glass`, `vinyl`, `turntable`, `speaker`, `metal`, `fire`, `fluid`, `doom`, `frost`, `record_store`, `lyrics`, `media`
- `effects`: `clean`, `texture`, `grain`, `film`, `crt`, `vhs`, `metal_vhs`, `fire`, `fluid`, `neon`, `doom`
- `captions`: `off`, `metadata`, `lyrics`, `lower_third`, `impact`
- `media_mode`: `background`, `overlay`, `picture_in_picture`, `gallery`, `texture`, `scene_source`

## Extra Toolkit Commands

Planned commands:

- `clipped assets track.mp3`
- `clipped remotion inspect-template TEMPLATE`
- `clipped remotion list-effects`
- `clipped remotion preview-matrix`
- `clipped remotion contact-sheet`
- `clipped remotion render-sample`
- `clipped remotion cache`

## Validation And Acceptance

Expected checks:

```bash
python3 -m compileall -q src/clipped
./bin/clipped doctor
./bin/clipped templates
./bin/clipped platforms
cd remotion && npm run typecheck
cd remotion && npm run compositions
```

Also perform still renders for intro, one-second, midpoint, and outro frames, plus short MP4 smoke renders for each new or rebuilt template.

Visual acceptance:

- Generate contact sheets.
- Compare `gallery_square` against Lane 2 Lane.
- Compare `pulse_reel` against Cannibal Corpse reel.
- Compare `fire_scene` and `fluid_scene` against the provided references.
- Reject blank media, stretched covers, unreadable lyrics, overlapping text, muddy blur, excessive noise, broken artwork framing, or generic UI-looking layouts.

## Important Notes

- Final generated videos should remain in configured output folders unless the user explicitly passes `--output`.
- The worktree is dirty and contains unrelated user/test media changes. Do not revert them.
- Legacy FFmpeg templates remain available.
- Discord/audio-only behavior remains FFmpeg-based.
- Cloud/Lambda/hosted rendering remains out of scope.
- The next agent should implement the shared engine first, then rebuild templates from shared components.

---

# Latest Implementation Progress: Shared Engine Foundation Started

This section records the first implementation pass after the Remotion visual engine plan.

## What Was Added

Added the first reusable Remotion engine modules:

- `src/remotion/src/audio/audio-utils.ts`
  - shared FFT value helpers
  - RMS
  - bass / low-mid / mid / high-mid / treble / full band analysis
  - fallback synthetic audio values
  - power-of-two-safe audio visualization helper
- `src/remotion/src/hooks/useAudioReactive.ts`
  - shared hook for all audio-reactive effects and visualizers
  - uses staged audio when present
  - falls back to `src/remotion/public/silence.wav` for Studio/still/default renders
- `src/remotion/src/effects/Overlays.tsx`
  - `Vignette`
  - `FilmGrain`
  - `Scanlines`
  - `LightSweep`
  - `ReactiveHalo`
  - `BeatFlash`
  - `CameraShake`
  - `PostFxStack`
- `src/remotion/src/visualizers/Spectrum.tsx`
  - `SpectrumBars`
  - `RadialBars`
  - `WaveRibbon`
- `src/remotion/src/components/music/AlbumCard.tsx`
  - `BorderedAlbumCard`
  - `CompactCaption`
- `src/remotion/src/components/vinyl/VinylRecord.tsx`
  - reusable spinning vinyl record with grooves and album-label center
- `src/remotion/src/presets/effects.ts`
  - preset definitions for `clean`, `texture`, `grain`, `film`, `crt`, `vhs`, `metal_vhs`, and `neon`
- `src/remotion/public/silence.wav`
  - tiny silent fallback audio file so Remotion Studio/still renders do not crash when preview props have no staged audio

Also added exact Remotion CLI dependency:

- `@remotion/cli@4.0.468`

Reason: the installed `remotion@4.0.468` package did not expose a CLI binary by itself, so `npm run compositions` and `npx --no-install remotion ...` failed until the matching `@remotion/cli` package was installed.

## Templates Rebuilt In First Pass

Updated `gallery_square` to use shared primitives:

- `BackgroundField`
- `ReactiveHalo`
- `LightSweep`
- `BorderedAlbumCard`
- `CompactCaption`
- `SpectrumBars`
- `WaveRibbon`
- `BeatFlash`
- `PostFxStack`

The goal is now closer to the Lane 2 Lane reference: blurred background, centered bordered artwork card, cleaner metadata, and optional reusable waveform/ribbon treatment.

Updated `record_square` to use shared primitives:

- `BackgroundField`
- `ReactiveHalo`
- `LightSweep`
- `RadialBars`
- `VinylRecord`
- `CompactCaption`
- `SpectrumBars`
- `WaveRibbon`
- `BeatFlash`
- `PostFxStack`

The goal is now a proper reusable vinyl/spinning-media scene rather than one-off circular cover art.

## Manifest And Type Updates

Updated `src/remotion/src/types.ts` with expanded visual style and waveform unions.

Updated `src/remotion/templates.manifest.json` to expose more reusable modes:

- `mirror`
- `ribbon`
- `flower`
- richer effect stacks such as `film`, `crt`, `vhs`, `metal_vhs`, and `neon`
- `shared_effects` capabilities on rebuilt templates

## Validation Performed

Passed:

```bash
python3 -m compileall -q src/clipped
cd remotion && npm run typecheck
cd remotion && npm run compositions
```

Composition listing after the changes:

```text
pulse-reel        30      1080x1920      240 (8.00 sec)
gallery-square    30      1080x1080      240 (8.00 sec)
record-square     30      1080x1080      240 (8.00 sec)
```

Still renders succeeded:

```text
.cache/remotion-smoke/gallery_square_rebuild.png
.cache/remotion-smoke/record_square_rebuild.png
.cache/remotion-smoke/debug_gallery.png
.cache/remotion-smoke/debug_record.png
```

Short MP4 smoke renders succeeded:

```text
.cache/remotion-smoke/gallery_square_rebuild.mp4
.cache/remotion-smoke/record_square_rebuild.mp4
```

Smoke render commands used the Disincarnate test track:

```bash
./bin/clipped video '/Volumes/Eksternal/Audio/Metal/D/Disincarnate/1993 - Dreams of the Carrion Kind/07. Entranced.mp3' --template gallery_square --platform default --start 0 --end 5 --output .cache/remotion-smoke/gallery_square_rebuild.mp4 --waveform ribbon --effects film

./bin/clipped video '/Volumes/Eksternal/Audio/Metal/D/Disincarnate/1993 - Dreams of the Carrion Kind/07. Entranced.mp3' --template record_square --platform default --start 0 --end 5 --output .cache/remotion-smoke/record_square_rebuild.mp4 --waveform flower --effects metal_vhs
```

## Issues Found And Fixed

- `useAudioData()` throws when called with an empty source.
  - Fixed by adding `src/remotion/public/silence.wav` and using it as preview fallback.
- `visualizeAudio()` requires the sample count to be a power of two.
  - Fixed by normalizing requested sample counts in `useAudioReactive()`.
- `npm run compositions` failed because the local Remotion package did not expose a CLI binary.
  - Fixed by installing exact `@remotion/cli@4.0.468`.

## Next Suggested Work

Continue from the reusable engine, not one-off templates:

1. Inspect the new MP4 smoke renders visually and compare against the Lane 2 Lane / Cannibal Corpse references.
2. Tune spacing, text scale, and lower-third behavior in `gallery_square` and `record_square`.
3. Move more current artwork/background logic into shared components.
4. Add album-folder/web asset selection and `rmbg` logo cleanup.
5. Add synced lyrics/captions plumbing.
6. Add the next reusable scene blocks: turntable, CD/disc, speaker cone, fire/fluid scenes.

# Runtime Cleanup Note: Shared uv Python And Remotion Node Modules

The user uses the central Scripts runtime documented at:

```text
/Users/rd/Scripts/.config/README.md
```

That setup is intended to avoid per-project Python virtualenv clutter. The preferred Python runtime path is:

```text
/Users/rd/Scripts/.config/python/run.sh
/Users/rd/Scripts/.config/python/venvs/shared
```

Current Clipped behavior still depends on the repo-local virtualenv because `bin/clipped` runs:

```bash
exec "$REPO_DIR/.venv/bin/python" -m src/clipped.main "$@"
```

So do not delete `/Users/rd/Scripts/Riley/clipped/.venv` until the launcher and related references are changed.

Checked state on 2026-05-29:

- Repo-local `.venv` has Clipped deps installed: `typer`, `rich`, `questionary`, `yt_dlp`, `mutagen`.
- Global/user Python also has those deps installed.
- The central shared uv runtime currently has `mutagen`, but is missing `typer`, `rich`, `questionary`, and `yt_dlp`.

Recommended cleanup path:

1. Add Clipped's Python dependencies to `/Users/rd/Scripts/.config/python/requirements.txt`.
2. Run:

```bash
bash /Users/rd/Scripts/.config/python/setup.sh
```

3. Patch `bin/clipped` to source the shared environment and run through the central uv-managed runtime:

```bash
source "$HOME/Scripts/.config/python/env.sh"
exec "$HOME/Scripts/.config/python/run.sh" -m src/clipped.main "$@"
```

4. Patch `.venv` references in `install.sh`, `README.md`, and `tests/test_all_templates.py`.
5. Validate:

```bash
./bin/clipped doctor
./bin/clipped templates
python3 -m compileall -q src/clipped
```

6. After validation passes, the repo-local `.venv` can be removed.

Important Node note:

- Keep `src/remotion/node_modules` for now.
- The user has global Node/npm through mise, but Remotion package versions are exact and project-local in `src/remotion/package-lock.json`.
- Deleting `src/remotion/node_modules` is safe only as a temporary space cleanup, and Remotion will need `cd remotion && npm install` before rendering again.
