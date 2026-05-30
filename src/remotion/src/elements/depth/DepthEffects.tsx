import type { CSSProperties } from "react";

type DepthFogProps = {
  intensity?: number;
  color?: string;
};

export const DepthFog = ({
  intensity = 0.3,
  color = "#000",
}: DepthFogProps) => {
  const style: CSSProperties = {
    position: "absolute",
    inset: 0,
    pointerEvents: "none",
    background: `linear-gradient(0deg, ${color} 0%, transparent ${intensity * 60}%)`,
    opacity: intensity * 0.5,
  };
  return <div style={style} />;
};

type DepthBlurProps = {
  intensity?: number;
};

export const DepthBlur = ({ intensity = 0.3 }: DepthBlurProps) => {
  const px = intensity * 12;
  const style: CSSProperties = {
    position: "absolute",
    inset: 0,
    pointerEvents: "none",
    backdropFilter: `blur(${px}px)`,
    maskImage: `linear-gradient(0deg, rgba(0,0,0,0.8) 0%, transparent ${100 - intensity * 40}%)`,
    WebkitMaskImage: `linear-gradient(0deg, rgba(0,0,0,0.8) 0%, transparent ${100 - intensity * 40}%)`,
  };
  return <div style={style} />;
};
