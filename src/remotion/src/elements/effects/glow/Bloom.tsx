import type { CSSProperties } from "react";

type BloomProps = {
  intensity?: number;
  color?: string;
  radius?: number;
  opacity?: number;
};

export const Bloom = ({
  intensity = 0.3,
  color = "#ffffff",
  radius = 60,
  opacity = 1,
}: BloomProps) => {
  const style: CSSProperties = {
    position: "absolute",
    inset: 0,
    pointerEvents: "none",
    background: `radial-gradient(circle at 50% 50%, ${color} 0%, transparent ${radius}%)`,
    opacity: intensity * opacity,
    mixBlendMode: "screen",
  };
  return <div style={style} />;
};
