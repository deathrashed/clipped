import type { CSSProperties } from "react";
import { useCurrentFrame } from "remotion";
import type { AudioAnalysis } from "../audio/audio-utils";
import type { Palette } from "../lib/palette";

export const SpectrumBars = ({
  audio,
  palette,
  count = 48,
  width = 860,
  height = 130,
  color,
  mirror = false,
}: {
  audio: AudioAnalysis;
  palette: Palette;
  count?: number;
  width?: number;
  height?: number;
  color?: CSSProperties["color"];
  mirror?: boolean;
}) => {
  const values = audio.values.slice(0, count);
  const bars = mirror ? [...values.slice(1).reverse(), ...values] : values;
  return (
    <div
      style={{
        width,
        height,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        gap: Math.max(3, width / Math.max(1, bars.length) * 0.16),
      }}
    >
      {bars.map((value, idx) => (
        <div
          key={idx}
          style={{
            flex: 1,
            height: 10 + value * (height - 10),
            borderRadius: 999,
            background: idx % 7 === 0 ? palette.accent2 : color || palette.accent,
            opacity: 0.48 + value * 0.46,
            boxShadow: `0 0 ${8 + value * 24}px ${palette.accent}66`,
          }}
        />
      ))}
    </div>
  );
};

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
          const barHeight = mode === "flower" ? 36 + value * 150 : 18 + value * 86;
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
            const value = audio.values[(idx * 3 + line * 7) % audio.values.length] || 0;
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
            filter="drop-shadow(0 0 14px rgba(255,255,255,0.22))"
          />
        );
      })}
    </svg>
  );
};

/** Oscilloscope — smooth single-line waveform trace across the width */
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
      const sample = audio.values[Math.floor((idx / pointCount) * audio.values.length)] || 0;
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

/** PulseRings — audio-reactive concentric expanding circles centered on an element */
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
      style={{ position: "absolute", left: "50%", top: "50%", transform: "translate(-50%,-50%)" }}
    >
      {Array.from({ length: ringCount }).map((_, i) => {
        const phase = (frame / 24 + i * (1 / ringCount)) % 1;
        const r = (size * 0.22) + phase * size * 0.36;
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
