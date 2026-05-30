import { useCurrentFrame } from "remotion";
import { motionFactor } from "../tokens/motion";

/**
 * VinylDisc — rotating disc base with groove rings.
 * No glow. No accent color. Pure material.
 */
export const VinylDisc = ({
  size,
  motion = "medium",
  children,
}: {
  size: number;
  motion?: string;
  children?: React.ReactNode;
}) => {
  const frame = useCurrentFrame();
  const mf = motionFactor(motion);
  // 33.3 RPM → 200°/s → at 30fps: 200/30 ≈ 6.67°/frame
  const rotation = frame * (200 / 30) * mf;

  const grooveCount = 40;

  return (
    <div
      style={{
        width: size,
        height: size,
        borderRadius: "50%",
        transform: `rotate(${rotation}deg)`,
        background: "radial-gradient(circle at center, #080808 0%, #131313 30%, #060606 55%, #181818 72%, #030303 100%)",
        // Cinematic shadow — no colored accent glow
        boxShadow: "0 60px 90px rgba(0,0,0,0.88), 0 0 0 1px rgba(255,255,255,0.04)",
        overflow: "hidden",
        position: "relative",
      }}
    >
      {/* Groove rings */}
      {Array.from({ length: grooveCount }).map((_, i) => {
        const inset = 16 + i * (size / 120);
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              inset,
              borderRadius: "50%",
              border: "1px solid rgba(255,255,255,0.04)",
            }}
          />
        );
      })}
      {children}
    </div>
  );
};
