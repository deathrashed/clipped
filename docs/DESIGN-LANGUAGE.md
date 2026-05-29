# Design Language — Clipped

## Visual Principles

- **Audio-first**: Visualizers are the primary aesthetic layer. Text and background support, never dominate.
- **Subtle by default**: Effects start at zero/neutral. Bloom, glow, dither require explicit intent.
- **Safe rendering**: No unmoderated strobe, no unintended 3D, no auto-playing remote assets.
- **Layered composition**: Background → Scene (3D/lights) → Visualizers → Effects → Overlay Elements (text/shapes).

## Elements Registry Design

See `ELEMENTS-REGISTRY.md` for the full catalog.

### Categories (ordered by render pass)

1. **Backgrounds** — Static (gradient, noise) and dynamic (shader, video sphere)
2. **Scene** — 3D camera and environment controllers (experimental)
3. **Lights** — Ambient fill, point light, presets, and 3D-only spotlight/directional
4. **Visualizers** — Audio-reactive (waveform, spectre, oscilloscope, pulsar, circle, ferro-fluid)
5. **Effects** — Color grading, lens, texture, glow effects
6. **Depth Effects** — Fog, depth blur, SSAO
7. **Shapes & 3D** — Time display overlay, 3D geometry stubs
8. **Text** — Typography (text, lyrics, 3D text stub)

### Modifier Effects (per-element)

- Glow, Blur, Shadow, Stroke — safe by default
- Adjust — always safe (brightness/contrast/sat/hue)
- Dither, Pixelate, Wobble — VHS/glitch only

### Tier System

| Tier | Description |
|---|---|
| `core` | Free, always available, no opt-in required |
| `premium` | Requires license; always safe if toggled |
| `experimental` | Incomplete or unoptimized; marked in UI |
| `disabled` | Requires explicit user override (policy block) |

### Opt-In Policy

| Feature | Opt-In Required | Reason |
|---|---|---|
| 3D elements | `enable3D: true` | Performance, peer dependency |
| Strobe effect | tier: disabled | Health/safety |
| Remote assets | Explicit URL | No surprise downloads |
