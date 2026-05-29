# Roadmap — Clipped

## Phase 4: Elements Registry (Current)

Registry-driven element system with inspector schemas, modifier effects, scene presets, and 6-template compatibility.

### Done
- 44 element definitions across 8 categories with full inspector schemas
- 8 per-element modifier components (glow, blur, shadow, stroke, adjust, dither, pixelate, wobble)
- ModifierWrapper that stacks active modifiers over child elements
- ElementStack applies registry defaults and wraps elements with modifiers
- Scene preset type supports modifiers and enable3D fields
- All 6 templates wired to ElementStack

### Next
- QA fixture validation and verification pass
- Documentation (ELEMENTS-REGISTRY.md, ARCHITECTURE.md update, DESIGN-LANGUAGE.md, ROADMAP.md)
- Typecheck, composition listing, smoke test against all 6 templates

## Phase 5: Inspector UI

- Build inspector panel components for each control type (slider, color picker, select, toggle, number input)
- Wire inspector schemas to interactive TUI or Remotion Studio controls
- Keyframeable marker UI (timeline indicators, no playback engine)

## Phase 6: Template Expansion

- New templates composable entirely from element arrays
- Per-element position/scale transforms in template layouts
- Scene-level postFX pipeline (color grading pass, atmosphere pass, bloom pass)

## Phase 7: 3D Pipeline

- Wire `@remotion/three` for Box, Sparkles, Fog, Camera, Environment, lights
- Model-viewer-style orbit control for previews
- 3D-safe rendering tier flag

## Backlog

- Overlay layers support
- Video textures (as background option)
- Video Sphere remote asset loading (with URL opt-in)
- Unreal Bloom with real Three.js postprocessing
- SSAO depth effect
- Timeline/sequencer UI for multi-track element stacking
- Tone mapping effect
- Environment HDRI loading (with user-provided URL)
- 3D Text rendering
