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
