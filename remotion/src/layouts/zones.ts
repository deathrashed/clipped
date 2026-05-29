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
