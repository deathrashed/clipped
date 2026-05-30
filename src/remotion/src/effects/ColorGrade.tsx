import React from "react";
import { AbsoluteFill } from "remotion";

export type ColorGradePreset =
  | "neutral"
  | "cinematic"
  | "cold"
  | "warm"
  | "vhs"
  | "black-metal"
  | "boom-bap"
  | "luxury-vinyl";

export type ColorGradeProps = {
  preset?: ColorGradePreset;
  opacity?: number;
  children?: React.ReactNode;
};

export const ColorGrade: React.FC<ColorGradeProps> = ({
  preset = "neutral",
  opacity = 1.0,
  children,
}) => {
  // Define CSS filters for each preset
  const filters: Record<ColorGradePreset, string> = {
    neutral: "none",
    cinematic: "contrast(1.08) saturate(0.92) brightness(0.98)",
    cold: "contrast(1.02) saturate(0.85) hue-rotate(5deg)",
    warm: "contrast(1.02) saturate(1.05) sepia(0.12)",
    vhs: "contrast(0.95) saturate(1.22) brightness(1.02)",
    "black-metal": "contrast(1.45) saturate(0.08) brightness(0.9)",
    "boom-bap": "contrast(1.12) sepia(0.22) saturate(0.95) brightness(0.95)",
    "luxury-vinyl": "contrast(1.15) saturate(1.02) brightness(0.88)",
  };

  // Color overlays (tints) to mix in using blend modes
  const overlays: Record<ColorGradePreset, { background: string; mixBlendMode: React.CSSProperties["mixBlendMode"]; opacity: number } | null> = {
    neutral: null,
    cinematic: {
      background: "linear-gradient(to bottom, rgba(255, 140, 0, 0.04), rgba(0, 80, 255, 0.06))",
      mixBlendMode: "color-burn",
      opacity: 0.8,
    },
    cold: {
      background: "rgba(0, 100, 255, 0.08)",
      mixBlendMode: "color-dodge",
      opacity: 0.6,
    },
    warm: {
      background: "rgba(230, 150, 40, 0.06)",
      mixBlendMode: "color-burn",
      opacity: 0.7,
    },
    vhs: {
      background: "linear-gradient(rgba(255,0,0,0.03), rgba(0,255,0,0.02), rgba(0,0,255,0.03))",
      mixBlendMode: "screen",
      opacity: 0.9,
    },
    "black-metal": {
      background: "rgba(10, 10, 15, 0.15)",
      mixBlendMode: "multiply",
      opacity: 0.8,
    },
    "boom-bap": {
      background: "rgba(120, 90, 50, 0.08)",
      mixBlendMode: "color-burn",
      opacity: 0.7,
    },
    "luxury-vinyl": {
      background: "radial-gradient(circle, rgba(255, 215, 0, 0.05) 0%, rgba(20, 10, 0, 0.15) 100%)",
      mixBlendMode: "hard-light",
      opacity: 0.8,
    },
  };

  const activeFilter = filters[preset] || "none";
  const activeOverlay = overlays[preset];

  const content = (
    <>
      {children}
      {activeOverlay ? (
        <AbsoluteFill
          style={{
            pointerEvents: "none",
            background: activeOverlay.background,
            mixBlendMode: activeOverlay.mixBlendMode,
            opacity: activeOverlay.opacity * opacity,
            zIndex: 99,
          }}
        />
      ) : null}
    </>
  );

  if (!children) {
    // Just overlay mode
    return activeOverlay ? (
      <AbsoluteFill
        style={{
          pointerEvents: "none",
          background: activeOverlay.background,
          mixBlendMode: activeOverlay.mixBlendMode,
          opacity: activeOverlay.opacity * opacity,
          backdropFilter: activeFilter !== "none" ? activeFilter : undefined,
          zIndex: 99,
        }}
      />
    ) : null;
  }

  return (
    <div style={{ display: "contents", filter: activeFilter !== "none" ? activeFilter : undefined }}>
      {content}
    </div>
  );
};
