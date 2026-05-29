// Typography tokens for Clipped.
// Sizes are expressed as fractions of min(width, height) — scale in components.
// Fonts loaded via @remotion/google-fonts in typography/fonts.ts.

export type TypographyPreset =
  | "cinematic"
  | "editorial"
  | "brutal"
  | "minimal"
  | "compact"
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
    trackTitle:  { sizeFactor: 0.058, weight: 700, tracking: -0.02, transform: "none",      fontFamily: "display" },
    artistName:  { sizeFactor: 0.030, weight: 400, tracking:  0.10, transform: "uppercase", fontFamily: "body" },
    metaLine:    { sizeFactor: 0.020, weight: 400, tracking:  0.14, transform: "uppercase", fontFamily: "body" },
    lyricLine:   { sizeFactor: 0.042, weight: 600, tracking:  0,    transform: "none",      fontFamily: "body", lineHeight: 1.25 },
    lowerThird:  { sizeFactor: 0.020, weight: 500, tracking:  0.06, transform: "uppercase", fontFamily: "body" },
  },
  editorial: {
    trackTitle:  { sizeFactor: 0.064, weight: 700, tracking: -0.03, transform: "none",      fontFamily: "display" },
    artistName:  { sizeFactor: 0.028, weight: 400, tracking:  0.12, transform: "uppercase", fontFamily: "body" },
    metaLine:    { sizeFactor: 0.018, weight: 400, tracking:  0.16, transform: "uppercase", fontFamily: "body" },
    lyricLine:   { sizeFactor: 0.040, weight: 600, tracking:  0,    transform: "none",      fontFamily: "body", lineHeight: 1.3 },
    lowerThird:  { sizeFactor: 0.018, weight: 500, tracking:  0.08, transform: "uppercase", fontFamily: "body" },
  },
  brutal: {
    trackTitle:  { sizeFactor: 0.068, weight: 900, tracking: -0.01, transform: "uppercase", fontFamily: "display" },
    artistName:  { sizeFactor: 0.032, weight: 700, tracking:  0.06, transform: "uppercase", fontFamily: "display" },
    metaLine:    { sizeFactor: 0.020, weight: 700, tracking:  0.10, transform: "uppercase", fontFamily: "body" },
    lyricLine:   { sizeFactor: 0.048, weight: 900, tracking:  0,    transform: "uppercase", fontFamily: "display", lineHeight: 1.1 },
    lowerThird:  { sizeFactor: 0.022, weight: 700, tracking:  0.04, transform: "uppercase", fontFamily: "display" },
  },
  minimal: {
    trackTitle:  { sizeFactor: 0.052, weight: 500, tracking:  0,    transform: "none",      fontFamily: "body" },
    artistName:  { sizeFactor: 0.026, weight: 400, tracking:  0.08, transform: "uppercase", fontFamily: "body" },
    metaLine:    { sizeFactor: 0.016, weight: 400, tracking:  0.12, transform: "uppercase", fontFamily: "body" },
    lyricLine:   { sizeFactor: 0.038, weight: 500, tracking:  0,    transform: "none",      fontFamily: "body", lineHeight: 1.35 },
    lowerThird:  { sizeFactor: 0.017, weight: 400, tracking:  0.08, transform: "none",      fontFamily: "body" },
  },
  compact: {
    trackTitle:  { sizeFactor: 0.044, weight: 600, tracking: -0.01, transform: "none",      fontFamily: "body" },
    artistName:  { sizeFactor: 0.022, weight: 400, tracking:  0.10, transform: "uppercase", fontFamily: "body" },
    metaLine:    { sizeFactor: 0.015, weight: 400, tracking:  0.14, transform: "uppercase", fontFamily: "body" },
    lyricLine:   { sizeFactor: 0.036, weight: 600, tracking:  0,    transform: "none",      fontFamily: "body", lineHeight: 1.3 },
    lowerThird:  { sizeFactor: 0.015, weight: 400, tracking:  0.08, transform: "none",      fontFamily: "body" },
  },
  vhs: {
    trackTitle:  { sizeFactor: 0.054, weight: 700, tracking:  0.04, transform: "uppercase", fontFamily: "mono" },
    artistName:  { sizeFactor: 0.026, weight: 400, tracking:  0.10, transform: "uppercase", fontFamily: "mono" },
    metaLine:    { sizeFactor: 0.016, weight: 400, tracking:  0.14, transform: "uppercase", fontFamily: "mono" },
    lyricLine:   { sizeFactor: 0.040, weight: 700, tracking:  0.02, transform: "uppercase", fontFamily: "mono", lineHeight: 1.2 },
    lowerThird:  { sizeFactor: 0.018, weight: 400, tracking:  0.10, transform: "uppercase", fontFamily: "mono" },
  },
  lyric: {
    trackTitle:  { sizeFactor: 0.054, weight: 700, tracking: -0.01, transform: "none",      fontFamily: "display" },
    artistName:  { sizeFactor: 0.028, weight: 400, tracking:  0.08, transform: "uppercase", fontFamily: "body" },
    metaLine:    { sizeFactor: 0.018, weight: 400, tracking:  0.12, transform: "uppercase", fontFamily: "body" },
    lyricLine:   { sizeFactor: 0.046, weight: 700, tracking: -0.01, transform: "none",      fontFamily: "display", lineHeight: 1.28 },
    lowerThird:  { sizeFactor: 0.020, weight: 500, tracking:  0.06, transform: "none",      fontFamily: "body" },
  },
};

export const resolveTypeScale = (preset: TypographyPreset): TypeScale => presets[preset];

/** Resolve font-size in px from a sizeFactor and the viewport min dimension. */
export const typeSize = (sizeFactor: number, minDim: number): number =>
  Math.round(sizeFactor * minDim);
