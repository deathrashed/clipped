import type { CSSProperties } from "react";
import type { AudioAnalysis } from "../../audio/audio-utils";
import type { Palette } from "../../lib/palette";

type FerroFluidProps = {
  audio: AudioAnalysis;
  palette: Palette;
  intensity?: number;
  width?: number;
  height?: number;
};

export const FerroFluid = ({
  audio,
  palette,
  intensity = 0.5,
  width = 860,
  height = 96,
}: FerroFluidProps) => {
  const vals = audio.values;
  const centerX = width / 2;
  const centerY = height / 2;
  const baseRadius = Math.min(width, height) * 0.35;
  const maxDrift = Math.min(width, height) * 0.25;

  const bandCount = 5;
  const bandsPerBlob = Math.max(1, Math.floor(vals.length / bandCount));
  const blobColors = [palette.accent, palette.accent2, "#6bcbff", "#a66cff", "#51cf66"];

  const blobs = Array.from({ length: bandCount }, (_, i) => {
    const start = i * bandsPerBlob;
    const end = Math.min(start + bandsPerBlob, vals.length);
    const slice = vals.slice(start, end);
    const energy = slice.length ? slice.reduce((a: number, b: number) => a + b, 0) / slice.length : 0;

    const angle = (i / bandCount) * Math.PI * 2 + energy * 0.8;
    const radius = baseRadius * (0.35 + energy * 0.65) * intensity;
    const dx = Math.cos(angle + energy * 0.5) * maxDrift * energy;
    const dy = Math.sin(angle * 0.7 + energy * 1.2) * maxDrift * energy * 0.6;

    const rx = radius * (0.8 + energy * 0.4);
    const ry = radius * (0.5 + energy * 0.5) * (0.8 + Math.sin(energy * 3 + i) * 0.2);

    return {
      cx: centerX + dx,
      cy: centerY + dy,
      rx: Math.max(2, rx),
      ry: Math.max(2, ry),
      fill: blobColors[i % blobColors.length],
      opacity: 0.25 + energy * 0.35,
    };
  });

  return (
    <svg width={width} height={height} style={{ position: "absolute", inset: 0 } as CSSProperties}>
      <defs>
        <filter id="ferro-blur">
          <feGaussianBlur in="SourceGraphic" stdDeviation="3" />
        </filter>
      </defs>
      {blobs.map((blob, i) => (
        <ellipse
          key={i}
          cx={blob.cx}
          cy={blob.cy}
          rx={blob.rx}
          ry={blob.ry}
          fill={blob.fill}
          opacity={blob.opacity}
          filter="url(#ferro-blur)"
        />
      ))}
    </svg>
  );
};
