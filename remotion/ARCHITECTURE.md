# Motion Toolkit Architecture

This document describes the structure and layers of the Remotion visualization application in Clipped.

## 1. Directory Layout

The application is structured into domain-specific directories under `remotion/src/`:

```
remotion/src/
  ├── artwork/         # Backgrounds, frames, and artwork wrappers
  ├── audio/           # Sound analysis, React audio hooks, and layers
  ├── components/      # Higher-level UI elements (metadata, captions)
  ├── effects/         # Cinematic overlays, halation, grading, lights
  ├── hooks/           # Unified react hooks (useAudioReactive, useLayout)
  ├── layouts/         # Aspect-ratio and coordinate grid engines
  ├── lib/             # Helpers for colors, text, and palette resolvers
  ├── presets/         # Effect and ScenePreset registry definitions
  ├── templates/       # The 6 core render layouts/scenes
  ├── tokens/          # Standard layout sizes, typography, and spacing
  ├── transitions/     # Transition wrappers (BlurDissolve, LumaFade)
  └── typography/      # Text rendering stack and font loaders
```

## 2. Core Systems

### A. ScenePreset System (`presets/scene-presets.ts`)
Decouples visual template components from options styles. The registry resolves a unified configuration for:
- Typography presets (`cinematic`, `editorial`, `brutal`, etc.)
- Color grade presets (`neutral`, `cinematic`, `luxury-vinyl`, etc.)
- Atmosphere modes (`none`, `dust`, `fog`, `ash`)
- Halation, Ambient Light, Rim Light parameters
- Visualizer glow settings
- Reactive halo visibility

### B. Effects System (`effects/`)
Implements post-processing overlays that stack over compositions:
- **Halation**: Highlight diffusion that bleeds filmic warmth.
- **ColorGrade**: Applies contrast, saturation, and hue filters with CSS blend-mode color washes.
- **AmbientLight**: Full-scene lighting wash.
- **RimLight**: Side-specific edge lights for cards/artwork.
- **AtmosphereLayer**: Composes `DustLayer` (particles) and `FogLayer` (drifting haze).

### C. Typography System (`typography/`)
Loads local fonts asynchronously using browser `FontFace` APIs inside `fonts.ts` to avoid Google Font network calls during offline builds:
- Standardizes fonts: `Inter` (body), `Oswald` (display), `Bebas Neue` (brutal), and `Space Mono` (mono).
- `MetadataBlock` takes explicit text props and typographyPreset values to remain layout-agnostic.

### D. Transitions System (`transitions/`)
Manages smooth intro/outro transitions:
- `BlurDissolve`: Peak-blur opacity fades for card/logo swaps.
- `LumaFade`: White-out flashes for scene changes.
- `TextFadeUp`: Spring-driven metadata entrances.
- `TextTrackIn`: Collapse of wide letter-spacing.
