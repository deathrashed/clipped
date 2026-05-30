import { AbsoluteFill } from "remotion";

/**
 * LumaFade — flash to near-white and back.
 * progress 0 = transparent, 0.5 = peak white, 1 = transparent.
 * Use for scene cuts in metal/vhs presets.
 */
export const LumaFade = ({
  progress,
  color = "rgba(255,255,255,0.92)",
  peakOpacity = 0.88,
}: {
  progress: number;
  color?: string;
  peakOpacity?: number;
}) => {
  if (progress <= 0 || progress >= 1) return null;
  // Bell curve: 0 at 0 and 1, max at 0.5
  const peak = 1 - Math.abs(progress - 0.5) * 2;
  const opacity = peak * peakOpacity;

  return (
    <AbsoluteFill
      style={{
        pointerEvents: "none",
        backgroundColor: color,
        opacity,
        mixBlendMode: "screen",
      }}
    />
  );
};
