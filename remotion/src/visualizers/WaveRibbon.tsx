import { useCurrentFrame } from "remotion";
import type { AudioAnalysis, Palette } from "./shared";

export const WaveRibbon = ({
  audio,
  palette,
  width = 880,
  height = 120,
  lines = 3,
}: {
  audio: AudioAnalysis;
  palette: Palette;
  width?: number;
  height?: number;
  lines?: number;
}) => {
  const frame = useCurrentFrame();
  const pointCount = 20;
  const step = width / (pointCount - 1);

  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
      {Array.from({ length: lines }).map((_, line) => {
        const offset = line * 0.15;
        const d = Array.from({ length: pointCount })
          .map((__, idx) => {
            const value =
              audio.values[(idx * 3 + line * 7) % audio.values.length] || 0;
            const x = idx * step;
            const y =
              height / 2 +
              Math.sin(idx * 0.9 + frame / 18 + offset) * (10 + line * 5) +
              (value - 0.5) * height * 0.68;
            return `${idx === 0 ? "M" : "L"} ${x.toFixed(1)} ${y.toFixed(1)}`;
          })
          .join(" ");
        return (
          <path
            key={line}
            d={d}
            fill="none"
            stroke={line === 0 ? palette.accent2 : palette.accent}
            strokeWidth={line === 0 ? 6 : 3}
            strokeLinecap="round"
            strokeLinejoin="round"
            opacity={0.72 - line * 0.16}
            filter="drop-shadow(0 0 14px rgba(255,255,255,0.18))"
          />
        );
      })}
    </svg>
  );
};
