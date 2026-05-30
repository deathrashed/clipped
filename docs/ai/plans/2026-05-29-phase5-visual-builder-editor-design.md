# Phase 5 — Visual Builder Editor Foundation

**Goal**: Build the editor foundation, not a full animation system.

**Priority**: Inspector Panel > Element Reorder/Visibility > Transform Controls > Keyframe Schema > Preset Migration > QA

**Constraint**: No commit/push without explicit request.

---

## 1. Architecture Overview

Phase 5 adds an **editor state layer** and a **registry-driven inspector panel** that sit alongside the existing render pipeline. No template, no renderer, no postFX system is touched.

```
src/editor/
  state.ts           ← EditorState, derived setters, serialization
  InspectorPanel.tsx  ← Registry-driven inspector UI
  InspectorControl.tsx ← Per-type control renderer
  ElementList.tsx     ← Reorder/visibility UI
  TransformControls.tsx ← X/Y/Z/Scale inputs
  types.ts            ← Editor-specific types
  serialize.ts        ← Keyframe serialization
  index.ts            ← Barrel export
src/fixtures/
  qa-inspector.json        ← NEW: inspector rendering fixtures
  qa-transform.json        ← NEW: transform editing fixtures
  qa-visibility.json       ← NEW: visibility toggle fixtures
  qa-ordering.json         ← NEW: element ordering fixtures
  qa-keyframes.json        ← NEW: keyframe serialization fixtures
```

---

## 2. Data Model

### EditorState (`src/editor/types.ts`)

```typescript
type EditorState = {
  elements: EditorElementState[];      // ordered, filtered
  selectedId: string | null;           // currently selected element ID
  expandedSections: Record<string, boolean>; // section collapse state
};

type EditorElementState = {
  id: string;                           // matches registry ElementDefinition.id
  instance: ElementInstance;            // the actual element configuration
  visible: boolean;                     // enabled/disabled toggle
  locked: boolean;                      // future: prevent edits
};
```

### Derived operations (`src/editor/state.ts`)

```typescript
// Selection
function selectElement(state: EditorState, id: string | null): EditorState;
function getSelectedDefinition(state: EditorState): ElementDefinition | null;

// Visibility
function toggleVisibility(state: EditorState, id: string): EditorState;

// Ordering (no drag-and-drop)
function moveUp(state: EditorState, id: string): EditorState;
function moveDown(state: EditorState, id: string): EditorState;

// Transform
function setTransform(
  state: EditorState,
  id: string,
  field: "position.x" | "position.y" | "rotation.z" | "scale",
  value: number
): EditorState;

// Props
function setElementProp(
  state: EditorState,
  id: string,
  key: string,     // dot-notation, e.g. "appearance.opacity"
  value: unknown
): EditorState;
```

All functions are **pure** — they return a new state object (React-friendly via `useReducer` or `useState`).

### Keyframe data model (`src/editor/types.ts`)

```typescript
type KeyframeData = {
  elementId: string;
  controlKey: string;       // dot-notation, e.g. "transform.position.x"
  keyframes: Keyframe[];
};

type Keyframe = {
  frame: number;
  value: number;
  easing?: "linear" | "ease" | "easeIn" | "easeOut" | "spring";
};

type KeyframeSet = {
  keyframes: KeyframeData[];
};
```

This consumes the existing `keyframeable: true` metadata already on every `InspectorControl`.

---

## 3. Proposed Files

### New files

| File | Purpose |
|------|---------|
| `src/editor/types.ts` | `EditorState`, `EditorElementState`, `KeyframeData`, `KeyframeSet` |
| `src/editor/state.ts` | Pure state helpers (select, toggle, moveUp/Down, setTransform, setProp) |
| `src/editor/InspectorPanel.tsx` | Top-level panel: iterates `definition.inspector`, renders sections |
| `src/editor/InspectorControl.tsx` | Per-control renderer: `switch (control.type)` → number/slider/color/boolean/select |
| `src/editor/ElementList.tsx` | Ordered element list with visibility toggle, move-up/down, selection |
| `src/editor/TransformControls.tsx` | X/Y/Z/Scale numeric inputs bound to `state.transform` |
| `src/editor/serialize.ts` | `exportKeyframes(state): KeyframeSet`, `importKeyframes(state, set): EditorState` |
| `src/editor/index.ts` | Barrel exports |
| `src/fixtures/qa-inspector.json` | One element per control type, expected inspector output |
| `src/fixtures/qa-transform.json` | Transform edits + expected state |
| `src/fixtures/qa-visibility.json` | Toggle sequences + expected visible set |
| `src/fixtures/qa-ordering.json` | Move sequences + expected element order |
| `src/fixtures/qa-keyframes.json` | Round-trip serialization fixtures |

### Modified files

| File | Changes |
|------|---------|
| `src/elements/inspector.ts` | Add `resolveInspectorDefaults()` export already exists; no changes needed |
| `src/elements/types.ts` | No changes needed — Phase 4 types are sufficient |
| `src/index.ts` | Add `export * from "./editor"` |

### No changes to

- `ElementStack.tsx` — unchanged, consumes same types
- `VisualizerStack.tsx` — unchanged
- `scene-presets.ts` — unchanged (compatibility layer is separate)
- Any template file — no template changes
- `registry.ts` — unchanged (editor reads from registry)
- `modifiers/` — unchanged

---

## 4. Inspector Panel Architecture

### `InspectorPanel.tsx` (no hardcoded forms)

```typescript
type InspectorPanelProps = {
  definition: ElementDefinition;
  instance: ElementInstance;
  state: EditorState;
  onUpdate: (key: string, value: unknown) => void;
};
```

Rendering flow:

1. Get selected element's `ElementDefinition` from registry.
2. Iterate `definition.inspector` array (the `InspectorSection[]`).
3. Each section → titled `div` with `controls` rendered by `InspectorControl`.
4. Each section title row includes a future keyframe button (`<button disabled title="Timeline coming in Phase 6">`).

### `InspectorControl.tsx`

```
switch (control.type):
  "number"  → <input type="number" min max step />
  "slider"  → <input type="range" + numeric readout />
  "color"   → <input type="color" />
  "boolean" → <input type="checkbox" />
  "select"  → <select><option/></select>
```

Values are read from `instance` via existing `resolveInspectorValue(key, props)` and applied via `setElementProp()`.

### Keyframe buttons

Every control with `keyframeable: true` gets a small diamond icon button to its right. All buttons are **rendered but disabled** with tooltip: `"Keyframe editor coming in Phase 6"`. This ensures the layout is future-proof without implementing functionality.

---

## 5. Element List (Reorder / Visibility)

### `ElementList.tsx`

Renders the ordered list of elements from `EditorState.elements`.

Per row:
- Eye icon (toggle `visible`) — uses `toggleVisibility()`
- Element label (from `registry[element.id].label`)
- Up/down arrow buttons (move-up/move-down, disabled at edges) — uses `moveUp()`/`moveDown()`
- Click to select (sets `selectedId`) — uses `selectElement()`
- Lock icon (disabled, `locked` state reserved for future)

No drag-and-drop library. No visual reorder handle animation.

---

## 6. Transform Controls

### `TransformControls.tsx`

Four numeric inputs bound to the existing `TransformControls` shape:

| Field | Key | Bound To | Default |
|-------|-----|----------|---------|
| Position X | `transform.position.x` | `instance.transform.position.x` | 0 |
| Position Y | `transform.position.y` | `instance.transform.position.y` | 0 |
| Rotation Z | `transform.rotation.z` | `instance.transform.rotation.z` | 0 |
| Scale | `transform.scale` | `instance.transform.scale` | 1 |

These use the same `resolveInspectorValue`/`setElementProp` path as the inspector panel.

---

## 7. Keyframe Schema Usage

### Serialization layer (`src/editor/serialize.ts`)

```typescript
function exportKeyframes(state: EditorState): KeyframeSet {
  // Walk all elements, find controls with keyframeable: true
  // that have defined keyframes in their instance props
  // Return as serializable JSON
}

function importKeyframes(state: EditorState, set: KeyframeSet): EditorState {
  // Merge KeyframeSet into existing state
  // No timeline UI, no frame interpolation
}
```

Storage format matches what the rendering engine would consume later:

```json
{
  "keyframes": [
    {
      "elementId": "vignette",
      "controlKey": "intensity",
      "keyframes": [
        { "frame": 0, "value": 0.5, "easing": "linear" },
        { "frame": 120, "value": 0.8, "easing": "ease" }
      ]
    }
  ]
}
```

No easing editor, no curve preview, no playback scrubber.

---

## 8. Preset Migration Strategy

### Compatibility layer (design only, no implementation)

**Principle**: Existing presets continue working unchanged. The legacy fields (`halation`, `ambientLight`, `rimLight`, `visualizer`, `halo`) remain authoritative. The `effects`, `visualizers`, `background`, `lights`, `scene` arrays are **additive** — they can supplement but cannot conflict with legacy fields.

New presets (added in a future phase) may omit legacy fields entirely and rely solely on element arrays.

```typescript
// Legacy preset → elements migration (conceptual, not implemented)
function legacyToElements(preset: ScenePreset): ElementInstance[] {
  // Convert halation/ambientLight/rimLight → element instances
  // Only called when a preset has NO explicit element arrays
}
```

**Implementation is deferred** until a real use case for new presets exists. The type system already supports optional `elements`/`visualizers`/`modifiers` on `ScenePreset`.

---

## 9. QA Strategy

### Fixture files

| Fixture | What it tests |
|---------|---------------|
| `qa-inspector.json` | One element per `InspectorControl` type, expected control rendering count |
| `qa-transform.json` | 4 transform edits (X, Y, Z, scale) + expected `EditorState` after each |
| `qa-visibility.json` | Toggle sequence (on→off→on) + expected visible element count |
| `qa-ordering.json` | 3-element list, move up/down sequences, expected order |
| `qa-keyframes.json` | Round-trip serialize/deserialize with 2 keyframes on one control |

### Smoke tests

New smoke compositions for still renders verifying the editor components mount without error:

- `qa-inspector-panel` — renders `InspectorPanel` with vignette definition
- `qa-element-list` — renders `ElementList` with 3 mock elements

These use the Remotion still-render pattern already established (`qa/still:smoke`).

### Verification commands (same as Phase 4)

```bash
npm run typecheck        # 0 errors
npm run compositions     # 9 + 2 = 11 compositions
npm run still:smoke      # gallery-square + new QA stills
./bin/clipped doctor     # all checks passed
```

---

## 10. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Inspector panel grows too large for one file | Maintainability | Split per-control type into separate files at 400+ lines |
| Editor state mutations out of sync with render state | Stale UI | All mutations go through pure functions; single `EditorState` source of truth |
| `resolveInspectorValue` dot-path resolution fails on nested props | Broken inspector display | Already tested in Phase 4; add unit test coverage |
| Keyframe schema drifts from future timeline phase | Rework | Keep schema minimal and well-documented; defer easing/curve choices |
| Preset migration coupling | Fragile | No migration code is written yet; type system compatibility only |
| Stale working-tree state (fonts, etc.) | Noise | No font/asset files are touched; working with `src/editor/` only |

---

## 11. Verification Commands

```bash
# After all Phase 5 changes:
npm run typecheck
npm run compositions
npm run still:smoke
npm run check:fonts
./bin/clipped doctor
./bin/clipped templates
./bin/clipped platforms

# QA-specific:
node scripts/validate-fixtures.mjs src/fixtures/qa-inspector.json
node scripts/validate-fixtures.mjs src/fixtures/qa-transform.json
node scripts/validate-fixtures.mjs src/fixtures/qa-visibility.json
node scripts/validate-fixtures.mjs src/fixtures/qa-ordering.json
node scripts/validate-fixtures.mjs src/fixtures/qa-keyframes.json
```

(If `validate-fixtures.mjs` does not exist, add a simple JSON schema validation script.)

---

## 12. Implementation Order

1. `src/editor/types.ts` — EditorState, KeyframeData, KeyframeSet
2. `src/editor/state.ts` — Pure state helpers
3. `src/editor/InspectorControl.tsx` — Per-type control renderer
4. `src/editor/InspectorPanel.tsx` — Section iteration, keyframe button stubs
5. `src/editor/ElementList.tsx` — Reorder/visibility with move-up/down
6. `src/editor/TransformControls.tsx` — X/Y/Z/Scale inputs
7. `src/editor/serialize.ts` — Keyframe export/import
8. `src/editor/index.ts` — Barrel export + `src/index.ts` update
9. Fixture files (5 new `qa-*.json`)
10. QA smoke compositions
11. Verification pass + cleanup
