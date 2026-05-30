import { useCurrentFrame } from "remotion";
import { motionFactor } from "../tokens/motion";

/**
 * VinylSpecular — world-space fixed specular highlight.
 * Represents reflections from a stationary light source.
 * The highlight remains fixed in world space (0 degrees rotation)
 * while the vinyl disc grooves rotate underneath.
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
  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        width: size,
        height: size,
        borderRadius: "50%",
        background: "conic-gradient(from 30deg, rgba(255,255,255,0.18), transparent 20%, rgba(255,255,255,0.08) 30%, transparent 52%, rgba(255,255,255,0.14), transparent 76%)",
        mixBlendMode: "screen",
        opacity,
        pointerEvents: "none",
      }}
    />
  );
};
