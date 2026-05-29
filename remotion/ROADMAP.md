# Motion Toolkit Roadmap

This document outlines the milestones and release phases of the Remotion Motion Toolkit.

## Phase 1 — Stabilization ✅
- Split monolithic visualizers from single `Spectrum.tsx` into individual components (`SpectrumBars`, `RadialBars`, `WaveRibbon`, `Oscilloscope`, `PulseRings`).
- Move obsolete code to `_deprecated/`.
- Correct physical vinyl specular highlight coordinate rendering.
- Make metadata block layouts independent of hardcoded margin assumptions.

## Phase 2 — Cinematic Layer & Preset Registry ✅
- Implement local offline font loading.
- Add cinematic PostFX modules: `Halation`, `ColorGrade`, `AmbientLight`, `RimLight`, `DustLayer`, `FogLayer`, `AtmosphereLayer`.
- Create a `ScenePreset` registry mapping styles to aesthetic choices.
- Integrate transition modules (`BlurDissolve`, `LumaFade`, `TextFadeUp`) into templates.
- Restrict `ReactiveHalo` to VHS/Neon styles and prefer film lighting defaults.

## Phase 3 — Preset Architecture ⏳
- Allow user customization of scene preset attributes via external `.json` configuration files.
- Add preset override parameters in CLI options.

## Phase 4 — Asset Pipeline ⏳
- Optimize image compression and local static file discovery.
- Automate artwork asset sizing and resizing on-the-fly.

## Phase 5 — Scene Builder ⏳
- Construct dynamic timelines allowing composition transitions.
- Interactive multi-scene video outputs.

## Phase 6 — Quality Validation ⏳
- Integrate end-to-end visual tests.
- Compare frame renders to baselines automatically on build.
