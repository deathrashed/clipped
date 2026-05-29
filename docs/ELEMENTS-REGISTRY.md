# Elements Registry — Clipped Remotion

The Elements Registry is a unified, categorized system of visual building blocks for Remotion templates. It replaces ad-hoc effect wiring with a declarative `ElementStack` that renders effects, backgrounds, lights, depth cues, visualizers, and 3D scene elements from data-driven arrays.

## Implementation Status

### Implemented

| ID | Category | Tier | Description |
|----|----------|------|-------------|
| vignette | effects/lens | core | Radial darkening at edges |
| chromatic-aberration | effects/lens | core | Color channel offset |
| fisheye | effects/lens | core | Radial lens distortion |
| noise | effects/texture | core | Film grain overlay |
| scanline | effects/texture | core | Horizontal scan lines |
| vhs | effects/texture | core | VHS tracking artifacts |
| bloom | effects/glow | core | Soft glow on bright areas |
| brightness-contrast | effects/color | core | Brightness and contrast adjustment |
| hue-saturation | effects/color | core | Hue rotation and saturation |
| color-grading | effects/color | core | LUT-based color grading presets |
| filter-effect | effects/color | core | Generic color filter overlay |
| black-white | effects/color | core | Desaturation to monochrome |
| inversion | effects/color | core | Color inversion |
| fog | depth | premium | Distance-based atmospheric fog |
| depth-blur | depth | premium | Distance-based blur |
| shader-bg | backgrounds | core | Animated shader background |
| gradient-bg | backgrounds | core | Gradient background |
| noise-bg | backgrounds | core | Animated noise texture background |
| ambient-light | lights | premium | Radial ambient light overlay |
| point-light | lights | premium | Point light overlay |
| light-preset | lights | premium | Pre-configured lighting setups |
| spectre | visualizers | core | Audio-reactive spectrum bars |
| oscilloscope | visualizers | core | Audio waveform oscilloscope |
| pulsar | visualizers | core | Audio-reactive pulse rings |
| circle | visualizers | core | Audio-reactive circle pattern |

### Stubbed (not implemented, `implemented: false`)

| ID | Category | Tier | Notes |
|----|----------|------|-------|
| ferro-fluid | visualizers | experimental | Component exists but is a placeholder wrapper |
| pixelation | effects/texture | experimental | Component returns null in ElementStack |
| strobe | effects/glow | disabled | `() => null` stub, disabled by policy |
| tone-mapping | effects/color | core | Component returns null |
| text-3d | shapes3d | premium | Returns null |
| box-3d | shapes3d | premium | Returns null |
| sparkles-3d | shapes3d | premium | Returns null |
| fog-3d | shapes3d | premium | Returns null |
| time-display-3d | shapes3d | premium | Returns null |
| video-sphere | backgrounds | core | Returns null |
| spot-light | lights | premium | Returns null |
| directional-light | lights | premium | Returns null |
| camera-3d | scene3d | experimental | Returns null |
| environment-3d | scene3d | experimental | Returns null |
| scene-controller | scene3d | experimental | Composite: renders stubs |
| three-scene | scene3d | experimental | Returns null |
| ssao | depth | premium | Returns null |

### Status Summary

| Status | Count |
|--------|-------|
| Implemented | 25 |
| Stubbed (not implemented) | 18 |
| **Total registered** | **43** |

## Architecture

```
elements/
├── types.ts            # Shared TypeScript types
├── categories.ts       # Category labels and ordering
├── registry.ts         # 43 element definitions
├── ElementStack.tsx     # Render engine — delegates to modular components
├── index.ts            # Barrel exports
├── text/               # TextElement, LyricsElement, Text3D
├── visualizers/        # VisualizerStack wrapping existing visualizers
├── effects/            # glow/, color/, texture/, lens/ subfolders
├── depth/              # DepthFog, DepthBlur, SSAO (stub)
├── shapes3d/           # TimeDisplay3D, Box3D/Sparkles3D/Fog3D (stubs)
├── backgrounds/        # ShaderBackground, GradientBackground, NoiseBackground, VideoSphere (stub)
├── lights/             # AmbientLightLayer, PointLightLayer, LightPreset, stubs
└── scene3d/            # Camera3D, EnvironmentLayer, SceneController, ThreeScene (all stubs)
```

## Tier System

- **core**: Always available, safe to use without opt-in.
- **premium**: Available but marked as requiring consideration (needs `enable3D` for 3D elements).
- **experimental**: Requires `allowExperimental` opt-in on `ElementStack`.
- **disabled**: Never renders unless explicitly overridden (e.g., strobe).

## Opt-In Rules

- `allowExperimental` prop on `ElementStack` unlocks experimental-tier elements.
- `enable3D` prop unlocks all `requires3D` elements (currently all stubs).
- All stub/non-implemented elements are skipped silently with a dev console warning.

## Scene Preset Integration

Scene presets include five element arrays matching functional categories:

```ts
type ScenePreset = {
  // ...existing fields...
  effects: ElementInstance[]
  visualizers: ElementInstance[]
  lights: ElementInstance[]
  background: ElementInstance[]
  scene: ElementInstance[]
}
```

Each template renders `<ElementStack>` with the combined arrays from the resolved scene preset.

## Adding a New Element

1. Add a definition to `registry.ts` with the correct category, tier, and metadata.
2. Create or wire a component. If the element maps to an existing component, add a case in `ElementStack.tsx`.
3. If the element is not yet implemented, set `implemented: false`.
4. For 3D elements, set `requires3D: true` and `implemented: false`.
5. Template integration is automatic through scene preset arrays.

## Safety

- `ElementStack` filters out unimplemented, disabled, experimental (without opt-in), and 3D (without opt-in) elements.
- Dev warnings are emitted for unknown element IDs and unimplemented elements.
- Default z-ordering: backgrounds (-1), lights (70), depth (80), effects/glow (85), effects/texture (95), effects/color (95).
