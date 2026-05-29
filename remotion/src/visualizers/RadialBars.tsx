import { useCurrentFrame } from "remotion";
import type { AudioAnalysis, Palette } from "./shared";

export const RadialBars = ({
  audio,
  palette,
  size = 760,
  innerRadius = 260,
  count = 96,
  mode = "ring",
}: {
  audio: AudioAnalysis;
  palette: Palette;
  size?: number;
  innerRadius?: number;
  count?: number;
  mode?: "ring" | "flower";
}) => {
  const frame = useCurrentFrame();
  const radius = size / 2;
  const values = audio.values.slice(0, count);

  return (
    <div style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        {values.map((value, idx) => {
          const angle = (idx / values.length) * 360 + frame * 0.018;
          const barHeight =
            mode === "flower" ? 36 + value * 150 : 18 + value * 86;
          const lineWidth = mode === "flower" ? 5 : 4;
          return (
            <rect
              key={idx}
              x={radius - lineWidth / 2}
              y={radius - innerRadius - barHeight}
              width={lineWidth}
              height={barHeight}
              rx={999}
              fill={idx % 8 === 0 ? palette.accent2 : palette.accent}
              opacity={0.34 + value * 0.56}
              transform={`rotate(${angle} ${radius} ${radius})`}
            />
          );
        })}
      </svg>
    </div>
  );
};
