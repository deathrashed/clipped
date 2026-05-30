import { useCurrentFrame } from "remotion";
import type { CSSProperties } from "react";

type StrobeProps = {
  intensity?: number;
  opacity?: number;
};

export const Strobe = ({ intensity = 0.5, opacity = 1 }: StrobeProps) => {
  const frame = useCurrentFrame();
  const interval = Math.max(2, Math.round((1 - intensity) * 10 + 2));
  const isOn = frame % interval < Math.max(1, Math.round(interval * 0.25));

  if (!isOn) return null;

  const style: CSSProperties = {
    position: "absolute",
    inset: 0,
    backgroundColor: intensity > 0.7 ? "#ffffff" : "#f0f0f0",
    opacity: 0.08 * intensity * opacity,
    pointerEvents: "none",
  };

  return <div style={style} />;
};
