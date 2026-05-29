# Motion Toolkit Design Language

This document defines the core aesthetic guidelines and visual rules for building high-quality cinematic music videos and visualizers in the Clipped framework.

## 1. Core Philosophy: Premium & Subtle

We avoid the "amateur DJ visualizer" look. Every component must feel premium, editorial, and polished.

- **What Looks Professional**:
  - Consistent typography sizing, hierarchy, and letter-spacing (tracking).
  - Subtle, slow-drifting organic elements (dust/fog haze).
  - Filmic lighting effects (halation highlight bleed, ambient light, rim highlights).
  - Clean layout alignment locked to aspect-aware grids and safe zones.
  - Smooth, elegant visual transitions (BlurDissolve, LumaFade).
  - Muted, harmonious, and HSL-tailored color grading.

- **What to Avoid**:
  - High-frequency glowing drop shadows on spectrum bars.
  - Intense, saturated neon glows.
  - Overly-reactive scaling effects that distort the artwork (e.g. extreme pulsing/bouncing).
  - Monolithic visualizers that combine layouts and rendering in a single file.
  - Hardcoded absolute positioning values that break across aspect ratios.

## 2. Typography Rules

- Limit font loading to the specific weight and subset needed.
- Use the correct typography preset based on style:
  - `cinematic` (default): Serif display titles, clean sans-serif bodies, spacious tracking.
  - `editorial`: Sharp layout, tight display title tracking.
  - `brutal`: Large, uppercase bold titles, loud presence.
  - `minimal`: Muted sizes, thin weight, high elegance.
  - `vhs`: Monospace, classic digital aesthetic.
- Titles must be block-level and respect safe margins. Right alignment should align the text strictly to the right side of its container.

## 3. Audio-Reactive Policy

- Keep reactive parameters within realistic limits:
  - Title/artwork scale reaction should not exceed `1.15x` peak zoom.
  - Particle drift or speed can react to bass hits, but should never jitter.
- Waveform components should utilize the unified analysis pipeline and have subtle, desaturated background lines.

## 4. Color Grading & Lighting Rules

- Grade styles using CSS filter configurations and blend-mode overlays instead of destructive LUT transformations.
- **Ambient Light**: Use to wash scenes in soft, single-direction lighting to match mood (warm orange, cool blue, deep gold).
- **Halation**: Highlight bleeds must simulate film halation (subtle warm red/orange edge glows), not neon styling.
- **Rim Lighting**: Edge-highlighting cards/artwork should use desaturated accents matched to the design palette.

## 5. Halo & Glow Policy

- **ReactiveHalo** must be disabled by default for clean, cinematic, and premium presets.
- Limit halo/glow effects to neon and retro VHS presets only.
- Prefer Halation, ColorGrade, and AmbientLight over crude back-lighting halos.

## 6. Transition Rules

- Scene cut reveals (such as logo intro to card) should use `BlurDissolve` or `LumaFade` to prevent harsh frames.
- Captions and metadata blocks should enter via `TextFadeUp` with a slow, spring-driven translation.
