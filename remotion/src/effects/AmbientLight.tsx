import React from "react";
import { AbsoluteFill } from "remotion";

export type AmbientLightProps = {
  color?: string;
  opacity?: number;
  blendMode?: React.CSSProperties["mixBlendMode"];
};

export const AmbientLight: React.FC<AmbientLightProps> = ({
  color = "rgba(255, 180, 100, 0.15)",
  opacity = 0.4,
  blendMode = "screen",
}) => {
  return (
    <AbsoluteFill
      style={{
        pointerEvents: "none",
        background: `radial-gradient(circle at 30% 20%, ${color} 0%, transparent 80%)`,
        opacity,
        mixBlendMode: blendMode,
        zIndex: 90,
      }}
    />
  );
};
