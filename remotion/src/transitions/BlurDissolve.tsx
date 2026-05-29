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
