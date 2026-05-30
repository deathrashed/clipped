# Elements Registry — Clipped Visual Builder

Registry-driven element system for Clipped's Remotion engine. Every element defines its inspector controls, default props, compatibility tier, and category metadata.

## Categories

| Category | Label | Count | Groups |
|---|---|---|---|
| text | Text | 3 | Typography |
| visualizers | Visualizers | 6 | Wave, Pulse |
| effects | Effects | 19 | Glow, Color, Texture, Lens |
| depth | Depth Effects | 3 | Atmosphere |
| shapes3d | Shapes & 3D | 4 | Overlay, Geometry |
| backgrounds | Backgrounds | 4 | Static, Dynamic |
| lights | Lights | 5 | Fill, 3D |
| scene | Scene | 2 | Controller |

## Element Definitions

### Text

| ID | Label | Tier | Implemented | Group | Inspector Sections |
|---|---|---|---|---|---|
| `text` | Text | core | ✅ | Typography | Transform, Appearance, Text |
| `lyrics` | Lyrics | core | ✅ | Typography | Transform, Appearance, Lyrics |
| `text-3d` | 3D Text | experimental | ❌ | Typography | Transform, Appearance, 3D Text |

### Visualizers

| ID | Label | Tier | Implemented | Group | Audio-Reactive |
|---|---|---|---|---|---|
| `waveform` | Waveform | core | ✅ | Wave | ✅ |
| `spectre` | Spectre | core | ✅ | Wave | ✅ |
| `oscilloscope` | Oscilloscope | core | ✅ | Wave | ✅ |
| `pulsar` | Pulsar | core | ✅ | Pulse | ✅ |
| `circle` | Circle | core | ✅ | Pulse | ✅ |
| `ferro-fluid` | Ferro Fluid | experimental | ✅ | Pulse | ✅ |

### Effects

| ID | Label | Tier | Implemented | Group | Subgroup |
|---|---|---|---|---|---|
| `bloom` | Bloom | premium | ✅ | Glow | — |
| `unreal-bloom` | Unreal Bloom | premium | ❌ | Glow | — |
| `strobe` | Strobe | disabled | ✅ | Glow | — |
| `brightness-contrast` | Brightness / Contrast | core | ✅ | Color | — |
| `hue-saturation` | Hue / Saturation | core | ✅ | Color | — |
| `color-grading` | Color Grading | core | ✅ | Color | — |
| `filter-effect` | Filter | core | ✅ | Color | — |
| `tone-mapping` | Tone Mapping | premium | ❌ | Color | — |
| `black-white` | Black & White | core | ✅ | Color | — |
| `inversion` | Inversion | core | ✅ | Color | — |
| `noise` | Noise | core | ✅ | Texture | — |
| `scanline` | Scanline | core | ✅ | Texture | — |
| `vhs` | VHS | core | ✅ | Texture | — |
| `pixelation` | Pixelation | experimental | ✅ | Texture | — |
| `vignette` | Vignette | core | ✅ | Lens | — |
| `chromatic-aberration` | Chromatic Aberration | core | ✅ | Lens | — |
| `fisheye` | Fisheye | experimental | ✅ | Lens | — |

### Depth Effects

| ID | Label | Tier | Implemented | Group |
|---|---|---|---|---|
| `fog` | Fog | core | ✅ | Atmosphere |
| `depth-blur` | Depth Blur | core | ✅ | Atmosphere |
| `ssao` | SSAO | experimental | ❌ | Atmosphere |

### Shapes & 3D

| ID | Label | Tier | Implemented | Group |
|---|---|---|---|---|
| `time-display` | Time Display | core | ✅ | Overlay |
| `box-3d` | Box | experimental | ❌ | Geometry |
| `sparkles-3d` | Sparkles | experimental | ❌ | Geometry |
| `fog-3d` | Fog | experimental | ❌ | Geometry |

### Backgrounds

| ID | Label | Tier | Implemented | Group |
|---|---|---|---|---|
| `shader-bg` | Shader Background | premium | ✅ | Dynamic |
| `gradient-bg` | Gradient | core | ✅ | Static |
| `noise-bg` | Noise Background | core | ✅ | Static |
| `video-sphere` | Video Sphere | experimental | ❌ | Dynamic |

### Lights

| ID | Label | Tier | Implemented | Group |
|---|---|---|---|---|
| `ambient-light` | Ambient Light | core | ✅ | Fill |
| `point-light` | Point Light | experimental | ✅ | Fill |
| `light-preset` | Light Preset | premium | ✅ | Fill |
| `spot-light` | Spot Light | experimental | ❌ | 3D |
| `directional-light` | Directional Light | experimental | ❌ | 3D |

### Scene

| ID | Label | Tier | Implemented | Group |
|---|---|---|---|---|
| `camera-3d` | Camera | experimental | ❌ | Controller |
| `environment-3d` | Environment | experimental | ❌ | Controller |

## Inspector Schema

Every element provides:

```
Transform:
  Position X (number, keyframeable)
  Position Y (number, keyframeable)
  Rotation Z (number, keyframeable)
  Scale (slider 0-10, keyframeable)

Appearance:
  Opacity (slider 0-1, keyframeable)
```

Then element-specific controls.

## Modifier Effects (Per-Element)

| ID | Label | Safe by Default | Key Controls |
|---|---|---|---|
| `glow` | Glow | ✅ | Intensity, Radius, Color |
| `blur` | Blur | ✅ | Amount |
| `shadow` | Shadow | ✅ | X, Y, Blur, Color, Opacity |
| `stroke` | Stroke | ✅ | Width, Color, Opacity |
| `adjust` | Adjust | ✅ | Brightness, Contrast, Saturation, Hue |
| `dither` | Dither | ❌ | Amount, Pattern, Colors |
| `pixelate` | Pixelate | ❌ | Size |
| `wobble` | Wobble | ❌ | Amplitude, Speed |

## Policies

1. **Effect modifiers are per-element wrappers.** They wrap a single element and are stackable.
2. **Global postFX are scene-level only.** ColorGrade, AtmosphereLayer, Halation, AmbientLight remain scene-level in cinematic PostFX.
3. **3D requires explicit opt-in** (`enable3D: true`).
4. **Strobe requires explicit opt-in** — disabled by policy (tier: disabled).
5. **Glow is rare** — subtle by default, not the default state for visualizers.
6. **Pixelate, Dither, Wobble** are VHS/glitch only by default (safeByDefault: false).
7. **Unreal Bloom** is marked experimental until true Three.js postprocessing bloom is wired.
8. **Video Sphere** does not load remote assets. **Environment** does not download HDRIs.
