import type { CSSProperties, ReactNode } from "react";

type PixelateModifierProps = {
  children: ReactNode;
  size?: number;
  enabled?: boolean;
};

export const PixelateModifier = ({
  children,
  size = 8,
  enabled = true,
}: PixelateModifierProps) => {
  if (!enabled) return <>{children}</>;

  const style: CSSProperties = {
    filter: `blur(${size * 0.4}px)`,
    imageRendering: "pixelated",
  };

  const overlay: CSSProperties = {
    position: "absolute",
    inset: 0,
    pointerEvents: "none",
    backgroundImage: [
      `repeating-linear-gradient(90deg, transparent 0px, transparent ${size - 0.5}px, rgba(0,0,0,0.04) ${size - 0.5}px, rgba(0,0,0,0.04) ${size}px)`,
      `repeating-linear-gradient(0deg, transparent 0px, transparent ${size - 0.5}px, rgba(0,0,0,0.04) ${size - 0.5}px, rgba(0,0,0,0.04) ${size}px)`,
    ].join(", "),
    backgroundSize: `${size}px ${size}px`,
  };

  return (
    <div style={{ position: "relative" }}>
      <div style={style}>{children}</div>
      <div style={overlay} />
    </div>
  );
};
