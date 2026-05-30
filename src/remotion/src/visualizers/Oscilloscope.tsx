import { useCurrentFrame } from "remotion";
import type { AudioAnalysis, Palette } from "./shared";

export const Oscilloscope = ({
  audio,
  palette,
  width = 880,
  height = 80,
  color,
  strokeWidth = 3,
  glow = true,
}: {
  audio: AudioAnalysis;
  palette: Palette;
  width?: number;
  height?: number;
  color?: string;
  strokeWidth?: number;
  glow?: boolean;
}) => {
  const frame = useCurrentFrame();
  const pointCount = 64;
  const step = width / (pointCount - 1);
  const c = color || palette.accent;
  const d = Array.from({ length: pointCount })
    .map((_, idx) => {
      const sample =
        audio.values[
          Math.floor((idx / pointCount) * audio.values.length)
        ] || 0;
      const x = idx * step;
      const y =
        height / 2 +
        Math.sin(idx * 0.4 + frame / 12) * 6 +
        (sample - 0.5) * height * 0.84;
      return `${idx === 0 ? "M" : "L"} ${x.toFixed(1)} ${y.toFixed(1)}`;
    })
    .join(" ");

  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
      {glow && (
        <path
          d={d}
          fill="none"
          stroke={c}
          strokeWidth={strokeWidth + 8}
          strokeLinecap="round"
          strokeLinejoin="round"
          opacity={0.18}
          filter="blur(6px)"
        />
      )}
      <path
        d={d}
        fill="none"
        stroke={c}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        strokeLinejoin="round"
        opacity={0.88}
      />
    </svg>
  );
};
