import type { CSSProperties } from "react";
import type { AudioAnalysis, Palette } from "./shared";

export const SpectrumBars = ({
  audio,
  palette,
  count = 48,
  width = 860,
  height = 130,
  color,
  mirror = false,
  glow = false,
}: {
  audio: AudioAnalysis;
  palette: Palette;
  count?: number;
  width?: number;
  height?: number;
  color?: CSSProperties["color"];
  mirror?: boolean;
  glow?: boolean;
}) => {
  const values = audio.values.slice(0, count);
  const bars = mirror ? [...values.slice(1).reverse(), ...values] : values;
  const accentColor = color || palette.accent;

  return (
    <div
      style={{
        width,
        height,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        gap: Math.max(3, (width / Math.max(1, bars.length)) * 0.16),
      }}
    >
      {bars.map((value, idx) => (
        <div
          key={idx}
          style={{
            flex: 1,
            height: 10 + value * (height - 10),
            borderRadius: 999,
            background: idx % 7 === 0 ? palette.accent2 : accentColor,
            opacity: 0.48 + value * 0.46,
            boxShadow: glow
              ? `0 0 ${4 + value * 12}px ${accentColor}44`
              : undefined,
          }}
        />
      ))}
    </div>
  );
};
