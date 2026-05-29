import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";

/**
 * VinylSleeve — sleeve peek entering from bottom-right behind the record.
 * size: approximately record diameter.
 * y: vertical offset of record center from frame center.
 * progress: 0 = off-screen, 1 = settled peek visible.
 */
export const VinylSleeve = ({
  size,
  y = 0,
  progress = 1,
}: {
  size: number;
  y?: number;
  progress?: number;
}) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();

  const sleeveW = size * 0.92;
  const sleeveH = size * 0.94;
  const peekX = interpolate(progress, [0, 1], [size * 0.5, size * 0.08]);
  const peekY = interpolate(progress, [0, 1], [size * 0.5, size * 0.10]);

  // Slow micro-wobble for life
  const wobble = Math.sin(frame / 90) * 1.5;

  return (
    <div
      style={{
        position: "absolute",
        left: "50%",
        top: "50%",
        width: sleeveW,
        height: sleeveH,
        transform: `translate(calc(-50% + ${peekX + wobble}px), calc(-50% + ${y + peekY}px))`,
        borderRadius: 8,
        background: "linear-gradient(135deg, #1a1a1a 0%, #0d0d0d 60%, #222 100%)",
        boxShadow: "inset -4px -4px 20px rgba(255,255,255,0.04), 0 20px 60px rgba(0,0,0,0.8)",
        zIndex: 1, // behind VinylRecord (z:2)
      }}
    />
  );
};
