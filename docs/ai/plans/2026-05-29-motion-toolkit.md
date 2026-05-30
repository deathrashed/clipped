# Motion Toolkit Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the ad-hoc visual system with a layered, composable motion-graphics toolkit — covering typography, layout, transitions, materials/frames, audio-reactive primitives, and cinematic postFX — then refactor all six templates to consume it.

**Architecture:** New modules live under `remotion/src/` in domain folders (`tokens/`, `typography/`, `layouts/`, `transitions/`, `materials/`, `audio/`, `lighting/`, `postfx/`, `atmosphere/`). Templates stay in `templates/` but become thin consumers of toolkit primitives. Each phase is additive — templates continue to render throughout. No big-bang rewrites.

**Tech Stack:** Remotion 4.0.468, React 19, TypeScript 6, `@remotion/noise` (Perlin noise for grain/atmosphere), `@remotion/google-fonts` (Inter, Oswald, Bebas Neue), `@remotion/transitions` (scene transition helpers), existing `@remotion/media-utils` (audio).

**Remotion-specific rules (read before every task):**
- `useCurrentFrame()`, `useVideoConfig()` are frame-pure — never use `Date.now()` or random without `random()` from remotion.
- All image sources must go through `staticFile()`.
- `interpolate()` needs `extrapolateLeft/Right: "clamp"` unless intentional.
- Spring config: `damping: 18–22, stiffness: 80–100` for artwork; `damping: 26, stiffness: 120` for text.
- CSS `backdrop-filter` is not supported in Remotion renders — never use it.
- `Math.random()` breaks determinism — always use `random(seed)` from remotion.
- Font loading: use `@remotion/google-fonts` `loadFont()` called at module top level.

---

## Phase 1 — Typography + Layout Foundation

### Task 1.1: Token files — motion, spacing, and typography scale

**Files:**
- Create: `remotion/src/tokens/motion.ts`
- Create: `remotion/src/tokens/spacing.ts`
- Create: `remotion/src/tokens/typography.ts`
- Modify: `remotion/src/lib/palette.ts` (remove `motionFactor`, re-export from tokens)

**Step 1: Create `remotion/src/tokens/motion.ts`**

```ts
// Easing curves and motion multipliers for Clipped templates.
// Import motionFactor from here, not from lib/palette.

import { Easing } from "remotion";

/** Scale raw animation values by motion level. */
export const motionFactor = (motion: string): number => {
  if (motion === "low") return 0.55;
  if (motion === "high") return 1.45;
  return 1;
};

/** Standard easing curves. Use these instead of inline bezier calls. */
export const ease = {
  /** Snappy overshoot — artwork reveals, logo entrances. */
  snap: Easing.bezier(0.16, 1, 0.3, 1),
  /** Smooth deceleration — text fades, background drift. */
  out: Easing.out(Easing.cubic),
  /** Linear — opacity-only fades where easing doesn't apply. */
  linear: Easing.linear,
  /** Spring-like — not a real spring, use spring() for that. */
  bounceOut: Easing.bezier(0.34, 1.56, 0.64, 1),
} as const;

/** Named frame durations at 30fps. Scale if fps differs. */
export const dur = {
  instant: 6,     // quarter-second
  fast: 12,       // half-second
  normal: 18,     // 3/4-second
  slow: 30,       // one second
  verySlow: 60,   // two seconds
} as const;
```

**Step 2: Create `remotion/src/tokens/spacing.ts`**

```ts
// Named spacing values. All in px at 1080p; scale by (width/1080).
// Never use magic pixel numbers in templates — reference these instead.

export const sp = {
  /** Outer edge inset for all content. */
  edgeInset: 72,
  /** Standard gap between stacked elements. */
  gap: 24,
  /** Gap between title and artist. */
  metaGap: 16,
  /** Bottom safe area (9:16 accounts for TikTok/Reels chrome). */
  safeBottom_16_9: 160,
  /** Bottom safe area square/4:5. */
  safeBottom_square: 80,
  /** Logo zone top inset. */
  logoTop: 80,
  /** Waveform bottom clearance. */
  waveformBottom: 56,
} as const;
```

**Step 3: Create `remotion/src/tokens/typography.ts`**

```ts
// Typography tokens for Clipped.
// Sizes are expressed as fractions of min(width, height) — scale in components.
// Fonts loaded via @remotion/google-fonts in typography/fonts.ts.

export type TypographyPreset =
  | "cinematic"
  | "editorial"
  | "brutal"
  | "minimal"
  | "vhs"
  | "lyric";

type TypeLevel = {
  /** Size as fraction of min(width,height). */
  sizeFactor: number;
  weight: number;
  /** em units. Negative = tighter. */
  tracking: number;
  transform: "uppercase" | "none";
  fontFamily: "display" | "body" | "mono";
};

export type TypeScale = {
  trackTitle: TypeLevel;
  artistName: TypeLevel;
  metaLine: TypeLevel;
  lyricLine: TypeLevel & { lineHeight: number };
  lowerThird: TypeLevel;
};

const presets: Record<TypographyPreset, TypeScale> = {
  cinematic: {
    trackTitle:  { sizeFactor: 0.065, weight: 700, tracking: -0.02, transform: "none",      fontFamily: "display" },
    artistName:  { sizeFactor: 0.032, weight: 400, tracking:  0.10, transform: "uppercase", fontFamily: "body" },
    metaLine:    { sizeFactor: 0.022, weight: 400, tracking:  0.14, transform: "uppercase", fontFamily: "body" },
    lyricLine:   { sizeFactor: 0.042, weight: 600, tracking:  0,    transform: "none",      fontFamily: "body", lineHeight: 1.25 },
    lowerThird:  { sizeFactor: 0.020, weight: 500, tracking:  0.06, transform: "uppercase", fontFamily: "body" },
  },
  editorial: {
    trackTitle:  { sizeFactor: 0.072, weight: 700, tracking: -0.03, transform: "none",      fontFamily: "display" },
    artistName:  { sizeFactor: 0.030, weight: 400, tracking:  0.12, transform: "uppercase", fontFamily: "body" },
    metaLine:    { sizeFactor: 0.020, weight: 400, tracking:  0.16, transform: "uppercase", fontFamily: "body" },
    lyricLine:   { sizeFactor: 0.040, weight: 600, tracking:  0,    transform: "none",      fontFamily: "body", lineHeight: 1.3 },
    lowerThird:  { sizeFactor: 0.018, weight: 500, tracking:  0.08, transform: "uppercase", fontFamily: "body" },
  },
  brutal: {
    trackTitle:  { sizeFactor: 0.080, weight: 900, tracking: -0.01, transform: "uppercase", fontFamily: "display" },
    artistName:  { sizeFactor: 0.034, weight: 700, tracking:  0.06, transform: "uppercase", fontFamily: "display" },
    metaLine:    { sizeFactor: 0.022, weight: 700, tracking:  0.10, transform: "uppercase", fontFamily: "body" },
    lyricLine:   { sizeFactor: 0.048, weight: 900, tracking:  0,    transform: "uppercase", fontFamily: "display", lineHeight: 1.1 },
    lowerThird:  { sizeFactor: 0.022, weight: 700, tracking:  0.04, transform: "uppercase", fontFamily: "display" },
  },
  minimal: {
    trackTitle:  { sizeFactor: 0.058, weight: 500, tracking:  0,    transform: "none",      fontFamily: "body" },
    artistName:  { sizeFactor: 0.028, weight: 400, tracking:  0.08, transform: "uppercase", fontFamily: "body" },
    metaLine:    { sizeFactor: 0.018, weight: 400, tracking:  0.12, transform: "uppercase", fontFamily: "body" },
    lyricLine:   { sizeFactor: 0.038, weight: 500, tracking:  0,    transform: "none",      fontFamily: "body", lineHeight: 1.35 },
    lowerThird:  { sizeFactor: 0.017, weight: 400, tracking:  0.08, transform: "none",      fontFamily: "body" },
  },
  vhs: {
    trackTitle:  { sizeFactor: 0.060, weight: 700, tracking:  0.04, transform: "uppercase", fontFamily: "mono" },
    artistName:  { sizeFactor: 0.028, weight: 400, tracking:  0.10, transform: "uppercase", fontFamily: "mono" },
    metaLine:    { sizeFactor: 0.018, weight: 400, tracking:  0.14, transform: "uppercase", fontFamily: "mono" },
    lyricLine:   { sizeFactor: 0.040, weight: 700, tracking:  0.02, transform: "uppercase", fontFamily: "mono", lineHeight: 1.2 },
    lowerThird:  { sizeFactor: 0.018, weight: 400, tracking:  0.10, transform: "uppercase", fontFamily: "mono" },
  },
  lyric: {
    trackTitle:  { sizeFactor: 0.060, weight: 700, tracking: -0.01, transform: "none",      fontFamily: "display" },
    artistName:  { sizeFactor: 0.030, weight: 400, tracking:  0.08, transform: "uppercase", fontFamily: "body" },
    metaLine:    { sizeFactor: 0.020, weight: 400, tracking:  0.12, transform: "uppercase", fontFamily: "body" },
    lyricLine:   { sizeFactor: 0.046, weight: 700, tracking: -0.01, transform: "none",      fontFamily: "display", lineHeight: 1.28 },
    lowerThird:  { sizeFactor: 0.020, weight: 500, tracking:  0.06, transform: "none",      fontFamily: "body" },
  },
};

export const resolveTypeScale = (preset: TypographyPreset): TypeScale => presets[preset];

/** Resolve font-size in px from a sizeFactor and the viewport min dimension. */
export const typeSize = (sizeFactor: number, minDim: number): number =>
  Math.round(sizeFactor * minDim);
```

**Step 4: Patch `remotion/src/lib/palette.ts` — remove `motionFactor`, re-export**

Remove the `motionFactor` function body from `palette.ts` and replace with a re-export:

```ts
// At bottom of palette.ts, replace the motionFactor definition with:
export { motionFactor } from "../tokens/motion";
```

This keeps all existing imports working without touching templates yet.

**Step 5: Verify typecheck**

```bash
cd /Users/rd/Scripts/Riley/clipped/remotion && npm run typecheck 2>&1 | head -40
```

Expected: zero errors (only added files, patched an export).

**Step 6: Commit**

```bash
cd /Users/rd/Scripts/Riley/clipped && git add remotion/src/tokens/ remotion/src/lib/palette.ts && git commit -m "feat(tokens): add motion, spacing, typography token files"
```

---

### Task 1.2: Font loading module

**Files:**
- Create: `remotion/src/typography/fonts.ts`

**Context:** `@remotion/google-fonts` is already installed. `loadFont()` must be called at module scope (top level), not inside components. The return value is `{ fontFamily: string }`. Remotion will inject the font into the render environment automatically.

**Step 1: Create `remotion/src/typography/fonts.ts`**

```ts
// Font loading for Clipped typography system.
// loadFont() must be called at module top level — Remotion injects the CSS.
// Import { fonts } in any component that uses text.

import { loadFont as loadInter } from "@remotion/google-fonts/Inter";
import { loadFont as loadOswald } from "@remotion/google-fonts/Oswald";
import { loadFont as loadBebasNeue } from "@remotion/google-fonts/BebasNeue";
import { loadFont as loadSpaceMono } from "@remotion/google-fonts/SpaceMono";

const inter    = loadInter();
const oswald   = loadOswald();
const bebas    = loadBebasNeue();
const spaceMono = loadSpaceMono();

/**
 * Font family strings keyed by role.
 * "display" → Oswald (editorial/cinematic) or Bebas Neue (brutal)
 * "body"    → Inter
 * "mono"    → Space Mono (VHS/CRT)
 *
 * Usage: style={{ fontFamily: fonts.display }}
 */
export const fonts = {
  display:  oswald.fontFamily,
  brutal:   bebas.fontFamily,
  body:     inter.fontFamily,
  mono:     spaceMono.fontFamily,
} as const;

/**
 * Resolve fontFamily string from the token role + typography preset context.
 * "display" uses brutal face for brutal preset, oswald otherwise.
 */
export const resolveFont = (
  role: "display" | "body" | "mono",
  isBrutal = false,
): string => {
  if (role === "display") return isBrutal ? fonts.brutal : fonts.display;
  if (role === "mono") return fonts.mono;
  return fonts.body;
};
```

**Step 2: Verify typecheck**

```bash
cd /Users/rd/Scripts/Riley/clipped/remotion && npm run typecheck 2>&1 | head -20
```

**Step 3: Commit**

```bash
cd /Users/rd/Scripts/Riley/clipped && git add remotion/src/typography/fonts.ts && git commit -m "feat(typography): add font loading module (Inter, Oswald, Bebas Neue, Space Mono)"
```

---

### Task 1.3: Typography components — TrackTitle, ArtistName, MetaLine, MetadataStack

**Files:**
- Create: `remotion/src/typography/TrackTitle.tsx`
- Create: `remotion/src/typography/ArtistName.tsx`
- Create: `remotion/src/typography/MetaLine.tsx`
- Create: `remotion/src/typography/MetadataStack.tsx`
- Create: `remotion/src/typography/index.ts`

**Context:** Each component is a single text block with its own reveal animation. `MetadataStack` composes the three with staggered reveals. All sizes are computed from `typeSize(sizeFactor, minDim)`. No magic pixel values. No Arial. Shadow is a single consistent value: `0 3px 14px rgba(0,0,0,0.65)`.

**Step 1: Create `remotion/src/typography/TrackTitle.tsx`**

```tsx
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import type { CSSProperties } from "react";
import type { TypographyPreset } from "../tokens/typography";
import { resolveTypeScale, typeSize } from "../tokens/typography";
import { resolveFont } from "./fonts";

export const TrackTitle = ({
  text,
  preset = "cinematic",
  color = "white",
  revealFrame = 0,
  align = "center",
  maxWidth,
}: {
  text: string;
  preset?: TypographyPreset;
  color?: string;
  revealFrame?: number;
  align?: CSSProperties["textAlign"];
  maxWidth?: number | string;
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const scale = resolveTypeScale(preset);
  const t = scale.trackTitle;
  const minDim = Math.min(width, height);
  const size = typeSize(t.sizeFactor, minDim);
  const isBrutal = preset === "brutal";

  const reveal = spring({ frame: frame - revealFrame, fps, config: { damping: 26, stiffness: 120 } });
  const opacity = interpolate(reveal, [0, 1], [0, 1]);
  const translateY = interpolate(reveal, [0, 1], [18, 0]);

  return (
    <div
      style={{
        fontFamily: resolveFont(t.fontFamily, isBrutal),
        fontSize: size,
        fontWeight: t.weight,
        letterSpacing: `${t.tracking}em`,
        textTransform: t.transform,
        color,
        textAlign: align,
        lineHeight: 1.1,
        textShadow: "0 3px 14px rgba(0,0,0,0.65)",
        opacity,
        transform: `translateY(${translateY}px)`,
        maxWidth: maxWidth ?? "100%",
      }}
    >
      {text}
    </div>
  );
};
```

**Step 2: Create `remotion/src/typography/ArtistName.tsx`**

```tsx
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import type { CSSProperties } from "react";
import type { TypographyPreset } from "../tokens/typography";
import { resolveTypeScale, typeSize } from "../tokens/typography";
import { resolveFont } from "./fonts";

export const ArtistName = ({
  text,
  preset = "cinematic",
  color,
  revealFrame = 8,
  align = "center",
}: {
  text: string;
  preset?: TypographyPreset;
  color?: string;
  revealFrame?: number;
  align?: CSSProperties["textAlign"];
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const scale = resolveTypeScale(preset);
  const t = scale.artistName;
  const minDim = Math.min(width, height);
  const size = typeSize(t.sizeFactor, minDim);
  const isBrutal = preset === "brutal";

  const reveal = spring({ frame: frame - revealFrame, fps, config: { damping: 26, stiffness: 120 } });
  const opacity = interpolate(reveal, [0, 1], [0, 1]);
  const translateY = interpolate(reveal, [0, 1], [14, 0]);

  return (
    <div
      style={{
        fontFamily: resolveFont(t.fontFamily, isBrutal),
        fontSize: size,
        fontWeight: t.weight,
        letterSpacing: `${t.tracking}em`,
        textTransform: t.transform,
        color: color ?? "rgba(255,255,255,0.72)",
        textAlign: align,
        lineHeight: 1.2,
        textShadow: "0 2px 10px rgba(0,0,0,0.55)",
        opacity,
        transform: `translateY(${translateY}px)`,
      }}
    >
      {text}
    </div>
  );
};
```

**Step 3: Create `remotion/src/typography/MetaLine.tsx`**

```tsx
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import type { CSSProperties } from "react";
import type { TypographyPreset } from "../tokens/typography";
import { resolveTypeScale, typeSize } from "../tokens/typography";
import { resolveFont } from "./fonts";

export const MetaLine = ({
  text,
  preset = "cinematic",
  color,
  revealFrame = 16,
  align = "center",
}: {
  text: string;
  preset?: TypographyPreset;
  color?: string;
  revealFrame?: number;
  align?: CSSProperties["textAlign"];
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const scale = resolveTypeScale(preset);
  const t = scale.metaLine;
  const minDim = Math.min(width, height);
  const size = typeSize(t.sizeFactor, minDim);
  const isBrutal = preset === "brutal";

  const reveal = spring({ frame: frame - revealFrame, fps, config: { damping: 26, stiffness: 120 } });
  const opacity = interpolate(reveal, [0, 1], [0, 0.8]);
  const translateY = interpolate(reveal, [0, 1], [10, 0]);

  return (
    <div
      style={{
        fontFamily: resolveFont(t.fontFamily, isBrutal),
        fontSize: size,
        fontWeight: t.weight,
        letterSpacing: `${t.tracking}em`,
        textTransform: t.transform,
        color: color ?? "rgba(255,255,255,0.52)",
        textAlign: align,
        lineHeight: 1.3,
        opacity,
        transform: `translateY(${translateY}px)`,
      }}
    >
      {text}
    </div>
  );
};
```

**Step 4: Create `remotion/src/typography/MetadataStack.tsx`**

```tsx
import type { CSSProperties } from "react";
import type { TypographyPreset } from "../tokens/typography";
import { TrackTitle } from "./TrackTitle";
import { ArtistName } from "./ArtistName";
import { MetaLine } from "./MetaLine";
import { sp } from "../tokens/spacing";

export const MetadataStack = ({
  title,
  artist,
  meta,
  preset = "cinematic",
  accentColor,
  textColor,
  revealFrame = 0,
  align = "center",
  gap,
}: {
  title: string;
  artist: string;
  meta?: string;
  preset?: TypographyPreset;
  accentColor?: string;
  textColor?: string;
  revealFrame?: number;
  align?: CSSProperties["textAlign"];
  gap?: number;
}) => {
  const gapPx = gap ?? sp.metaGap;

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: align === "center" ? "center" : align === "left" ? "flex-start" : "flex-end", gap: gapPx }}>
      <TrackTitle  text={title}  preset={preset} color={textColor}        revealFrame={revealFrame}      align={align} />
      <ArtistName  text={artist} preset={preset}                          revealFrame={revealFrame + 8}  align={align} />
      {meta ? <MetaLine text={meta} preset={preset} color={accentColor} revealFrame={revealFrame + 16} align={align} /> : null}
    </div>
  );
};
```

**Step 5: Create `remotion/src/typography/index.ts`**

```ts
export { TrackTitle } from "./TrackTitle";
export { ArtistName } from "./ArtistName";
export { MetaLine } from "./MetaLine";
export { MetadataStack } from "./MetadataStack";
export { fonts, resolveFont } from "./fonts";
export { resolveTypeScale, typeSize } from "../tokens/typography";
export type { TypographyPreset, TypeScale } from "../tokens/typography";
```

**Step 6: Typecheck**

```bash
cd /Users/rd/Scripts/Riley/clipped/remotion && npm run typecheck 2>&1 | head -30
```

Expected: 0 errors.

**Step 7: Commit**

```bash
cd /Users/rd/Scripts/Riley/clipped && git add remotion/src/typography/ && git commit -m "feat(typography): TrackTitle, ArtistName, MetaLine, MetadataStack components"
```

---

### Task 1.4: Layout engine — zones, safe areas, useLayout hook

**Files:**
- Create: `remotion/src/layouts/zones.ts`
- Create: `remotion/src/layouts/safe-zones.ts`
- Create: `remotion/src/layouts/useLayout.ts`
- Create: `remotion/src/layouts/index.ts`

**Step 1: Create `remotion/src/layouts/safe-zones.ts`**

```ts
// Safe area insets as fractions of frame dimension.
// Source: TikTok/Reels UI chrome measurements, Instagram safe zone specs.

export type AspectClass = "square" | "vertical" | "horizontal";

export const classifyAspect = (width: number, height: number): AspectClass => {
  const ratio = width / height;
  if (ratio > 1.2) return "horizontal";
  if (ratio < 0.9) return "vertical";
  return "square";
};

type SafeInsets = { top: number; right: number; bottom: number; left: number };

/** Safe area insets as fractions of frame width/height. */
export const safeZones: Record<AspectClass, SafeInsets> = {
  square:     { top: 0.08, right: 0.08, bottom: 0.08, left: 0.08 },
  vertical:   { top: 0.12, right: 0.06, bottom: 0.16, left: 0.06 },
  horizontal: { top: 0.08, right: 0.08, bottom: 0.08, left: 0.08 },
};

/** Returns pixel safe insets for a given frame size. */
export const getSafeInsets = (width: number, height: number) => {
  const cls = classifyAspect(width, height);
  const z = safeZones[cls];
  return {
    top:    z.top    * height,
    right:  z.right  * width,
    bottom: z.bottom * height,
    left:   z.left   * width,
  };
};
```

**Step 2: Create `remotion/src/layouts/zones.ts`**

```ts
// Named layout zone definitions.
// All values are fractions (0–1) of frame width/height.
// Resolve to pixels with resolveZone().

import type { AspectClass } from "./safe-zones";

export type ZoneName = "centered" | "editorial-left" | "editorial-right" | "lower-third" | "poster";

type ZoneFractions = {
  /** Artwork bounding box. */
  artwork: { cx: number; cy: number; size: number };
  /** Typography anchor point. left/top as fraction, width as fraction. */
  typography: { left: number; top: number; width: number; align: "center" | "left" | "right" };
  /** Visualizer strip. cx, bottom as fraction from bottom. */
  visualizer: { cx: number; bottom: number; width: number };
  /** Logo zone. cx, top as fraction from top. */
  logo: { cx: number; top: number; width: number };
};

type LayoutDef = Record<AspectClass, ZoneFractions>;

const layouts: Record<ZoneName, LayoutDef> = {
  "centered": {
    square:     { artwork: { cx: 0.50, cy: 0.42, size: 0.60 }, typography: { left: 0.10, top: 0.74, width: 0.80, align: "center" }, visualizer: { cx: 0.50, bottom: 0.07, width: 0.76 }, logo: { cx: 0.50, top: 0.07, width: 0.54 } },
    vertical:   { artwork: { cx: 0.50, cy: 0.38, size: 0.64 }, typography: { left: 0.08, top: 0.70, width: 0.84, align: "center" }, visualizer: { cx: 0.50, bottom: 0.18, width: 0.80 }, logo: { cx: 0.50, top: 0.08, width: 0.58 } },
    horizontal: { artwork: { cx: 0.50, cy: 0.44, size: 0.50 }, typography: { left: 0.12, top: 0.74, width: 0.76, align: "center" }, visualizer: { cx: 0.50, bottom: 0.06, width: 0.72 }, logo: { cx: 0.50, top: 0.06, width: 0.48 } },
  },
  "editorial-left": {
    square:     { artwork: { cx: 0.68, cy: 0.42, size: 0.52 }, typography: { left: 0.06, top: 0.30, width: 0.44, align: "left" },   visualizer: { cx: 0.50, bottom: 0.07, width: 0.76 }, logo: { cx: 0.22, top: 0.08, width: 0.34 } },
    vertical:   { artwork: { cx: 0.50, cy: 0.36, size: 0.64 }, typography: { left: 0.08, top: 0.68, width: 0.84, align: "left" },   visualizer: { cx: 0.50, bottom: 0.18, width: 0.80 }, logo: { cx: 0.28, top: 0.08, width: 0.40 } },
    horizontal: { artwork: { cx: 0.70, cy: 0.44, size: 0.44 }, typography: { left: 0.05, top: 0.26, width: 0.42, align: "left" },   visualizer: { cx: 0.50, bottom: 0.06, width: 0.72 }, logo: { cx: 0.20, top: 0.06, width: 0.30 } },
  },
  "editorial-right": {
    square:     { artwork: { cx: 0.32, cy: 0.42, size: 0.52 }, typography: { left: 0.50, top: 0.30, width: 0.44, align: "left" },   visualizer: { cx: 0.50, bottom: 0.07, width: 0.76 }, logo: { cx: 0.72, top: 0.08, width: 0.34 } },
    vertical:   { artwork: { cx: 0.50, cy: 0.36, size: 0.64 }, typography: { left: 0.08, top: 0.68, width: 0.84, align: "right" },  visualizer: { cx: 0.50, bottom: 0.18, width: 0.80 }, logo: { cx: 0.72, top: 0.08, width: 0.40 } },
    horizontal: { artwork: { cx: 0.30, cy: 0.44, size: 0.44 }, typography: { left: 0.52, top: 0.26, width: 0.42, align: "left" },   visualizer: { cx: 0.50, bottom: 0.06, width: 0.72 }, logo: { cx: 0.78, top: 0.06, width: 0.30 } },
  },
  "lower-third": {
    square:     { artwork: { cx: 0.50, cy: 0.42, size: 0.72 }, typography: { left: 0.08, top: 0.78, width: 0.84, align: "left" },   visualizer: { cx: 0.50, bottom: 0.05, width: 0.76 }, logo: { cx: 0.50, top: 0.07, width: 0.50 } },
    vertical:   { artwork: { cx: 0.50, cy: 0.40, size: 0.78 }, typography: { left: 0.08, top: 0.76, width: 0.84, align: "left" },   visualizer: { cx: 0.50, bottom: 0.18, width: 0.80 }, logo: { cx: 0.50, top: 0.08, width: 0.54 } },
    horizontal: { artwork: { cx: 0.50, cy: 0.44, size: 0.58 }, typography: { left: 0.06, top: 0.76, width: 0.84, align: "left" },   visualizer: { cx: 0.50, bottom: 0.05, width: 0.72 }, logo: { cx: 0.50, top: 0.06, width: 0.46 } },
  },
  "poster": {
    square:     { artwork: { cx: 0.50, cy: 0.50, size: 1.00 }, typography: { left: 0.08, top: 0.10, width: 0.84, align: "center" }, visualizer: { cx: 0.50, bottom: 0.07, width: 0.76 }, logo: { cx: 0.50, top: 0.05, width: 0.50 } },
    vertical:   { artwork: { cx: 0.50, cy: 0.50, size: 1.00 }, typography: { left: 0.08, top: 0.08, width: 0.84, align: "center" }, visualizer: { cx: 0.50, bottom: 0.18, width: 0.80 }, logo: { cx: 0.50, top: 0.05, width: 0.54 } },
    horizontal: { artwork: { cx: 0.50, cy: 0.50, size: 1.00 }, typography: { left: 0.08, top: 0.10, width: 0.84, align: "center" }, visualizer: { cx: 0.50, bottom: 0.05, width: 0.72 }, logo: { cx: 0.50, top: 0.05, width: 0.46 } },
  },
};

export const getZone = (name: ZoneName, aspect: AspectClass): ZoneFractions =>
  layouts[name][aspect];
```

**Step 3: Create `remotion/src/layouts/useLayout.ts`**

```ts
import { useVideoConfig } from "remotion";
import type { ZoneName } from "./zones";
import { getZone } from "./zones";
import { classifyAspect, getSafeInsets } from "./safe-zones";

/** Returns resolved pixel values for the named layout zone. */
export const useLayout = (name: ZoneName) => {
  const { width, height } = useVideoConfig();
  const aspect = classifyAspect(width, height);
  const zone = getZone(name, aspect);
  const safe = getSafeInsets(width, height);

  return {
    /** Artwork center in pixels. */
    artwork: {
      cx: zone.artwork.cx * width,
      cy: zone.artwork.cy * height,
      /** Square artwork side length. */
      size: zone.artwork.size * Math.min(width, height),
    },
    /** Typography anchor in pixels. */
    typography: {
      left:  zone.typography.left  * width,
      top:   zone.typography.top   * height,
      width: zone.typography.width * width,
      align: zone.typography.align,
    },
    /** Visualizer strip in pixels. */
    visualizer: {
      cx:     zone.visualizer.cx     * width,
      bottom: zone.visualizer.bottom * height,
      width:  zone.visualizer.width  * width,
    },
    /** Logo zone in pixels. */
    logo: {
      cx:    zone.logo.cx    * width,
      top:   zone.logo.top   * height,
      width: zone.logo.width * width,
    },
    safe,
    width,
    height,
    aspect,
  };
};
```

**Step 4: Create `remotion/src/layouts/index.ts`**

```ts
export { useLayout } from "./useLayout";
export { getZone } from "./zones";
export { getSafeInsets, classifyAspect } from "./safe-zones";
export type { ZoneName } from "./zones";
export type { AspectClass } from "./safe-zones";
```

**Step 5: Typecheck + commit**

```bash
cd /Users/rd/Scripts/Riley/clipped/remotion && npm run typecheck 2>&1 | head -20
cd /Users/rd/Scripts/Riley/clipped && git add remotion/src/layouts/ && git commit -m "feat(layouts): zone definitions, safe-area constants, useLayout hook"
```

---

## Phase 2 — Transition Engine

### Task 2.1: Transition primitives — BlurDissolve, LumaFade, TextFadeUp, TextTrackIn

**Files:**
- Create: `remotion/src/transitions/BlurDissolve.tsx`
- Create: `remotion/src/transitions/LumaFade.tsx`
- Create: `remotion/src/transitions/TextFadeUp.tsx`
- Create: `remotion/src/transitions/TextTrackIn.tsx`
- Create: `remotion/src/transitions/index.ts`

**Context:** Transitions in Remotion are not scene-level cuts — they are element-level animations driven by an explicit `progress` prop (0→1). The caller drives `progress` via `interpolate(frame, [startFrame, endFrame], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })`. Transitions wrap children via `style` mutation.

**Step 1: Create `remotion/src/transitions/BlurDissolve.tsx`**

Smoothly blurs and fades a child out, then in. Pass `progress` 0→0.5 for exit, 0.5→1 for entrance. Caller controls which direction.

```tsx
import type { ReactNode, CSSProperties } from "react";

/**
 * Blur-dissolve transition wrapper.
 *
 * progress 0   = fully visible, sharp
 * progress 0.5 = peak blur / invisible
 * progress 1   = fully visible, sharp (new content)
 *
 * Use for artwork crossfades and cover-to-cover transitions.
 * maxBlur: CSS blur in px at peak. Default 24.
 */
export const BlurDissolve = ({
  progress,
  children,
  maxBlur = 24,
  style,
}: {
  progress: number;
  children: ReactNode;
  maxBlur?: number;
  style?: CSSProperties;
}) => {
  // 0→0.5: fade + blur out. 0.5→1: fade + blur in.
  const half = Math.abs(progress - 0.5) * 2; // 1 at 0 and 1, 0 at 0.5
  const opacity = half;
  const blur = (1 - half) * maxBlur;

  return (
    <div
      style={{
        ...style,
        opacity,
        filter: blur > 0.5 ? `blur(${blur.toFixed(1)}px)` : undefined,
        willChange: "opacity, filter",
      }}
    >
      {children}
    </div>
  );
};
```

**Step 2: Create `remotion/src/transitions/LumaFade.tsx`**

Brightness ramps to white then back — film burn style cut.

```tsx
import { AbsoluteFill } from "remotion";

/**
 * LumaFade — flash to near-white and back.
 * progress 0 = transparent, 0.5 = peak white, 1 = transparent.
 * Use for scene cuts in metal/vhs presets.
 */
export const LumaFade = ({
  progress,
  color = "rgba(255,255,255,0.92)",
  peakOpacity = 0.88,
}: {
  progress: number;
  color?: string;
  peakOpacity?: number;
}) => {
  if (progress <= 0 || progress >= 1) return null;
  // Bell curve: 0 at 0 and 1, max at 0.5
  const peak = 1 - Math.abs(progress - 0.5) * 2;
  const opacity = peak * peakOpacity;

  return (
    <AbsoluteFill
      style={{
        pointerEvents: "none",
        backgroundColor: color,
        opacity,
        mixBlendMode: "screen",
      }}
    />
  );
};
```

**Step 3: Create `remotion/src/transitions/TextFadeUp.tsx`**

Standard text entrance — fade + translate up. Wraps any child.

```tsx
import type { ReactNode, CSSProperties } from "react";

/**
 * TextFadeUp — standard metadata/caption entrance.
 * progress 0 = invisible below, 1 = fully visible at rest.
 * riseDistance: px to travel. Default 20.
 *
 * Caller drives progress via spring or interpolate.
 */
export const TextFadeUp = ({
  progress,
  children,
  riseDistance = 20,
  style,
}: {
  progress: number;
  children: ReactNode;
  riseDistance?: number;
  style?: CSSProperties;
}) => {
  const clampedP = Math.max(0, Math.min(1, progress));
  return (
    <div
      style={{
        ...style,
        opacity: clampedP,
        transform: `translateY(${(1 - clampedP) * riseDistance}px)`,
        willChange: "opacity, transform",
      }}
    >
      {children}
    </div>
  );
};
```

**Step 4: Create `remotion/src/transitions/TextTrackIn.tsx`**

Title entrance: letter-spacing collapses from wide (+0.2em) to target. Runs for 18 frames.

```tsx
import type { ReactNode, CSSProperties } from "react";

/**
 * TextTrackIn — editorial title entrance via letter-spacing collapse.
 * progress 0 = wide tracking, 1 = final tracking.
 * targetTracking: final em value (from typography token). Default -0.02.
 * startTracking: wide em value to start from. Default 0.22.
 */
export const TextTrackIn = ({
  progress,
  children,
  targetTracking = -0.02,
  startTracking = 0.22,
  style,
}: {
  progress: number;
  children: ReactNode;
  targetTracking?: number;
  startTracking?: number;
  style?: CSSProperties;
}) => {
  const clampedP = Math.max(0, Math.min(1, progress));
  const tracking = startTracking + (targetTracking - startTracking) * clampedP;
  const opacity = Math.min(1, clampedP * 1.5); // fade in faster than tracking collapses

  return (
    <div
      style={{
        ...style,
        opacity,
        letterSpacing: `${tracking}em`,
        willChange: "opacity, letter-spacing",
      }}
    >
      {children}
    </div>
  );
};
```

**Step 5: Create `remotion/src/transitions/index.ts`**

```ts
export { BlurDissolve } from "./BlurDissolve";
export { LumaFade } from "./LumaFade";
export { TextFadeUp } from "./TextFadeUp";
export { TextTrackIn } from "./TextTrackIn";
```

**Step 6: Typecheck + commit**

```bash
cd /Users/rd/Scripts/Riley/clipped/remotion && npm run typecheck 2>&1 | head -20
cd /Users/rd/Scripts/Riley/clipped && git add remotion/src/transitions/ && git commit -m "feat(transitions): BlurDissolve, LumaFade, TextFadeUp, TextTrackIn"
```

---

## Phase 3 — Masking / Frame / Material System

### Task 3.1: ArtworkBackground with atmospheric modes

**Files:**
- Create: `remotion/src/artwork/ArtworkBackground.tsx`
- Modify: `remotion/src/components/Artwork.tsx` (re-export `ArtworkBackground`, deprecate `BackgroundField`)

**Step 1: Create `remotion/src/artwork/ArtworkBackground.tsx`**

```tsx
import { Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import type { Palette } from "../lib/palette";

export type BackgroundMode = "atmospheric" | "editorial" | "minimal" | "color";

/**
 * ArtworkBackground — cinematic blurred background field.
 *
 * atmospheric: heavy blur (40px), desaturated (0.45), color-graded dark
 * editorial:   moderate blur (20px), moderate saturation (0.7), higher contrast
 * minimal:     no image — solid bg color
 * color:       solid extracted/palette color (set via `solidColor` prop)
 *
 * Replaces BackgroundField. BackgroundField stays in Artwork.tsx as a
 * re-export alias for backwards compatibility.
 */
export const ArtworkBackground = ({
  src,
  palette,
  mode = "atmospheric",
  solidColor,
  driftIntensity = 0.035,
}: {
  src: string | null;
  palette: Palette;
  mode?: BackgroundMode;
  solidColor?: string;
  driftIntensity?: number;
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const resolvedSrc = src ? staticFile(src) : null;

  if (mode === "minimal" || mode === "color") {
    return (
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundColor: solidColor ?? palette.bg,
        }}
      />
    );
  }

  const blurAmount = mode === "editorial" ? 20 : 40;
  const saturation = mode === "editorial" ? 0.70 : 0.45;
  const brightness = mode === "editorial" ? 0.50 : 0.38;
  const scale = interpolate(frame, [0, durationInFrames], [1, 1.04 + driftIntensity]);

  return (
    <div style={{ position: "absolute", inset: 0, overflow: "hidden", backgroundColor: palette.bg }}>
      {resolvedSrc ? (
        <Img
          src={resolvedSrc}
          style={{
            position: "absolute",
            inset: "-8%",
            width: "116%",
            height: "116%",
            objectFit: "cover",
            transform: `scale(${scale})`,
            filter: `blur(${blurAmount}px) brightness(${brightness}) saturate(${saturation})`,
          }}
        />
      ) : (
        <div style={{ position: "absolute", inset: 0, backgroundColor: palette.bg }} />
      )}
      {/* Vignette gradient — dark edges, transparent center */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: "radial-gradient(circle at center, transparent 30%, rgba(0,0,0,0.72) 100%)",
        }}
      />
    </div>
  );
};
```

**Step 2: Patch `remotion/src/components/Artwork.tsx` — add re-export alias**

At the bottom of `Artwork.tsx`, add:

```ts
// Backwards-compat alias. New code should import from artwork/ArtworkBackground.
export { ArtworkBackground } from "../artwork/ArtworkBackground";
/** @deprecated Use ArtworkBackground from artwork/ArtworkBackground */
export const BackgroundFieldV2 = ArtworkBackground;
```

Leave the existing `BackgroundField` intact so templates keep compiling.

**Step 3: Typecheck + commit**

```bash
cd /Users/rd/Scripts/Riley/clipped/remotion && npm run typecheck 2>&1 | head -20
cd /Users/rd/Scripts/Riley/clipped && git add remotion/src/artwork/ remotion/src/components/Artwork.tsx && git commit -m "feat(artwork): ArtworkBackground with atmospheric/editorial/minimal modes"
```

---

### Task 3.2: Material frame system — MatteBorder, ChromeBorder, VinylSleeve

**Files:**
- Create: `remotion/src/materials/MatteBorder.tsx`
- Create: `remotion/src/materials/ChromeBorder.tsx`
- Create: `remotion/src/materials/VinylSleeve.tsx`
- Create: `remotion/src/materials/ArtworkFrame.tsx`
- Create: `remotion/src/materials/index.ts`

**Step 1: Create `remotion/src/materials/MatteBorder.tsx`**

```tsx
import type { ReactNode, CSSProperties } from "react";

/**
 * MatteBorder — warm off-white matte frame around artwork.
 * thickness: border px. Default 10.
 * color: matte color. Default warm off-white.
 * radius: corner radius of inner content. Default 4.
 */
export const MatteBorder = ({
  size,
  thickness = 10,
  color = "#f2ede6",
  radius = 4,
  children,
  style,
}: {
  size: number;
  thickness?: number;
  color?: string;
  radius?: number;
  children?: ReactNode;
  style?: CSSProperties;
}) => (
  <div
    style={{
      width: size,
      height: size,
      padding: thickness,
      backgroundColor: color,
      borderRadius: radius + thickness,
      boxShadow: "0 40px 80px rgba(0,0,0,0.72)",
      ...style,
    }}
  >
    <div
      style={{
        width: "100%",
        height: "100%",
        overflow: "hidden",
        borderRadius: radius,
      }}
    >
      {children}
    </div>
  </div>
);
```

**Step 2: Create `remotion/src/materials/ChromeBorder.tsx`**

```tsx
import type { ReactNode, CSSProperties } from "react";

/**
 * ChromeBorder — razor-thin metallic gradient border.
 * thickness: border px. Default 2.
 * radius: corner radius. Default 6.
 */
export const ChromeBorder = ({
  size,
  thickness = 2,
  radius = 6,
  children,
  style,
}: {
  size: number;
  thickness?: number;
  radius?: number;
  children?: ReactNode;
  style?: CSSProperties;
}) => (
  <div
    style={{
      width: size,
      height: size,
      padding: thickness,
      background: "conic-gradient(from 135deg, #888 0%, #fff 25%, #aaa 50%, #fff 75%, #888 100%)",
      borderRadius: radius + thickness,
      boxShadow: "0 30px 70px rgba(0,0,0,0.72)",
      ...style,
    }}
  >
    <div
      style={{
        width: "100%",
        height: "100%",
        overflow: "hidden",
        borderRadius: radius,
      }}
    >
      {children}
    </div>
  </div>
);
```

**Step 3: Create `remotion/src/materials/VinylSleeve.tsx`**

Renders a dark sleeve peek entering from bottom-right behind the record.

```tsx
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";

/**
 * VinylSleeve — sleeve peek entering from bottom-right behind the record.
 * size: approximately record diameter.
 * y: vertical offset of record center from frame center.
 * progress: 0 = off-screen, 1 = settled peek visible.
 */
export const VinylSleeve = ({
  size,
  y = 0,
  progress = 1,
}: {
  size: number;
  y?: number;
  progress?: number;
}) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();

  const sleeveW = size * 0.92;
  const sleeveH = size * 0.94;
  const peekX = interpolate(progress, [0, 1], [size * 0.5, size * 0.08]);
  const peekY = interpolate(progress, [0, 1], [size * 0.5, size * 0.10]);

  // Slow micro-wobble for life
  const wobble = Math.sin(frame / 90) * 1.5;

  return (
    <div
      style={{
        position: "absolute",
        left: "50%",
        top: "50%",
        width: sleeveW,
        height: sleeveH,
        transform: `translate(calc(-50% + ${peekX + wobble}px), calc(-50% + ${y + peekY}px))`,
        borderRadius: 8,
        background: "linear-gradient(135deg, #1a1a1a 0%, #0d0d0d 60%, #222 100%)",
        boxShadow: "inset -4px -4px 20px rgba(255,255,255,0.04), 0 20px 60px rgba(0,0,0,0.8)",
        zIndex: 1, // behind VinylRecord (z:2)
      }}
    />
  );
};
```

**Step 4: Create `remotion/src/materials/ArtworkFrame.tsx`**

```tsx
import type { ReactNode } from "react";
import { MatteBorder } from "./MatteBorder";
import { ChromeBorder } from "./ChromeBorder";

export type FramePreset = "none" | "matte" | "chrome" | "vinyl-sleeve";

/**
 * ArtworkFrame — wraps children in the selected frame material.
 * size: frame outer dimension in px.
 * preset: frame style.
 */
export const ArtworkFrame = ({
  size,
  preset = "matte",
  children,
}: {
  size: number;
  preset?: FramePreset;
  children: ReactNode;
}) => {
  if (preset === "matte") {
    return <MatteBorder size={size}>{children}</MatteBorder>;
  }
  if (preset === "chrome") {
    return <ChromeBorder size={size}>{children}</ChromeBorder>;
  }
  // "none" or "vinyl-sleeve" — bare (sleeve is rendered separately)
  return (
    <div
      style={{
        width: size,
        height: size,
        overflow: "hidden",
        borderRadius: 6,
        boxShadow: "0 36px 90px rgba(0,0,0,0.72)",
      }}
    >
      {children}
    </div>
  );
};
```

**Step 5: Create `remotion/src/materials/index.ts`**

```ts
export { ArtworkFrame } from "./ArtworkFrame";
export { MatteBorder } from "./MatteBorder";
export { ChromeBorder } from "./ChromeBorder";
export { VinylSleeve } from "./VinylSleeve";
export type { FramePreset } from "./ArtworkFrame";
```

**Step 6: Typecheck + commit**

```bash
cd /Users/rd/Scripts/Riley/clipped/remotion && npm run typecheck 2>&1 | head -20
cd /Users/rd/Scripts/Riley/clipped && git add remotion/src/materials/ && git commit -m "feat(materials): ArtworkFrame, MatteBorder, ChromeBorder, VinylSleeve"
```

---

### Task 3.3: VinylRecord decomposition

**Files:**
- Create: `remotion/src/vinyl/VinylDisc.tsx`
- Create: `remotion/src/vinyl/VinylSpecular.tsx`
- Create: `remotion/src/vinyl/VinylLabel.tsx`
- Create: `remotion/src/vinyl/VinylReflection.tsx`
- Modify: `remotion/src/components/vinyl/VinylRecord.tsx` (replace internals, compose new parts)

**Step 1: Create `remotion/src/vinyl/VinylDisc.tsx`**

```tsx
import { useCurrentFrame } from "remotion";
import { motionFactor } from "../tokens/motion";

/**
 * VinylDisc — rotating disc base with groove rings.
 * No glow. No accent color. Pure material.
 */
export const VinylDisc = ({
  size,
  motion = "medium",
  children,
}: {
  size: number;
  motion?: string;
  children?: React.ReactNode;
}) => {
  const frame = useCurrentFrame();
  const mf = motionFactor(motion);
  // 33.3 RPM → 200°/s → at 30fps: 200/30 ≈ 6.67°/frame
  const rotation = frame * (200 / 30) * mf;

  const grooveCount = 40;

  return (
    <div
      style={{
        width: size,
        height: size,
        borderRadius: "50%",
        transform: `rotate(${rotation}deg)`,
        background: "radial-gradient(circle at center, #080808 0%, #131313 30%, #060606 55%, #181818 72%, #030303 100%)",
        // Cinematic shadow — no colored accent glow
        boxShadow: "0 60px 90px rgba(0,0,0,0.88), 0 0 0 1px rgba(255,255,255,0.04)",
        overflow: "hidden",
        position: "relative",
      }}
    >
      {/* Groove rings */}
      {Array.from({ length: grooveCount }).map((_, i) => {
        const inset = 16 + i * (size / 120);
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              inset,
              borderRadius: "50%",
              border: "1px solid rgba(255,255,255,0.04)",
            }}
          />
        );
      })}
      {children}
    </div>
  );
};
```

**Step 2: Create `remotion/src/vinyl/VinylSpecular.tsx`**

The specular highlight counter-rotates so it stays fixed in world space.

```tsx
import { useCurrentFrame } from "remotion";
import { motionFactor } from "../tokens/motion";

/**
 * VinylSpecular — world-space fixed specular highlight.
 * Counter-rotates against VinylDisc so the sheen stays stationary
 * while grooves spin underneath — physically correct.
 * Must be rendered OUTSIDE VinylDisc (not as a child).
 */
export const VinylSpecular = ({
  size,
  motion = "medium",
  opacity = 0.38,
}: {
  size: number;
  motion?: string;
  opacity?: number;
}) => {
  const frame = useCurrentFrame();
  const mf = motionFactor(motion);
  const counterRotation = -(frame * (200 / 30) * mf);

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        width: size,
        height: size,
        borderRadius: "50%",
        transform: `rotate(${counterRotation}deg)`,
        background: "conic-gradient(from 30deg, rgba(255,255,255,0.18), transparent 20%, rgba(255,255,255,0.08) 30%, transparent 52%, rgba(255,255,255,0.14), transparent 76%)",
        mixBlendMode: "screen",
        opacity,
        pointerEvents: "none",
      }}
    />
  );
};
```

**Step 3: Create `remotion/src/vinyl/VinylLabel.tsx`**

```tsx
import { Img, staticFile } from "remotion";

/**
 * VinylLabel — centered label zone with artwork and spindle hole.
 * labelScale: fraction of disc size. Default 0.34.
 */
export const VinylLabel = ({
  discSize,
  imageSrc,
  labelScale = 0.34,
}: {
  discSize: number;
  imageSrc: string | null;
  labelScale?: number;
}) => {
  const labelSize = discSize * labelScale;
  const spindleSize = discSize * 0.048;
  const src = imageSrc ? staticFile(imageSrc) : null;

  return (
    <>
      {/* Label disk */}
      <div
        style={{
          position: "absolute",
          left: "50%",
          top: "50%",
          width: labelSize,
          height: labelSize,
          transform: "translate(-50%, -50%)",
          borderRadius: "50%",
          overflow: "hidden",
          background: "#111",
          boxShadow: "0 0 20px rgba(0,0,0,0.6)",
        }}
      >
        {src ? (
          <Img src={src} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
        ) : null}
      </div>
      {/* Spindle hole */}
      <div
        style={{
          position: "absolute",
          left: "50%",
          top: "50%",
          width: spindleSize,
          height: spindleSize,
          transform: "translate(-50%, -50%)",
          borderRadius: "50%",
          background: "#080808",
          boxShadow: "inset 0 0 8px rgba(255,255,255,0.18)",
          zIndex: 2,
        }}
      />
    </>
  );
};
```

**Step 4: Create `remotion/src/vinyl/VinylReflection.tsx`**

```tsx
/**
 * VinylReflection — subtle floor reflection below the disc.
 * Renders a gradient oval shadow/reflection below the record.
 * opacity: 0.10–0.20 recommended.
 */
export const VinylReflection = ({
  size,
  y = 0,
  opacity = 0.14,
}: {
  size: number;
  y?: number;
  opacity?: number;
}) => {
  const reflectionH = size * 0.18;
  const reflectionW = size * 0.80;

  return (
    <div
      style={{
        position: "absolute",
        left: "50%",
        top: "50%",
        width: reflectionW,
        height: reflectionH,
        transform: `translate(-50%, calc(${size * 0.5 + y}px))`,
        background: "radial-gradient(ellipse at center, rgba(255,255,255,0.18) 0%, transparent 70%)",
        filter: "blur(10px)",
        opacity,
        pointerEvents: "none",
      }}
    />
  );
};
```

**Step 5: Rewrite `remotion/src/components/vinyl/VinylRecord.tsx`**

Replace the entire file content with a composed assembly using the new parts:

```tsx
import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import type { ClippedRenderProps } from "../../types";
import type { Palette } from "../../lib/palette";
import { VinylDisc } from "../../vinyl/VinylDisc";
import { VinylSpecular } from "../../vinyl/VinylSpecular";
import { VinylLabel } from "../../vinyl/VinylLabel";
import { VinylReflection } from "../../vinyl/VinylReflection";

export const VinylRecord = ({
  props,
  palette,
  size,
  y = 0,
  labelScale = 0.34,
  revealFrame = 0,
}: {
  props: ClippedRenderProps;
  palette: Palette;
  size: number;
  y?: number;
  labelScale?: number;
  revealFrame?: number;
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const reveal = spring({ frame: frame - revealFrame, fps, config: { damping: 20, stiffness: 85 } });

  return (
    <div
      style={{
        position: "absolute",
        left: "50%",
        top: "50%",
        width: size,
        height: size,
        transform: `translate(-50%, calc(-50% + ${y}px)) scale(${reveal})`,
      }}
    >
      <VinylReflection size={size} y={0} opacity={0.14} />
      <VinylDisc size={size} motion={props.options.motion}>
        <VinylLabel discSize={size} imageSrc={props.assets.coverSrc} labelScale={labelScale} />
      </VinylDisc>
      <VinylSpecular size={size} motion={props.options.motion} />
    </div>
  );
};
```

**Step 6: Verify typecheck**

```bash
cd /Users/rd/Scripts/Riley/clipped/remotion && npm run typecheck 2>&1 | head -20
```

**Step 7: Commit**

```bash
cd /Users/rd/Scripts/Riley/clipped && git add remotion/src/vinyl/ remotion/src/components/vinyl/VinylRecord.tsx && git commit -m "feat(vinyl): decompose VinylRecord into modular components with stationary specular highlight"
```

---

## Phase 4 — Audio-Reactive Visualizers & Particle Primitives

### Task 4.1: SpeakerCone component — physical vibration effect

Create a realistic speaker cone component that reacts dynamically to low frequency (bass) inputs, physically shifting scale and simulating air displacement.

**Files:**
- Create: `remotion/src/audio/SpeakerCone.tsx`

**Step 1: Create `remotion/src/audio/SpeakerCone.tsx`**

```tsx
import { useCurrentFrame } from "remotion";
import type { AudioAnalysis } from "./audio-utils";

/**
 * SpeakerCone — vibrating physical speaker graphic.
 * Concentric speaker layers scale up on heavy bass hits.
 */
export const SpeakerCone = ({
  audio,
  accentColor,
  size = 400,
}: {
  audio: AudioAnalysis;
  accentColor?: string;
  size?: number;
}) => {
  const frame = useCurrentFrame();
  const bass = audio.bass;
  const pulse = 1 + bass * 0.18;

  return (
    <div
      style={{
        width: size,
        height: size,
        position: "relative",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      {/* Outer frame/rim */}
      <div
        style={{
          width: size,
          height: size,
          borderRadius: "50%",
          background: "radial-gradient(circle, #2a2a2a 0%, #151515 80%, #0a0a0a 100%)",
          boxShadow: "0 20px 50px rgba(0,0,0,0.6)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        {/* Vibrating cone */}
        <div
          style={{
            width: size * 0.85,
            height: size * 0.85,
            borderRadius: "50%",
            background: "radial-gradient(circle, #1a1a1a 0%, #111 70%, #050505 100%)",
            transform: `scale(${pulse})`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            boxShadow: accentColor ? `0 0 ${20 + bass * 40}px ${accentColor}22` : undefined,
            transition: "transform 0.05s ease-out",
          }}
        >
          {/* Inner dust cap */}
          <div
            style={{
              position: "absolute",
              width: size * 0.35,
              height: size * 0.35,
              borderRadius: "50%",
              background: "radial-gradient(circle, #333 0%, #1a1a1a 80%, #000 100%)",
              boxShadow: "inset 0 4px 10px rgba(255,255,255,0.1), 0 10px 20px rgba(0,0,0,0.5)",
              transform: `scale(${1 + bass * 0.05})`,
            }}
          />
        </div>
      </div>
    </div>
  );
};
```

### Task 4.2: Visualizer integration

Export all audio-reactive visualizer components through a single index entrypoint under the visualizers directory.

**Files:**
- Create: `remotion/src/visualizers/index.ts`

**Step 1: Create `remotion/src/visualizers/index.ts`**

```ts
export { SpectrumBars, RadialBars, WaveRibbon, Oscilloscope, PulseRings } from "./Spectrum";
export { SpeakerCone } from "../audio/SpeakerCone";
```

---

## Phase 5 — Environment, Atmosphere, & Cinematic PostFX

### Task 5.1: Cinematic Overlays and PostFX Stack

Standardize the creative overlays and post-processing pipeline. The stack handles CRT scanlines, VHS tracking errors (VHSTears), chromatic aberration, Perlin noise overlays, vignette, and beat-flashing lights.

**Files:**
- Create: `remotion/src/effects/index.ts`

**Step 1: Create `remotion/src/effects/index.ts`**

```ts
export {
  Vignette,
  FilmGrain,
  Scanlines,
  LightSweep,
  ReactiveHalo,
  BeatFlash,
  CameraShake,
  PostFxStack,
  VHSTears,
  ChromaticAberration,
  StarField,
  NeonTunnel,
  FilmBurn
} from "./Overlays";
```

---

## Phase 6 — Template Refactoring

Refactor the six core compositions to consume primitives from the newly-created typography, layouts, transitions, materials, audio-reactive, and overlay modules.

### Task 6.1: Refactor `RecordSquare.tsx`

**Files:**
- Modify: `remotion/src/templates/RecordSquare.tsx`

**Refactor Checklist:**
1. Import `useLayout` from `../layouts` and initialize with `"centered"`.
2. Replace local styling calculations with values resolved from `useLayout` (e.g. `layout.artwork`, `layout.visualizer`, `layout.typography`).
3. Replace the local `VinylRecord` rendering with the new decomposed `VinylRecord`.
4. Import and utilize `Captions` with correct text hierarchy and layout safe areas.
5. Use `MetadataStack` or standard text layers rather than ad-hoc inline headers.

---

### Task 6.2: Refactor `GallerySquare.tsx`

**Files:**
- Modify: `remotion/src/templates/GallerySquare.tsx`

**Refactor Checklist:**
1. Initialize `useLayout("centered")`.
2. Extract the artwork card dimensions (`layout.artwork.size`) and wrap the cover image inside the newly defined `ArtworkFrame` with support for `preset="matte"` or `preset="chrome"`.
3. Swap ad-hoc background divs for `ArtworkBackground` using `mode="atmospheric"`.
4. Stagger metadata entry fields using `MetadataStack` driven by the token scale.

---

### Task 6.3: Refactor `PulseReel.tsx`

**Files:**
- Modify: `remotion/src/templates/PulseReel.tsx`

**Refactor Checklist:**
1. Initialize `useLayout` with `"centered"` zone in `vertical` mode (TikTok/Reels aspect).
2. Utilize safe bottom inset (`layout.safe.bottom`) to place visualizers and captions so they are not obscured by the platform's UI chrome.
3. Replace raw subtitle elements with the synchronized lyrics component matching typography scales.

---

### Task 6.4: Refactor `FluidScene.tsx`

**Files:**
- Modify: `remotion/src/templates/FluidScene.tsx`

**Refactor Checklist:**
1. Replace localized particle generators with `StarField` overlay.
2. Bind the central blob size and pulse animations to the resolved layout dimensions (`layout.artwork.size`) and structured audio analysis.
3. Position the bottom-mounted oscilloscope using the coordinates returned by the layout hook (`layout.visualizer`).

---

### Task 6.5: Refactor `PremiumCard.tsx`

**Files:**
- Modify: `remotion/src/templates/PremiumCard.tsx`

**Refactor Checklist:**
1. Use `useLayout("editorial-left")` or `"editorial-right"` for asymmetric layouts.
2. Bind card borders to `ChromeBorder` or `MatteBorder` components.
3. Align captions/titles automatically using typography alignment parameters (`layout.typography.align`).

---

### Task 6.6: Refactor `MetalVHS.tsx`

**Files:**
- Modify: `remotion/src/templates/MetalVHS.tsx`

**Refactor Checklist:**
1. Initialize typography using the `"vhs"` preset (Space Mono font loading).
2. Feed the environment wrapper through `PostFxStack` with VHS/CRT scanlines enabled.
3. Stagger scene elements using the entrance progress builders.

---

## Phase 7 — Verification & Polish

### Task 7.1: Comprehensive build and render validation

Run typechecks, syntax compilation checks, and perform mock runs for all modified templates to confirm that no regression was introduced.

**Step 1: Run complete typecheck**
```bash
cd /Users/rd/Scripts/Riley/clipped/remotion && npm run typecheck
```

**Step 2: Run dry-run render tests for all templates**
Verify that all six compositions compile, register correctly in `Root.tsx`, and can be rendered by the Python coordinator.

```bash
python3 scripts/test-templates.py --dry-run
```
