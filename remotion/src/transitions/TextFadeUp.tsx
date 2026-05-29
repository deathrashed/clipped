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
