import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";

export type FogLayerProps = {
  opacity?: number;
  density?: number;
  color?: string;
  drift?: number;
};

export const FogLayer: React.FC<FogLayerProps> = ({
  opacity = 0.12,
  density = 1.0,
  color = "rgba(230, 230, 240, 0.4)",
  drift = 0.5,
}) => {
  const frame = useCurrentFrame();
  const offset1 = Math.sin(frame * 0.005 * drift) * 15;
  const offset2 = Math.cos(frame * 0.007 * drift) * 20;

  return (
    <AbsoluteFill style={{ pointerEvents: "none", opacity, mixBlendMode: "screen", zIndex: 82 }}>
      <div
        style={{
          position: "absolute",
          bottom: "-20%",
          left: `${-20 + offset1}%`,
          right: `${-20 - offset1}%`,
          height: `${70 * density}%`,
          background: `radial-gradient(ellipse at bottom, ${color} 0%, transparent 70%)`,
          filter: "blur(20px)",
        }}
      />
      <div
        style={{
          position: "absolute",
          top: "-30%",
          right: `${-30 + offset2}%`,
          left: `${-30 - offset2}%`,
          height: `${80 * density}%`,
          background: `radial-gradient(ellipse at top right, ${color} 0%, transparent 65%)`,
          filter: "blur(30px)",
        }}
      />
    </AbsoluteFill>
  );
};
