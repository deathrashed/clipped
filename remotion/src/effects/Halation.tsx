import React from "react";

export type HalationProps = {
  opacity?: number;
  blur?: number;
  warmth?: number;
  intensity?: number;
  children?: React.ReactNode;
};

export const Halation: React.FC<HalationProps> = ({
  opacity = 0.35,
  blur = 8,
  warmth = 0.18,
  intensity = 1.0,
  children,
}) => {
  if (!children) {
    // Overlay layer mode
    return (
      <div
        style={{
          position: "absolute",
          inset: 0,
          pointerEvents: "none",
          backgroundColor: `rgba(255, 110, 40, ${opacity * 0.15 * warmth * intensity})`,
          filter: `blur(${blur}px)`,
          mixBlendMode: "screen",
        }}
      />
    );
  }

  // Wrapper mode: applies a warm filmic highlight bleed using CSS drop-shadow.
  return (
    <div
      style={{
        display: "contents",
        filter: `drop-shadow(0 0 ${blur}px rgba(255, 110, 40, ${opacity * warmth * intensity}))`,
      }}
    >
      {children}
    </div>
  );
};
