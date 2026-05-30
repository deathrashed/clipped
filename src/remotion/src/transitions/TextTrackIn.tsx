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
