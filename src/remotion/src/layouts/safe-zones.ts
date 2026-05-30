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
