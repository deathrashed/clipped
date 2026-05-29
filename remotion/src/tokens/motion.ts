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
