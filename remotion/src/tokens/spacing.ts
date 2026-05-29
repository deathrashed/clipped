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
