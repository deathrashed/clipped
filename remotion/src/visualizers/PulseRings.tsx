import { useCurrentFrame } from "remotion";
import type { AudioAnalysis, Palette } from "./shared";

export const PulseRings = ({
  audio,
  palette,
  size = 600,
  ringCount = 4,
  color,
}: {
  audio: AudioAnalysis;
  palette: Palette;
  size?: number;
  ringCount?: number;
  color?: string;
}) => {
  const frame = useCurrentFrame();
  const cx = size / 2;
  const cy = size / 2;
  const c = color || palette.accent;

  return (
    <svg
      width={size}
      height={size}
      viewBox={`0 0 ${size} ${size}`}
      style={{
        position: "absolute",
        left: "50%",
        top: "50%",
        transform: "translate(-50%,-50%)",
      }}
    >
      {Array.from({ length: ringCount }).map((_, i) => {
        const phase = (frame / 24 + i * (1 / ringCount)) % 1;
        const r = size * 0.22 + phase * size * 0.36;
        const opacity = (1 - phase) * (0.32 + audio.bass * 0.4);
        const strokeW = 2 + audio.bass * 4;
        return (
          <circle
            key={i}
            cx={cx}
            cy={cy}
            r={r}
            fill="none"
            stroke={i % 2 === 0 ? c : palette.accent2}
            strokeWidth={strokeW}
            opacity={opacity}
          />
        );
      })}
    </svg>
  );
};
