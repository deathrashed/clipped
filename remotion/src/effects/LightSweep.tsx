import { useCurrentFrame, useVideoConfig, interpolate } from "remotion";
import type { Palette } from "../lib/palette";

export const LightSweep = ({
  palette,
  opacity = 0.28,
  angle = 17,
}: {
  palette: Palette;
  opacity?: number;
  angle?: number;
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const progress = (frame % Math.max(90, durationInFrames * 0.8)) / Math.max(90, durationInFrames * 0.8);
  const left = interpolate(progress, [0, 1], [-35, 135]);
  return (
    <div
      style={{
        position: "absolute",
        top: "-20%",
        bottom: "-20%",
        left: `${left}%`,
        width: "18%",
        opacity,
        transform: `rotate(${angle}deg)`,
        background: `linear-gradient(90deg, transparent, ${palette.border}, ${palette.accent}66, transparent)`,
        filter: "blur(10px)",
        mixBlendMode: "screen",
        pointerEvents: "none",
      }}
    />
  );
};
