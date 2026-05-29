Good. I have a thorough read of the entire codebase. Now producing the audit.I have everything I need. Producing the full audit now.

---

# Clipped — Motion Graphics Audit & Architecture Plan

---

## 1. Repository Audit

### What Exists

**Entry points:** `Root.tsx` → `registerRoot` → 6 `<Composition>` registrations driven by `templates.manifest.json`. Clean.

**Compositions / Templates:**

| ID | File | Aspect | Style intent |
|---|---|---|---|
| `pulse-reel` | PulseReel.tsx | 9:16 | Logo → vinyl spin → framed cover, metadata |
| `gallery-square` | GallerySquare.tsx | 1:1 | Bordered album card, optional artist image swap |
| `record-square` | RecordSquare.tsx | 1:1 | Vinyl record spinning, radial visualizers |
| `fluid-scene` | FluidScene.tsx | 1:1 | Metallic blob, starfield, oscilloscope |
| `metal-vhs` | MetalVHS.tsx | 1:1 | VHS/glitch aesthetic, brutal typography |
| `premium-card` | PremiumCard.tsx | 1:1 | Clean logo → cover reveal, Apple system font |

**Visual/effect components:** Artwork, AudioLayer, Metadata, Stage3D, Waveform, Texture, Captions, AlbumCard, VinylRecord, Overlays, Spectrum.

**Audio pipeline:** `audio-utils.ts` (band extraction, RMS, fallback values), `useAudioReactive.ts` (hook wrapping `@remotion/media-utils`), `lyrics-utils.ts` (LRC/SRT/VTT parser).

**Style/theme:** `palette.ts` (5 named palettes + auto-resolution), `effects.ts` (8 named presets with grain/halo/vignette/scanline values), `motionFactor()`.

**Asset handling:** Entirely via `staticFile()`. No processing pipeline. Single `coverSrc`/`logoSrc`/`artistImageSrc`.

**Reusable abstractions:** `useAudioReactive`, `resolvePalette`, `motionFactor`, `effectPreset`, `cleanText`, `compactMeta`, `analyzeValues`, subtitle parsers. These are genuinely good.

---

### What's Reusable (Keep)

- `useAudioReactive` — solid hook, good band extraction
- `analyzeValues` / `fallbackAudioValues` — correct approach, deterministic seed
- `resolvePalette` / `motionFactor` — correct layering
- `effectPreset` — good intent, wrong values in places
- Subtitle parsers (LRC/SRT/VTT) — complete, keep as-is
- `SpectrumBars` SVG approach — correct choice for Remotion
- `VinylRecord` groove ring loop — technically correct foundation
- `Vignette`, `FilmGrain`, `Scanlines` — correct primitives

---

### What Is Template-Specific (Refactor Out)

Every template embeds its own timing logic, animation constants, layout positioning, font declarations, and post-FX application. There is zero shared scene infrastructure. The timing system (`logoEnd`, `recordStart`, `revealStart`, `coverRevealFrame`, etc.) is fully duplicated and divergent across templates. The font declaration `"Arial, Helvetica, sans-serif"` appears approximately 15 times across the codebase.

---

### What Should Be Deleted

| Component | Reason |
|---|---|
| `Stage3D.tsx` | Not a 3D system. It's a single `perspective(900px) rotateX(8deg)` border div. Delete. |
| `Texture.tsx` | Random dot "grain" is not film grain. Replaced by `FilmGrain` in Overlays. Delete. |
| `NeonTunnel` (Overlays) | YouTube intro template effect. Delete. |
| `StarField` (Overlays) | React screensaver energy. Delete unless used in a specific sci-fi preset. |
| `motionFactor` inside `palette.ts` | Wrong module. Move to `animation/timing.ts`. |

---

### What Should Be Refactored Into Primitives

- `BackgroundField` → `ArtworkBackground` primitive with configurable blur, saturation, brightness, and overlay
- `FramedArtwork`, `RecordArtwork`, `BorderedAlbumCard` → unified `ArtworkFrame` primitive with `shape: "square" | "vinyl" | "circle"` and `frame: "border" | "matte" | "none"`
- Inline timing logic in every template → `useSceneTimeline(fps, durationInFrames)` hook
- All `fontFamily: "Arial..."` references → `typography.ts` token file
- `BeatFlash`, `ReactiveHalo`, `CameraShake` → `audio-reactive/` module with explicit reactivity contracts

---

## 2. Component-by-Component Creative Review

---

### Captions.tsx

**Works:** Multi-format parsing, inline JSON path, timing offset correction. The subtitle infrastructure is genuinely solid.

**Amateur/Generic:**
- `fontFamily: "Arial, sans-serif"` throughout. Every streaming platform uses custom type. Arial is invisible, not minimal.
- `impact` style: 112px white bold uppercase center. This is a meme caption template. Literally the same as auto-generated TikTok captions from 2021.
- `lower_third`: `backdrop-filter: blur(10px)` frosted glass pill. Every React demo app built since 2020 looks like this.
- `lyrics` style: active line large, next line dimmed. Functionally correct but no entrance animation, no character-level timing, no tracking change, no weight shift. Just text that swaps.
- No typeface distinction between title, lyric, and caption contexts.

**What to remove:** `impact` style as implemented. `lower_third` as implemented.

**What to build:** `KineticCaptions` — line-by-line reveal with tracking expand, opacity cascade, optional word-level timing. `EditorialLowerThird` — left-aligned, no pill, color bar instead of glass. Both should accept a typography preset token rather than inline font/size.

**Remotion changes:** Use `interpolate` on `transform: translateY` and `letterSpacing` per active line. No `backdrop-filter` — use a semi-transparent solid or nothing.

---

### AlbumCard.tsx

**Works:** `BorderedAlbumCard` spring reveal is clean. Compositionally sound.

**Amateur/Generic:**
- `background: "rgba(255,255,255,0.9)"` white border is a Spotify embed card. Not cinematic. Not editorial. It's a frontend UI component pretending to be motion graphics.
- `CompactCaption` is Arial + inline styles. No letter spacing. No weight system. Looks like a placeholder.
- Shadow: `0 36px 120px rgba(0,0,0,0.72), 0 0 0 1px rgba(255,255,255,0.15)` — fine but generic.

**What to remove:** `CompactCaption` as a standalone component — absorb into `MetadataBlock`.

**What to build:** `ArtworkFrame` system. The white border should be a configurable frame preset: `matte` (off-white paper), `chrome` (thin metallic), `vinyl-sleeve` (textured dark sleeve peek), `bare` (no frame, artwork bleeds). The frame itself should be a material system component.

---

### VinylRecord.tsx

**Works:** Groove rings with `border: 1px solid rgba(255,255,255,0.045)` — correct subtle approach. Conic gradient specular is a good instinct. Label circle is correctly proportioned.

**Amateur/Cheap:**
- One monolithic 120-line component. No separation of physics, material, label, or specular.
- The conic gradient specular is static relative to the rotation. A real vinyl record's specular highlight stays fixed in world space while grooves rotate underneath. Currently everything rotates together — the "shimmer" goes with the disc, not against it.
- `boxShadow: 0 0 80px ${palette.accent}2f` — the glow behind the record is the single biggest cheap-template tell in the entire project. Colored glows behind circular objects is the YouTube music visualizer cliché of 2018–2022.
- `inset 0 0 45px rgba(255,255,255,0.08)` — barely visible, not doing anything.
- Rotation speed: `33.3 * 6 * motion` RPM → ~200 degrees per second at medium motion. At 30fps that's ~6.6 degrees/frame. Correct RPM for a vinyl is 33.3 RPM = 200 degrees/second. The formula is actually right. Good.
- Label area: no spindle hole detail, no label typography, no paper texture.
- No dust layer. No sleeve peek entering/exiting frame.

**What to build (split into):**

```
VinylDisc         — rotation, groove rings, base material
VinylSpecular     — world-space conic gradient overlay (counter-rotates)
VinylLabel        — label zone with image, optional text, spindle hole detail
VinylDust         — subtle particle layer on surface
VinylSleeve       — sleeve peek entering bottom-right or top-left
VinylReflection   — subtle floor/surface reflection below disc
```

**Kill:** The colored accent glow behind the disc. Replace with a real directional shadow: `0 60px 80px rgba(0,0,0,0.85)`.

---

### Artwork.tsx

**Works:** `BackgroundField` blur + scale-over-time is correct. Fallback to `coverSrc` when no `backgroundSrc` is right.

**Amateur:**
- `filter: blur(28px) brightness(0.42) saturate(0.92)` — the blurred artwork background is correct in principle, but `saturate(0.92)` is almost nothing. Either desaturate more aggressively (0.3–0.5) for cinematic, or keep full saturation for pop styles. 0.92 is indecision.
- Gradient overlay: `radial-gradient(circle at center, rgba(255,255,255,0.06), rgba(0,0,0,0.72))` — the white center brightening is doing the opposite of a real vignette. This makes the composition feel like a spotlight, which is fine only if intentional. Currently applied to all non-brutal styles.
- Drift: `Math.sin(frame / (60 / motion)) * 4 * motion` — extremely gentle. Not perceptible. Either commit to a visible parallax or remove.
- `fontFamily: "Arial, Helvetica, sans-serif"` in the fallback label. Minor but consistent with the problem.

**What to build:** `ArtworkBackground` with a `mode` prop: `"atmospheric"` (strong blur, desaturated, color-graded), `"editorial"` (moderate blur, high contrast), `"minimal"` (black or near-black, no artwork bleed). Background generation should also support a `colorExtracted` prop for a solid-color fallback derived from palette.

---

### AudioLayer.tsx

No creative issues. Thin, correct, fine. Keep.

---

### Metadata.tsx — MetadataBlock

**Works:** Spring reveal, slide-in from below, muted secondary, accent tertiary. Compositionally correct hierarchy.

**Amateur:**
- `fontFamily: "Arial, Helvetica, sans-serif"` — this is the defining problem of the entire project. Every typographic element uses system sans-serif with no deliberate weight, tracking, or size system.
- `fontSize: 72` for title, `42` for artist, `28` for meta — these ratios work but are generic. No scale system, no responsive adaptation.
- `textShadow: "0 8px 28px rgba(0,0,0,0.72)"` — the same shadow value on every text element in the project. It's not wrong but it's not designed.
- `LowerThird` is an absolute bottom-docked pill with `background: palette.panel`. It's a broadcast lower-third from 2004.

**What to build:** Full typography token system. `MetadataBlock` should accept a `typographyPreset` token. `LowerThird` should become `EditorialLowerThird` — left-aligned, accent color bar on left edge, no background panel, text with strong shadow only.

---

### Stage3D.tsx

`perspective(900px) rotateX(8deg)` border box. Not a 3D system.

**Delete it.** If a perspective stage is needed, build `PerspectiveStage` as a layout wrapper with configurable FOV, rotation axes, and depth layering for child elements.

---

### Waveform.tsx

**Works:** Fallback samples using sin/cos are deterministic and look reasonable. `powerOfTwoAtLeast` is correct.

**Amateur:**
- Two separate implementations of essentially the same component (`AudioWaveformBars`/`WaveformBars`, `AudioRadialWaveform`/`RadialWaveform`). The pattern of wrapping a `audioSrc ? AudioX : FallbackX` should be abstracted.
- `idx % 5 === 0 ? palette.accent2 : palette.accent` for visual variety in bars — this is a 2018 audio visualizer pattern. Every 5th bar is a different color. It looks like a progress indicator, not motion graphics.
- `boxShadow: 0 0 ${10 + sample * 18}px ${palette.accent}66` — glow on every bar. This is the glowing bars problem. Generic.
- `Radial` and `RadialWaveform` rotation `frame * 0.12 * motion` is slow and fine, but the bars are identically styled to the linear bars — same glow, same accent2 accent. The radial form should have its own visual treatment.

**What to build:** Waveform should be unified as a single `AudioVisualizer` primitive in `visualizers/` with a `mode` prop and no inline style decisions. Style decisions live in the preset/theme layer, not the primitive. The primitive outputs shape geometry; the theme applies color, opacity, glow weight.

---

### Overlays.tsx

**Works:** `Vignette`, `FilmGrain`, `Scanlines`, `LightSweep`, `PostFxStack` — correct primitives. `BeatFlash` is a good reactive primitive. `CameraShake` wrapper is useful.

**Amateur/Delete:**
- `NeonTunnel` — animated neon rectangle rings. OBS/Twitch stream overlay energy. Delete.
- `StarField` — React screensaver. If you need particles, build a proper `DustParticles` or `AtmosphereLayer` system. Delete `StarField`.
- `ChromaticAberration` — the CSS gradient approach is extremely low fidelity. It looks like a colored overlay, not chromatic aberration. Acceptable as a fallback but needs a proper shader/SVG filter alternative.
- `VHSTears` — the `frame * seed * 0.023` deterministic pattern means tears appear at predictable intervals. It reads as animation loop, not VHS degradation.
- `ReactiveHalo` — `radial-gradient` colored glow scaling with bass. This is the single most overused audio-reactive effect across the entire project. It appears in `RecordSquare`, `GallerySquare`, and is accessible everywhere. The glow-halo-behind-circle-scales-with-bass pattern is the YouTube music visualizer template look. Use it at most once, subtly.
- `FilmBurn` — correct concept, currently unused. Keep.

---

### Spectrum.tsx

**Works:** SVG-based rendering is correct for Remotion. `WaveRibbon`, `Oscilloscope`, `PulseRings` are more interesting than bars.

**Amateur:**
- `SpectrumBars` with `idx % 7 === 0 ? palette.accent2 : palette.accent` accent pattern. Same problem as Waveform bars. The rhythm of color accent should be musically driven (band energy), not index-mod.
- `boxShadow` on every bar — glow. Same note.
- `RadialBars` is decent but the `frame * 0.018` slow rotation has no relationship to audio content. Beat-synced rotation increments would be more compelling.
- `PulseRings` — expanding rings with `audio.bass` driving opacity. Better than most effects. The `i % 2` color alternation is slightly cheap but tolerable.
- `WaveRibbon` — three overlapping lines with different offsets is a genuinely nice effect. The best visualizer in the project.

---

## 3. Motion Architecture Review

### Current Problems

The system mixes **data**, **animation logic**, **layout**, **typography**, **effects**, and **scene orchestration** inside each template component. There is no scene graph, no timing system, no layout engine, no typography token system.

```
PulseReel.tsx currently contains:
  - Logo timing logic
  - Record timing logic
  - Cover reveal timing logic
  - Metadata reveal timing logic
  - Safe zone constant
  - Gradient overlay
  - Layout pixel positions (width * 0.72, height * 0.12, etc.)
  - Font family string
  - WaveformBars placement
  - Captions placement
  - PostFX selection
```

This is one component doing eight jobs. Every template repeats this structure with minor variations.

### Required Splits

**VinylRecord → decomposed:**
```
VinylDisc         props: size, y, motion, audioAnalysis
VinylSpecular     props: size (counter-rotates, world-space fixed)
VinylLabel        props: size, labelScale, imageSrc
VinylDust         props: size, density, opacity
VinylReflection   props: size, floorOpacity
```

**MetadataBlock → decomposed:**
```
TrackTitle       props: text, typographyPreset, revealFrame
ArtistName       props: text, typographyPreset, revealFrame
MetaLine         props: text, typographyPreset
MetadataStack    props: all of above + layout preset
```

**Template → composed from scene modules:**
```
SceneTimeline    hook returning named frame anchors
SceneLayout      component providing absolute positioning grid
SceneBackground  ArtworkBackground + atmospheric layer
SceneForeground  artwork/vinyl/card primitive
SceneTypography  MetadataStack + typography preset
SceneVisualizer  AudioVisualizer + style preset
ScenePostFX      PostFxStack driven by effects preset
```

---

## 4. Expanded Toolkit — What Exists vs What's Needed

| Category | Exists | Missing (Priority) |
|---|---|---|
| **Audio analysis** | Band extraction, RMS, fallback | Beat detection, section detection, transient peak |
| **Layout engine** | None (px values in templates) | `SceneLayout` with named zones |
| **Typography system** | `cleanText`, `compactMeta` | Font tokens, scale system, tracking rules, type presets |
| **Palette system** | 5 palettes + auto | Color extraction from artwork, contrast-safe selection |
| **Effects presets** | 8 presets (grain/halo/vignette) | Full preset objects including typography + layout |
| **Transitions** | None | Blur dissolve, depth parallax, luma fade |
| **Material system** | None | Vinyl, matte, chrome, paper |
| **Camera system** | None (implicit drift in BackgroundField) | Camera drift hook, push/pull, handheld |
| **Atmosphere** | FilmGrain, Vignette | Fog, dust, depth of field approximation |
| **Masking** | None | Shape masks, gradient masks, luma masks |
| **Lighting** | ReactiveHalo (poor) | Ambient, rim, directional, specular sweep |
| **PostFX** | Grain, Vignette, Scanlines, VHSTears, ChromAb | Color grading (CSS filter), halation, bloom |
| **Visualizers** | SpectrumBars, RadialBars, WaveRibbon, Oscilloscope, PulseRings | Minimal line visualizer, environmental visualizer |
| **Asset pipeline** | `staticFile()` only | Color extraction, blur map, artwork processing |
| **Preset system** | `effectPreset()` | Full scene presets (typography + layout + effects + audio reactivity) |
| **Genre system** | None | Genre motion languages |
| **Quality checks** | None | Safe zone, contrast, motion intensity validators |

---

## 5. Audio-Reactive Design Philosophy

### What Should React (and How)

The current system reacts to `bass` for almost everything — the halo, the flash, the blur, the shake. This is the core quality problem. One band driving five simultaneous effects looks like a visualizer, not motion graphics.

**Correct mapping:**

| Signal | Drives | Intensity |
|---|---|---|
| Bass | Subtle bloom/halation expansion | ±5% scale, imperceptible as individual pulses |
| Bass | Vinyl record shadow depth | Shadow softness varies ±10px |
| Bass | Background vignette tightening | ±0.04 opacity |
| RMS | Film grain density | Grain increases with energy, not per-beat |
| RMS | Color grading warmth | Subtle saturation shift at sustained energy |
| Transient/peak | Single-frame light flash | 1–2 frames, very subtle |
| Treble | Oscilloscope strokeWidth | ±1px |
| Mid | Atmosphere particle density | Fog thickness |
| Section change | Camera drift direction change | Slow, over 4–8 seconds |
| Section change | Typography fade/refresh | Metadata crossfade |
| BPM | Subtle background scale pulse | Keyed to actual beat, not continuous |

### What Should Never React

- Typography position (text should not move with bass)
- Typography size (no scaling with audio)
- Layout (elements should not shift reactively)
- Border/frame opacity (frame integrity must be stable)
- Color palette (hue shifts look like a malfunction)
- Camera shake on every beat (looks like a GIF, not cinema)

### What Looks Professional vs Cheap

| Professional | Cheap |
|---|---|
| RMS-driven grain density increase | Constant RGB split |
| Halation radius expands 3% on transient | Neon ring glow scales 30% with bass |
| Camera drift changes direction at section | Camera shakes on every kick |
| Vignette tightens subtly on loud sections | BeatFlash fires on every beat at 0.22 opacity |
| Film grain texture shifts slightly with energy | Radial halo pulses behind every element |
| Oscilloscope line weight varies ±1px | Bars glow bright on every frequency |

### Reusable Audio-Reactive Primitives to Build

```ts
// audio/reactive.ts
useReactiveValue(signal: AudioBand, range: [number, number], smoothing?: number): number
useReactivePulse(threshold: number, decay: number): boolean  // true for N frames after crossing
useReactiveDrift(fps: number): { x: number; y: number }     // slow 2D drift keyed to section energy
useReactiveGrain(rms: number, base: number): number         // grain opacity scaled by energy
```

### Existing Waveform/Spectrum Evolution

- `SpectrumBars` → remain as data primitive, remove inline color/glow decisions
- `WaveRibbon` → keep, add `smoothing` param (lerp between frames)
- `Oscilloscope` → keep, most cinematically appropriate of all current visualizers
- New: `EnergyLine` — single horizontal line whose thickness and opacity track RMS. Invisible as visualizer, just breathes with music.
- New: `MinimalDots` — sparse dots whose position drifts with audio. For atmospheric presets.

---

## 6. Layout, Composition, and Visual Hierarchy

### Current Problem

All templates use absolute pixel positioning relative to width/height with no named zones. `height * 0.64` for metadata position in PulseReel is a magic number. It breaks at non-standard aspect ratios and is invisible in code review.

### Layout System to Build

```ts
// layouts/zones.ts
type LayoutZone = {
  top: number;    // % from top
  left: number;   // % from left
  width: number;  // % width
  height: number; // % height
};

type SceneLayout = {
  artworkZone: LayoutZone;
  titleZone: LayoutZone;
  metaZone: LayoutZone;
  visualizerZone: LayoutZone;
  logoZone: LayoutZone;
  safeArea: { top: number; right: number; bottom: number; left: number }; // % insets
};

const layouts: Record<string, SceneLayout> = {
  "centered":          { ... },   // Everything centered, symmetric
  "editorial-left":    { ... },   // Artwork right 40%, text left-aligned
  "editorial-right":   { ... },   // Mirror
  "lower-third":       { ... },   // Artwork fills, text anchored bottom-left
  "magazine":          { ... },   // Bold title top, artwork 60%, meta below
  "poster":            { ... },   // Full bleed art, title massive, artist small
};
```

### Aspect Ratio Adaptation

Each layout should define values per aspect ratio. A `useLayout(layoutId, width, height)` hook resolves the correct values. No magic numbers in templates.

### Safe Zones

TikTok/Reels: 9:16 with ~15% bottom exclusion zone (UI chrome), ~12% top exclusion zone.
Instagram square: safe area 8% on all sides.
All current templates violate the TikTok bottom safe zone for waveform bars.

---

## 7. Typography System Design

### Core Problem

The project uses `Arial, Helvetica, sans-serif` or `Arial Black` for every typographic element. This is the single highest-impact solvable problem. A font change alone would increase perceived production quality by 40%.

### Font Recommendations

**Primary typefaces (self-hostable, no licensing issues for video):**

| Use | Font | Why |
|---|---|---|
| Cinematic titles | `Inter` variable (tight tracking, -0.03em) | Clean, modern, editorial |
| Aggressive/metal | `Oswald` or `Bebas Neue` | Compressed, uppercase authority |
| Luxury/editorial | `Playfair Display` | High contrast serif, album-liner energy |
| Minimal | `DM Sans` | Neutral without being Arial |
| VHS/retro | `Space Mono` | Monospaced, CRT-coded |
| Lyric/caption | `Inter` semibold | Highly legible at motion |

**Font pairing strategy:** One display face per preset, one body face per preset. Never more than two typefaces in a scene. The display face handles track title; body face handles artist/metadata.

### Type Scale System

```ts
// typography/scale.ts
type TypeScale = {
  trackTitle: { size: number; weight: number; tracking: number; transform: "uppercase" | "none" };
  artistName: { size: number; weight: number; tracking: number; transform: "uppercase" | "none" };
  albumMeta:  { size: number; weight: number; tracking: number; transform: "uppercase" | "none" };
  lyricLine:  { size: number; weight: number; tracking: number; lineHeight: number };
  lowerThird: { size: number; weight: number; tracking: number };
};

// Sizes expressed as % of min(width, height) — responsive
const cinematic: TypeScale = {
  trackTitle: { size: 0.065, weight: 700, tracking: -0.02, transform: "none" },
  artistName: { size: 0.038, weight: 400, tracking: 0.06, transform: "uppercase" },
  albumMeta:  { size: 0.024, weight: 400, tracking: 0.10, transform: "uppercase" },
  lyricLine:  { size: 0.042, weight: 600, tracking: 0, lineHeight: 1.25 },
  lowerThird: { size: 0.022, weight: 500, tracking: 0.04 },
};
```

### Typography Rules

**Do:**
- Artist name: uppercase, wide tracking (+0.06–0.12em), lighter weight than title
- Track title: mixed case or all-caps depending on preset, tighter tracking (-0.01 to -0.03em for large sizes)
- Metadata line: uppercase, very wide tracking (+0.10–0.16em), smallest size, accent color
- Lyrics: sentence case, line-height 1.2–1.35, never uppercase

**Ban:**
- `Arial` / `Helvetica` in any scene (system fallbacks only if font fails to load)
- `font-weight: 900` + uppercase + `textTransform` + huge size all at once (the "impact" problem)
- Mixed-case title + lowercase artist at same weight — creates no hierarchy
- Centered lyrics wider than 75% of frame width
- Text shadows heavier than `0 4px 16px rgba(0,0,0,0.6)`
- Letter-spacing on text below 18px equivalent

### Motion Rules for Typography

- Title reveal: `translateY` from +20px to 0 over 18 frames + opacity. No scale.
- Artist reveal: stagger 8 frames after title.
- Lyric transition: current line `translateY(0)` opacity 1 → outgoing `translateY(-16px)` opacity 0, incoming from `translateY(+16px)` opacity 0. Over 10 frames.
- No bounce, no elastic, no scale on text.
- Tracking should not animate (it does so poorly in CSS).

---

## 8. Transitions

None currently exist. Every template is a continuous loop with no cut system.

### Priority Transitions to Build

**1. BlurDissolve** — Gaussian blur increases as element exits, new element enters from blur. Good for artwork crossfades.
```ts
// Remotion: interpolate frame through blur/opacity keyframes
// blur: 0 → 24px at midpoint, then 24px → 0
// opacity: 1 → 0 + 0 → 1 with 6-frame overlap
```

**2. DepthParallaxCut** — Elements at different Z depths move at different rates on cut. Foreground element slides left faster than background.

**3. LumaFade** — Brightness ramps to near-white then back down. Works for scene-to-scene. `filter: brightness()` interpolated over 12 frames.

**4. FilmBurn** (already exists, unused) — Use this for VHS/metal presets on section transitions.

**5. TextTrackIn** — New text enters with letter-spacing collapsing from wide (+0.2em) to target. Title treatment only. 18 frames.

**6. TextFadeUp** — Standard for metadata and captions. Already partially implemented in MetadataBlock. Formalize.

**7. ArtworkReveal / DepthMask** — Artwork reveals behind a gradient wipe moving left-to-right or top-to-bottom. Cinematic presets.

### What to Avoid

- Zoom-in reveal (overused)
- Spin-in for text (cheap)
- Bounce/elastic spring on artwork (feels like an app UI)
- Cross-dissolve with identical blend on all layers (flat)
- Wipe transitions except when intentional (VHS preset)

---

## 9. Masking, Frames, Borders, and Materials

### Frame Presets to Build

```ts
type ArtworkFramePreset = "none" | "matte" | "chrome" | "vinyl-sleeve" | "crt" | "polaroid";
```

**Matte:** `border: 12px solid #f5f0e8` (warm off-white), subtle texture, no drop shadow beyond soft outer glow.

**Chrome:** 1px border, CSS metallic gradient using `conic-gradient`. Razor thin. For luxury/editorial presets.

**Vinyl-sleeve:** Dark textured frame, visible sleeve edge at bottom, slight corner wear. The sleeve texture can be a CSS pattern or noise overlay.

**CRT:** Rounded rectangle with scanline overlay, screen-door pixel grid, slight barrel distortion via `perspective`.

**Polaroid:** White border heavier on bottom (larger bottom padding), slight rotation, paper texture via pseudo-element.

### Material System

For the VinylRecord case specifically:

```ts
// materials/vinyl.ts
type VinylMaterial = {
  baseColor: [string, string, string]; // radial gradient stops
  grooveDensity: number;               // 20–60 rings
  grooveOpacity: number;               // 0.03–0.08
  sheen: number;                       // conic gradient opacity
  labelScale: number;
};
```

For glass/frosted glass: CSS `backdrop-filter: blur()` + `background: rgba(255,255,255,0.06)` + `border: 1px solid rgba(255,255,255,0.12)`. This is the correct glassmorphism approach but should only appear in specific presets (Spotify Canvas style), not universally.

---

## 10. Atmosphere, Lighting, and PostFX

### Priority Modules

**FilmGrain (exists):** Current dot-based approach is technically wrong but acceptable. A proper grain would use `feTurbulence` SVG filter. For Remotion, the dot approach is actually safer for performance. Improve: randomize dot shapes (square, dot mix), increase cell count to 400 for `grain` preset.

**Halation (missing):** Soft warm glow bleeding from bright areas. CSS: `filter: blur(40px)` applied to a slightly brightened, hue-rotated copy of artwork at very low opacity (0.15–0.25), mixed with `screen`. This adds enormous production value for zero cost.

**ColorGrading (missing):** CSS `filter: sepia() hue-rotate() saturate() contrast()` chain. Build a `ColorGrade` component wrapping children with configurable LUT-style parameters:
```ts
type ColorGrade = {
  temperature: number; // -1 (cool) to 1 (warm) → hue-rotate approx
  saturation: number;  // 0–2
  contrast: number;    // 0.8–1.4
  lift: number;        // shadows lifted (brightness on darks via CSS gradient)
  gamma: number;       // midpoint via contrast
};
```

**Vignette (exists):** Current radial-gradient approach is correct. The white-center issue noted above — fix by using `radial-gradient(circle at center, transparent 38%, rgba(0,0,0,0.8) 100%)` only.

**Bloom (missing):** Soft bright-area bleed. Same technique as halation but applied to all bright elements, not just artwork. SVG `feGaussianBlur` + `screen` blend on a brightness-threshold copy.

**DepthOfField approximation (missing):** Blur the background, keep foreground sharp. Currently `BackgroundField` blurs the bg but the blur value isn't responsive to artwork proximity. Add `focalBlur` prop to `ArtworkBackground`.

**Fog/Atmosphere (missing):** Radial gradient overlays at low opacity cycling slowly. For doom/ambient presets. Build `AtmosphereLayer` with:
```ts
type AtmosphereMode = "fog" | "dust" | "smoke" | "clear";
// Fog: bottom-weighted white gradient, slow opacity pulse
// Dust: sparse particles, slow drift, no glow
// Smoke: mid-frame horizontal layers, slight blur
```

---

## 11. Asset Pipeline Design

### Current State

Everything is `staticFile(src)`. No processing. No color extraction. No fallback generation. The Python side of Clipped presumably handles audio prep — the visual asset pipeline doesn't exist yet.

### Ideal Pipeline

```
Input: coverSrc, artistImageSrc, logoSrc, audioSrc
       ↓
[Python pre-processing before render]
  extract_dominant_colors(coverSrc) → palette suggestion
  generate_blurred_background(coverSrc, sigma=40) → backgroundSrc
  generate_color_background(dominant_color) → fallback bg
  crop_artist_safe(artistImageSrc, face_aware=True) → croppedArtistSrc
  prepare_logo(logoSrc, clean=True) → cleanLogoSrc
  extract_audio_analysis(audioSrc) → audioAnalysis.json (BPM, sections, peaks)
  ↓
[Remotion render-time]
  resolvePalette(extractedColors || userPalette)
  selectBackground(backgroundSrc || colorBackground || palette.bg)
  resolveTypography(genre || preset || style)
```

### Color Extraction

The `palette.ts` system currently has 5 fixed named palettes plus an `auto` path that falls back based on `options.style`. True color extraction would produce a `dominant`, `secondary`, `vibrant`, and `muted` color from the cover art, then feed these into the palette resolver.

**Contrast-safe selection:** When extracting colors for text/accent, run a WCAG contrast check against `palette.bg`. If the extracted accent has < 3:1 contrast, lighten/darken until compliant.

### Blur Map

The blurred background is currently generated at render time (blur filter on the image). Pre-generating a blurred version at 2x sigma and passing it as `backgroundSrc` would allow the render to use a `blur(0px)` version with no CSS filter cost — faster and identical quality.

---

## 12. Preset and Genre System

### Current State

`effects.ts` has 8 presets covering only grain/halo/vignette/scanline values. `palette.ts` has 5 color palettes. `VisualStyle` type has 9 values. These three systems aren't coordinated — a `style: "doom"` and `effects: "vhs"` can conflict.

### Proposed Full Preset Structure

```ts
type ScenePreset = {
  id: string;
  typography: TypographyPreset;
  palette: Palette;
  effects: EffectPreset;
  layout: string;       // layout ID
  audioReactivity: AudioReactivityPreset;
  atmosphere: AtmosphereMode;
  artwork: ArtworkFramePreset;
  visualizer: VisualizerPreset;
};
```

### 10 Core Presets

**Criterion:** Matte border frame, warm desaturated palette, Playfair Display for title, tracking in artist, no visualizer bars, subtle oscilloscope, halation, heavy vignette, no scanlines, no glow, music breathes only via grain density.

**Neo Noir:** Cold blue-green palette, chrome border, Inter tight tracking, horizontal oscilloscope below art, strong vignette, light sweep once, no bass reactivity.

**VHS Death:** Monochrome or red palette, scanlines heavy, VHSTears, chromatic aberration locked on, Space Mono font, spectrum bars as the main element, camera shake on transients only.

**Luxury Vinyl:** Gold/cream palette, vinyl frame with sleeve peek, Playfair Display title, wide artist tracking, VinylRecord as centerpiece, no visualizer bars, subtle record reflection, halation on label zone.

**Black Metal:** Pure monochrome, no borders, film grain heavy, Oswald font, centered composition, treble-reactive distortion, fog atmosphere, zero color.

**Boom Bap:** Warm brown/orange palette, DM Sans, centered artwork, oscilloscope only, film grain medium, no bloom, no glow, photography-grade composition.

**Brutalist:** High contrast red/black, Bebas Neue, no rounded corners anywhere, heavy top-aligned text, flat art (no frame), spectrum bars full width.

**Spotify Canvas:** Near-frameless, blurred background fills, clean cover center, Inter font, minimal oscilloscope, smooth animations, very low effects.

**Apple Music:** Clean white matte border, cover centered, SF Pro approximation (Inter), slow background zoom, no visualizer, vignette light, no grain.

**Documentary:** Warm film palette, Playfair Display, editorial left layout, lower-third text style, halation, subtle film grain, oscilloscope, no reactivity.

### Genre Motion Languages (abbreviated)

| Genre | Typography | Motion | Atmosphere | Visualizer | Avoid |
|---|---|---|---|---|---|
| Death Metal | Oswald uppercase | Sharp cuts, no smooth transitions | Fog, ash | Oscilloscope only | Any glow |
| Black Metal | Any compressed font, track only | Near-static, very slow | Smoke, dark ambient | None | Color, bloom |
| Doom | Playfair or compressed | Extremely slow drift | Dense fog | Breathing lines | Energetic reactivity |
| Thrash | Bebas Neue | Fast cuts at beat | None | Spectrum bars | Atmospheric softness |
| Heavy Metal | Oswald | Medium, punchy | Light dust | Radial minimal | Neon colors |
| Hip Hop | DM Sans or Inter | Mid-energy drift | None | Oscilloscope | Metal aesthetics |
| Boom Bap | DM Sans | Low, deliberate | Film grain only | Waveform subtle | Any glow |
| Jazz | Playfair Display | Slow, organic drift | Warm fog | Oscilloscope | Digital/glitch |
| Ambient | Inter light | Imperceptible | Heavy atmosphere | EnergyLine only | Beats-reactive |
| Electronic | Inter | Mid-high | Particles | SpectrumBars | Analog textures |

---

## 13. AI-Generation Readiness

### Scene Definition Schema

```ts
interface SceneDefinition {
  preset: string;                        // "neo-noir" | "criterion" | ...
  layout: string;                        // "centered" | "editorial-left" | ...
  artwork: AssetRef;
  artist: string;
  track: string;
  album?: string;
  audio?: AssetRef;
  reactive: AudioReactiveTarget[];       // ["lighting", "fog", "camera"]
  overlays: OverlayId[];                 // ["grain", "vignette", "halation"]
  typography: string;                    // typography preset ID
  transition?: string;                   // transition preset ID
  atmosphere?: AtmosphereMode;
  colorOverride?: Partial<Palette>;
  seed?: string;
}

type AudioReactiveTarget =
  | "lighting" | "fog" | "camera" | "typography"
  | "bloom" | "grain" | "atmosphere" | "distortion";

type OverlayId = "grain" | "vignette" | "halation" | "scanlines" | "bloom" | "lightsweep";
```

### Validation Rules

- `preset` must exist in preset registry
- If `reactive` includes `"typography"`, warn — this is in the banned list
- `overlays` count must be ≤ 4 (complexity cap)
- `reactive` count must be ≤ 3 simultaneously active targets
- If genre is metal/doom and `overlays` includes `"bloom"`, override to `"halation"` with warning
- `colorOverride` is only allowed to adjust `accent` and `panel`, not `bg` or `text` (contrast protection)

### What Should Be Randomizable

- `seed` (all deterministic variation)
- `atmosphere` intensity within preset bounds (±20%)
- `transition` selection within preset-compatible transitions
- Background zoom rate within ±10%

### What Should Be Fixed Per Preset

- Font family
- Layout ID
- Core palette
- Reactivity targets (presets define what reacts, not the caller)

---

## 14. Quality Control System

### Checklist (Semi-Automated or Manual)

**Visual Hierarchy:**
- [ ] Is there a clear primary element? (artwork or text, not both equally)
- [ ] Is title visually heavier than artist?
- [ ] Is artist visually heavier than metadata?
- [ ] Is any element competing with the primary at equal weight?

**Safe Zones:**
- [ ] All text within 8% inset from edges on square
- [ ] All text above 15% from bottom on 9:16
- [ ] Logo within 12% from top on 9:16

**Contrast:**
- [ ] Title text contrast ≥ 4.5:1 against background
- [ ] Artist text contrast ≥ 3:1
- [ ] Accent color contrast ≥ 2:1

**Motion:**
- [ ] No more than 3 simultaneously moving elements
- [ ] No camera shake without audio trigger
- [ ] No text position changes after initial reveal

**Audio Reactivity:**
- [ ] BeatFlash opacity ≤ 0.18
- [ ] Halo scale range ≤ 1.15 (currently up to 1.14 with bass=1 at motion=high — barely passing)
- [ ] No reactivity on typography
- [ ] ReactiveHalo used in at most 1 layer per scene

**Glow Detection:**
- [ ] `boxShadow` with colored accent on more than 2 elements → FAIL
- [ ] `filter: blur()` glow behind circular element → WARN
- [ ] `mixBlendMode: "screen"` on more than 3 layers → WARN

**Too Many Elements:**
- [ ] Count of simultaneously visible animated elements ≤ 6
- [ ] Count of visualizer modes active simultaneously = 1

---

## 15. Kill List — Anti-Patterns

### Delete or Replace

| Pattern | Where | Why |
|---|---|---|
| `fontFamily: "Arial, Helvetica, sans-serif"` | Every file | Immediate cheap-template signal |
| `boxShadow: 0 0 Xpx ${palette.accent}66` on circular elements | VinylRecord, ReactiveHalo, bars | YouTube music visualizer 2019 |
| `idx % N === 0 ? palette.accent2 : palette.accent` | Waveform, Spectrum | Index-based color rhythm, looks arbitrary |
| `BeatFlash` at opacity > 0.14 | MetalVHS (0.22) | Flicker, not flash |
| `ChromaticAberration` with constant `sin(frame/8)` | MetalVHS, FluidScene | Rhythmic not reactive, looks like a loop |
| `NeonTunnel` | Overlays | OBS stream overlay |
| `StarField` | FluidScene, Overlays | React demo screensaver |
| `Stage3D` single div with perspective | Stage3D.tsx | Not 3D, not useful |
| White border on artwork (`rgba(255,255,255,0.9)`) | AlbumCard | Spotify embed UI, not motion graphics |
| `backdrop-filter: blur(10px)` on lyric pill | Captions | React app lower-third |
| `textTransform: uppercase` + `fontWeight: 900` + `fontSize: 112` | Captions impact | Meme caption template |
| `ReactiveHalo` on multiple layers | RecordSquare, GallerySquare | Additive glow soup |
| `CameraShake` driven by continuous `sin(frame)` instead of transients | Overlays | Perpetual motion sickness |
| `font-size: 112` in Captions impact | Captions | Way too large, illegible at edges |
| Gradient bottom-to-top `rgba(0,0,0,0.78)` as the only text legibility solution | PulseReel | Lazy contrast solution, design the hierarchy instead |
| `textShadow: "0 8px 28px rgba(0,0,0,0.72)"` identical on all text | Everywhere | Design decision deferred to a shadow |
| Waveform bars as the primary visual element | RecordSquare bottom | The main event is the vinyl, not bars |
| Colored glow behind every interactive/reactive element | Everywhere | Web component energy |
| Camera shake at `strength > 4` | Overlays | Induces motion sickness in renders |
| `background: radial-gradient(circle at center, rgba(255,255,255,0.06), ...)` | Artwork.tsx | Inverted vignette |

### Motion Styles to Avoid

- Bounce/elastic easing on artwork (use `damping: 20, stiffness: 85` max)
- Continuous rotation of non-vinyl elements (always reads as loading spinner)
- Scale-to-reveal for typography
- Simultaneous entrance animations on all elements
- Any animation looping visibly within 8 seconds

### Composition Habits to Avoid

- Everything centered and equal weight
- Symmetric left-right layout on rectangular content
- Waveform bars always at bottom (they read as a UI chrome element)
- Artwork always square-centered (try 2/3 position, rotated, offset)

---

## 16. Recommended File Structure

```
remotion/src/
  ──────────────── CORE ─────────────────
  tokens/
    typography.ts          # font tokens, scale system, tracking rules
    colors.ts              # palette system (move from lib/palette.ts)
    motion.ts              # easing curves, duration constants, motionFactor
    spacing.ts             # named spacing values
    effects.ts             # effect token definitions

  ──────────────── AUDIO ────────────────
  audio/
    audio-utils.ts         # keep (analyzeValues, bands, RMS)
    lyrics-utils.ts        # keep (subtitle parsers)
    beat-detection.ts      # NEW: transient/peak detection
    reactive.ts            # NEW: useReactiveValue, useReactivePulse, useReactiveDrift

  ──────────────── LAYOUTS ──────────────
  layouts/
    zones.ts               # SceneLayout definitions, useLayout hook
    safe-zones.ts          # safe area constants by aspect ratio

  ──────────────── TYPOGRAPHY ───────────
  typography/
    presets.ts             # cinematic, brutal, minimal, lyric, editorial
    MetadataStack.tsx      # TrackTitle + ArtistName + MetaLine composed
    TrackTitle.tsx         # single typed title with preset
    ArtistName.tsx
    MetaLine.tsx
    LyricLine.tsx          # animated lyric display with word timing
    LowerThird.tsx         # editorial lower-third (new, non-pill)
    KineticCaptions.tsx    # replaces Captions.tsx

  ──────────────── ARTWORK ──────────────
  artwork/
    ArtworkBackground.tsx  # replaces BackgroundField
    ArtworkFrame.tsx       # replaces FramedArtwork + BorderedAlbumCard + RecordArtwork
    ArtworkReveal.tsx      # reveal transitions for artwork

  ──────────────── VINYL ────────────────
  vinyl/
    VinylDisc.tsx          # base disc with rotation, grooves
    VinylSpecular.tsx      # world-space counter-rotating specular
    VinylLabel.tsx         # label zone
    VinylDust.tsx          # surface dust layer
    VinylReflection.tsx    # floor/surface reflection
    VinylRecord.tsx        # composed assembly (replaces current)

  ──────────────── MATERIALS ────────────
  materials/
    MatteBorder.tsx
    ChromeBorder.tsx
    VinylSleeve.tsx
    CRTFrame.tsx
    PolaroidFrame.tsx

  ──────────────── CAMERA ───────────────
  camera/
    CameraDrift.tsx        # slow ambient drift wrapper
    CameraHandheld.tsx     # subtle reactive handheld
    PerspectiveStage.tsx   # replaces Stage3D

  ──────────────── ATMOSPHERE ───────────
  atmosphere/
    AtmosphereLayer.tsx    # fog/dust/smoke mode switcher
    FogLayer.tsx
    DustLayer.tsx
    ParticleField.tsx      # replaces/upgrades StarField

  ──────────────── LIGHTING ─────────────
  lighting/
    AmbientLight.tsx       # color temperature overlay
    RimLight.tsx           # edge lighting on artwork
    LightSweep.tsx         # move from Overlays.tsx
    Halation.tsx           # NEW: soft bright-area bleed
    ReactiveBloom.tsx      # NEW: subtle bloom on energy

  ──────────────── POSTFX ───────────────
  postfx/
    Vignette.tsx           # move from Overlays.tsx
    FilmGrain.tsx          # move from Overlays.tsx
    Scanlines.tsx          # move from Overlays.tsx
    ColorGrade.tsx         # NEW: CSS filter chain component
    ChromaticAberration.tsx # move from Overlays.tsx (improve)
    VHSTears.tsx           # move from Overlays.tsx
    FilmBurn.tsx           # move from Overlays.tsx
    PostFxStack.tsx        # composer (keep)

  ──────────────── VISUALIZERS ──────────
  visualizers/
    SpectrumBars.tsx       # move from Spectrum.tsx (strip style decisions)
    RadialBars.tsx
    WaveRibbon.tsx
    Oscilloscope.tsx
    PulseRings.tsx
    EnergyLine.tsx         # NEW: single RMS-driven breathing line
    MinimalDots.tsx        # NEW: sparse audio-driven dots

  ──────────────── TRANSITIONS ──────────
  transitions/
    BlurDissolve.tsx
    LumaFade.tsx
    FilmBurnTransition.tsx
    TextTrackIn.tsx
    TextFadeUp.tsx
    DepthParallax.tsx

  ──────────────── PRESETS ──────────────
  presets/
    index.ts               # preset registry
    criterion.ts
    neo-noir.ts
    vhs-death.ts
    luxury-vinyl.ts
    black-metal.ts
    boom-bap.ts
    brutalist.ts
    spotify-canvas.ts
    apple-music.ts
    documentary.ts
    effects.ts             # keep existing (expand)

  ──────────────── SCENE ────────────────
  scene/
    SceneBuilder.tsx       # createScene() AI-friendly API
    SceneTimeline.ts       # useSceneTimeline hook
    SceneLayout.tsx        # layout zone resolver
    SceneBackground.tsx
    SceneForeground.tsx
    SceneTypography.tsx
    ScenePostFX.tsx

  ──────────────── TEMPLATES ────────────
  templates/               # keep existing, refactor to use new modules
    PulseReel.tsx
    GallerySquare.tsx
    RecordSquare.tsx
    FluidScene.tsx
    MetalVHS.tsx
    PremiumCard.tsx

  ──────────────── QUALITY ──────────────
  quality/
    validators.ts          # contrast, safe-zone, motion-intensity checks
    checklist.ts           # export as data for external tooling

  ──────────────── LEGACY ───────────────
  _delete/                 # Stage3D.tsx, StarField, NeonTunnel, Texture.tsx
```

---

## 17. Implementation Roadmap

### Phase 1 — Audit and Cleanup (1–2 days)
**Goal:** Remove dead code, clarify module intent.
- Delete `Stage3D.tsx`, `Texture.tsx`
- Move `NeonTunnel`, `StarField` to `_deprecated/`
- Remove `motionFactor` from `palette.ts`, extract to `tokens/motion.ts`
- Add `// TODO: replace Arial` comments to all typography locations
- Add `// TODO: extract to tokens/spacing` to all magic-number positions
- **Expected improvement:** Codebase clarity. No visual change yet.

### Phase 2 — Typography System (2–3 days)
**Goal:** Eliminate Arial. Add Remotion font loading. Build scale system.
- Add `@remotion/google-fonts` or host Inter + Oswald + Bebas Neue via `<staticFile>`
- Create `tokens/typography.ts` with scale system
- Create `typography/TrackTitle.tsx`, `ArtistName.tsx`, `MetaLine.tsx`, `MetadataStack.tsx`
- Refactor `MetadataBlock` and `Captions` to use new components
- **Expected visual improvement:** Massive. Font choice alone will transform perceived quality.

### Phase 3 — Layout Engine (1–2 days)
**Goal:** Eliminate magic-number positioning.
- Create `layouts/zones.ts` with `centered`, `editorial-left`, `lower-third`, `poster` layouts
- Create `layouts/safe-zones.ts`
- Create `useLayout(id, width, height)` hook
- Refactor PulseReel and GallerySquare to use layout zones
- **Expected improvement:** Consistent positioning across aspect ratios.

### Phase 4 — Artwork and Frame System (2 days)
**Goal:** Replace white-border card with material-aware frame system.
- Create `artwork/ArtworkBackground.tsx` with atmospheric mode
- Create `materials/MatteBorder.tsx`, `ChromeBorder.tsx`
- Create `artwork/ArtworkFrame.tsx` with `preset` prop
- Update `GallerySquare`, `PremiumCard` to use new frame
- **Expected improvement:** Eliminates the "Spotify embed" look. High impact.

### Phase 5 — VinylRecord Decomposition (2 days)
**Goal:** Make vinyl cinematic.
- Extract `VinylDisc`, `VinylSpecular` (world-space), `VinylLabel`, `VinylReflection`
- Remove accent glow from behind disc
- Fix specular counter-rotation
- Add floor reflection at 0.15 opacity
- **Expected improvement:** Vinyl goes from YouTube visualizer to genuine showcase element.

### Phase 6 — PostFX Upgrade (2 days)
**Goal:** Add halation, color grading, improve grain.
- Create `lighting/Halation.tsx`
- Create `postfx/ColorGrade.tsx`
- Improve `FilmGrain` with rectangular grain mixed into circular dots
- Fix `Vignette` center-brightening issue
- Fix `ChromaticAberration` to be transient-triggered, not continuous
- **Expected improvement:** Cinematic texture across all presets.

### Phase 7 — Audio-Reactive Primitives (2–3 days)
**Goal:** Decouple reactivity from visual components.
- Create `audio/reactive.ts`: `useReactiveValue`, `useReactivePulse`, `useReactiveDrift`
- Create `audio/beat-detection.ts`: transient peak detection
- Reduce `BeatFlash` max opacity to 0.12 system-wide
- Remove `ReactiveHalo` from `GallerySquare` (duplicate)
- Reroute bass reactivity to grain density and halation radius instead
- **Expected improvement:** Audio reactivity becomes subtle and precise rather than obvious and flashy.

### Phase 8 — Preset System (2 days)
**Goal:** Full scene presets driving all sub-systems.
- Define `ScenePreset` type
- Implement `criterion`, `luxury-vinyl`, `boom-bap`, `vhs-death`
- Create `presets/index.ts` registry
- Wire presets to drive typography, palette, effects, layout, visualizer simultaneously
- **Expected improvement:** Preset selection produces a coherent look, not a mismatched combination of toggles.

### Phase 9 — Transitions (2 days)
**Goal:** Scene transitions and text transitions.
- Implement `BlurDissolve`, `LumaFade`, `TextTrackIn`, `TextFadeUp`
- Use in PulseReel (vinyl → cover transition) and GallerySquare (cover → artist swap)
- **Expected improvement:** Transitions feel intentional rather than opacity toggles.

### Phase 10 — Asset Pipeline (3+ days, Python side)
**Goal:** Color extraction and blur pre-processing.
- Python: dominant color extraction (`colorthief` or `Pillow`)
- Python: pre-blur background generation
- Python: face-aware artist crop (optional: `retinaface` or similar)
- Feed extracted palette suggestion into `auto` palette resolution
- **Expected improvement:** `auto` palette becomes meaningfully correct.

### Phase 11 — AI Scene API (2 days)
**Goal:** `createScene()` function for AI-assembly.
- Define `SceneDefinition` interface
- Create `scene/SceneBuilder.tsx`
- Add validation layer
- Wire existing templates as scene implementations
- **Expected improvement:** Claude/Cursor can assemble scenes from structured spec.

### Phase 12 — Quality Checks (1 day)
**Goal:** Automated validation.
- Implement contrast checker in `quality/validators.ts`
- Implement safe-zone checker
- Implement glow-count checker
- Run on render as optional dev-mode warning output
- **Expected improvement:** Catches regressions before render.

---

## 18. Top 100 Improvements by Impact

| # | Change | Why | Where | Effort |
|---|---|---|---|---|
| 1 | Replace Arial with Inter + Oswald + Bebas Neue | Font is the single biggest quality signal | Every component | Medium |
| 2 | Remove colored glow from behind VinylRecord | Eliminates YouTube visualizer feel immediately | VinylRecord | Quick |
| 3 | Fix `Vignette` center-brightening (white center → transparent center) | Inverted vignette is subtle but wrong | Artwork.tsx | Quick |
| 4 | Fix VinylSpecular to world-space (counter-rotate) | Physically correct, looks substantially more real | VinylRecord | Medium |
| 5 | Replace white-border AlbumCard with `MatteBorder` preset | Eliminates Spotify embed feel | AlbumCard | Medium |
| 6 | Add `Halation.tsx` and apply to cinematic/luxury presets | Single highest-value PostFX add | New file | Medium |
| 7 | Add `ColorGrade.tsx` wrapper with warm/cool/neutral modes | Professional color treatment | New file | Medium |
| 8 | Reduce `BeatFlash` intensity in MetalVHS from 0.22 → 0.10 | Current value causes flicker, not flash | MetalVHS | Quick |
| 9 | Extract all `fontSize`, `fontWeight`, `letterSpacing` into `tokens/typography.ts` | Enables consistent scaling | New file | Medium |
| 10 | Delete `Stage3D.tsx` entirely | Pretend 3D that does nothing | Stage3D | Quick |
| 11 | Delete `Texture.tsx` (dots fake-grain) | Replaced by proper FilmGrain | Texture | Quick |
| 12 | Add `useSceneTimeline` hook to eliminate per-template timing duplications | DRY, enables consistent scene pacing | New hook | Medium |
| 13 | Delete `NeonTunnel` from Overlays | Stream overlay energy | Overlays | Quick |
| 14 | Delete `StarField` or demote to optional sci-fi preset only | React screensaver | Overlays/FluidScene | Quick |
| 15 | Remove `motionFactor` from `palette.ts` | Wrong module | palette.ts → motion.ts | Quick |
| 16 | Add `EnergyLine` — single RMS-driven breathing line | Replaces bars as ambient audio indicator | New visualizer | Medium |
| 17 | Add letter-spacing to all artist name renders (+0.06em) | Instant editorial feel | Metadata | Quick |
| 18 | Add uppercase + wide-tracking to `MetaLine` (+0.12em) | Standard for all premium music content | Metadata | Quick |
| 19 | Add `VinylFloorReflection` — subtle reflection below disc | Doubles visual depth | New component | Medium |
| 20 | Fix `ChromaticAberration` to fire only on transient peaks | Rhythmic sine wave looks like a demo | Overlays | Medium |
| 21 | Build `layouts/zones.ts` with named layout IDs | Eliminates all magic-number positioning | New file | Medium |
| 22 | Add `AtmosphereLayer` with fog mode for doom/ambient presets | Missing entirely from all templates | New component | Medium |
| 23 | Remove `ReactiveHalo` from `GallerySquare` (already present in RecordSquare) | Duplicate halo usage | GallerySquare | Quick |
| 24 | Reduce `ReactiveHalo` scale range from bass*0.14 → bass*0.07 at motion=medium | Currently too reactive | Overlays | Quick |
| 25 | Add `VinylDust` — static semi-transparent particle layer | Textural, physical | New component | Quick |
| 26 | Add `VinylSleeve` peek entering from bottom-right | Narrative motion, production value | New component | Medium |
| 27 | Stagger metadata reveals: title first, artist 8f later, meta 14f later | Currently too simultaneous | MetadataBlock | Quick |
| 28 | Add `RimLight` component — edge highlight on artwork at 0.1–0.2 opacity | Lifts subject from background | New component | Medium |
| 29 | Add text tracking animation to `TrackTitle` reveal (wide → target) | Editorial text entrance | New component | Medium |
| 30 | Replace `backdrop-filter: blur(10px)` lyric pill with text-shadow only | Remove UI component from motion graphics | Captions | Quick |
| 31 | Fix `WaveRibbon` inter-frame smoothing (lerp values 30%) | Currently jittery at loud sections | Spectrum | Quick |
| 32 | Remove `idx % 7 === 0` accent2 pattern in SpectrumBars | Arbitrary, not musical | Spectrum | Quick |
| 33 | Remove `idx % 5 === 0` accent2 pattern in Waveform bars | Same issue | Waveform | Quick |
| 34 | Add `useReactivePulse` for transient detection | Foundation for proper beat reactivity | New hook | Medium |
| 35 | Wire grain density to RMS rather than constant | Grain breathes with music, not constantly present | PostFX | Medium |
| 36 | Remove `boxShadow` glow from `SpectrumBars` | Bars already have enough visual weight | Spectrum | Quick |
| 37 | Remove `boxShadow` glow from `Waveform` bars | Same | Waveform | Quick |
| 38 | Add `PerspectiveStage` replacing Stage3D with actual configurable 3D CSS | Useful as a layout wrapper | New component | Medium |
| 39 | Reduce VHSTears from 4 to 3 and slow pattern rate | Currently too regular / predictable | Overlays | Quick |
| 40 | Add `LumaFade` transition for MetalVHS section breaks | Cinematic VHS cut | New transition | Medium |
| 41 | Implement `ScenePreset` type and wire `criterion`, `luxury-vinyl` presets | First real presets | New file | Deep |
| 42 | Add `BlurDissolve` transition for artwork crossfades in GallerySquare | Removes hard cut | New transition | Medium |
| 43 | Add `safe-zones.ts` and validate text position at render-time in dev | Prevent safe zone violations | New file | Quick |
| 44 | Fix `ArtworkBackground` `saturate(0.92)` → `saturate(0.45)` for cinematic | Commit to desaturation | Artwork | Quick |
| 45 | Add `AmbientLight` temperature overlay for warm/cool scene grading | Cheap, high value | New component | Quick |
| 46 | Add `TextFadeUp` transition as standard metadata entrance | Replaces ad-hoc translateY logic | New transition | Medium |
| 47 | Fix `LightSweep` to complete once then stop (not loop infinitely) | Currently loops, reads as looping animation | Overlays | Quick |
| 48 | Add `Oscilloscope` as default visualizer for Premium/Criterion presets | Replaces bars | Templates | Quick |
| 49 | Remove `Oscilloscope` from MetalVHS top position — too clean for VHS | Wrong aesthetic match | MetalVHS | Quick |
| 50 | Add `MinimalDots` visualizer for ambient/jazz presets | Sparse, atmospheric | New visualizer | Medium |
| 51 | Create `presets/effects.ts` with `bloom`, `halation` fields added | Missing from current preset system | effects.ts | Quick |
| 52 | Reduce Vignette in `GallerySquare` from 0.72 → 0.56 (clean preset) | Currently too heavy for clean artwork | GallerySquare | Quick |
| 53 | Add artwork cover aspect-ratio awareness (non-square album art handling) | Some covers are not square | ArtworkFrame | Medium |
| 54 | Extract inline timing constants in PulseReel to `useSceneTimeline` | DRY, 6 duplicated timing systems | PulseReel | Medium |
| 55 | Add `FilmBurn` transition usage in MetalVHS intro | FilmBurn exists but is unused | MetalVHS | Quick |
| 56 | Add `DepthParallax` to `ArtworkBackground` (foreground/background drift) | Subtle parallax depth on background | ArtworkBackground | Medium |
| 57 | Wire `options.style === "doom"` to `AtmosphereLayer mode="fog"` | Doom preset exists but no atmosphere | Templates | Quick |
| 58 | Wire `options.style === "neon"` to `ChromaticAberration` only on transients | Better neon behavior | Templates | Quick |
| 59 | Add `.specular-sweep` CSS animation alternative using `@keyframes` | Alternative to JS-driven specular | VinylRecord | Quick |
| 60 | Remove `filter: contrast(1.12) saturate(0.8)` from MetalVHS cover — inconsistent | Mixed filter on one element vs none on others | MetalVHS | Quick |
| 61 | Make `FilmGrain` cells use rectangular dots not circular for realism | Film grain is clumps, not circles | FilmGrain | Quick |
| 62 | Add `grain.animated = false` option for still grain | Some presets need static grain | FilmGrain | Quick |
| 63 | Add `useAudioReactive` `smoothing` parameter (lerp between frames) | Prevents jitter at loud peaks | useAudioReactive | Quick |
| 64 | Add lyrics word-level timing support to `KineticCaptions` | For word-by-word karaoke style | Captions | Deep |
| 65 | Remove `CameraShake` `Math.sin(frame * 0.61)` perpetual motion | Should only fire on transients | Overlays | Quick |
| 66 | Add `CameraHandheld` — very slow 0.3px drift, imperceptible but adds life | Replaces perpetual shake | New component | Quick |
| 67 | Add `ArtworkReveal` with `DepthMask` wipe for editorial presets | Better than spring scale reveal | New transition | Medium |
| 68 | Add `useLayout` hook consuming `layouts/zones.ts` | First layout engine usage | New hook | Medium |
| 69 | Make `resolvePalette` accept `extractedColors` param | Color extraction readiness | palette.ts | Quick |
| 70 | Add `"auto-warm"` and `"auto-cool"` to palette names | More meaningful auto modes | palette.ts | Quick |
| 71 | Add `PosterLayout` with full-bleed art, top-anchored massive title | Missing layout type | layouts/ | Medium |
| 72 | Add `EditorialLeftLayout` with artwork right, text left-aligned | Missing layout type | layouts/ | Medium |
| 73 | Add `LowerThirdLayout` for live-lyric templates | Missing layout type | layouts/ | Medium |
| 74 | Add `MagazineLayout` with header title, artwork, meta strip | Missing layout type | layouts/ | Medium |
| 75 | Make `MetadataBlock` accept `align: "left"` and respect `EditorialLeftLayout` | Currently centered-only effective | Metadata | Quick |
| 76 | Add `LogoReveal` with `DepthBlur` entrance (instead of spring scale) | More cinematic logo treatment | PulseReel | Medium |
| 77 | Add `SectionBreak` event support driven by audio analysis | Scene can change on musical sections | scene/ | Deep |
| 78 | Wire `extractedPalette.accent` suggestion to `auto` palette resolver | Color extraction integration | palette.ts | Medium |
| 79 | Add `quality/validators.ts` with contrast check and safe-zone check | Dev-mode quality gate | New file | Medium |
| 80 | Add `quality/glow-detector.ts` — count glowing elements, warn if > 2 | Quality control | New file | Quick |
| 81 | Add `WaveformMode: "energy-line"` option | New minimal visualizer mode | types.ts + visualizers | Quick |
| 82 | Remove `Oscilloscope` bottom strip from `FluidScene` — the blob is the event | Competing visual elements | FluidScene | Quick |
| 83 | Reduce `PulseRings` ring count in `FluidScene` from 5 → 3 | Too many rings dilutes impact | FluidScene | Quick |
| 84 | Add `backdrop` option to `Captions` allowing `"none" | "subtle" | "panel"` | More nuanced background control | Captions | Quick |
| 85 | Wire `options.style === "hiphop"` to boom-bap preset | Style value exists but no preset | presets/ | Quick |
| 86 | Add `SpineFix` — artwork container that corrects non-square cover art | Edge case but common | ArtworkFrame | Medium |
| 87 | Add `ArtistImage` component for artist photo handling | Currently unused `artistImageSrc` | artwork/ | Medium |
| 88 | Add face-aware crop hint support for `ArtistImage` | Asset pipeline readiness | ArtistImage | Deep |
| 89 | Wire `options.style === "frost"` to frosted glass material | Style value exists but no implementation | materials/ | Medium |
| 90 | Add `ColorGrade mode="vintage"` with sepia(0.2) + warmth | Common film look | ColorGrade | Quick |
| 91 | Add `ColorGrade mode="cold"` with hue-rotate(-10deg) + low saturation | Neo noir implementation | ColorGrade | Quick |
| 92 | Add `VinylLabel` with optional artist/title typography overlay | Label typography adds depth | VinylLabel | Medium |
| 93 | Add `ChromeBorder` preset | Missing from material set | materials/ | Medium |
| 94 | Add `PolaroidFrame` preset | Useful for gallery and artist presets | materials/ | Medium |
| 95 | Add `SceneBuilder` `createScene()` API stub | AI-generation foundation | scene/ | Deep |
| 96 | Add `AudioReactivityPreset` to `ScenePreset` type | Preset-driven reactivity | presets/ | Medium |
| 97 | Add `GenrePreset` type extending `ScenePreset` | Genre system foundation | presets/ | Medium |
| 98 | Add `durationPhases` to `useSceneTimeline` for <30s / 30-60s / 60s+ clips | Dynamic pacing based on clip length | scene/ | Medium |
| 99 | Add `validateSceneDefinition()` function | AI-scene quality gate | quality/ | Medium |
| 100 | Create `DESIGN_LANGUAGE.md` — written rules document for the system | Onboarding, AI context, consistency | docs/ | Quick |

---

## Summary

The foundation is architecturally sound — `useAudioReactive`, the band analysis, subtitle parsing, the palette system, and the `effectPreset` abstraction are all correct thinking. The audio analysis layer is good enough to build on without major surgery.

The visual output suffers from four structural problems:

1. **Every component uses Arial.** This single fact is responsible for more perceived cheapness than all other issues combined. Fix this first.

2. **Glow is the primary visual language.** Colored bloom/glow behind circular elements, on every bar, around text, behind artwork — this is the defining signature of amateur music visualizers from 2015–2022. The fix is restraint: one subtle glow maximum per scene, driven by a lighting system, not by every component independently.

3. **Audio reactivity is bass-centric and simultaneous.** The halo, the flash, the blur, the shake, the bars all react to the same signal at the same time. Professional audio-reactive work uses different bands, different signals, different time constants, and different subtle magnitudes.

4. **No scene infrastructure.** Every template is a monolith. Until there's a layout engine, a typography token system, a scene timeline hook, and a preset system that drives all sub-systems together, the system will produce inconsistent output no matter how many individual components improve.

The roadmap phases are ordered by impact. Typography (Phase 2) alone will produce a visible quality step. Artwork frames (Phase 4) and VinylRecord decomposition (Phase 5) will remove the most identifiable template-look problems. PostFX upgrade (Phase 6) adds cinematic texture. Audio-reactive refinement (Phase 7) removes the visualizer energy.
