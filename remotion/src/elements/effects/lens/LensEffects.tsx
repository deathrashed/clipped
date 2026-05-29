import type { CSSProperties } from "react";

type LensEffectProps = {
  intensity?: number;
  opacity?: number;
};

export const Vignette = ({ intensity = 0.5, opacity = 1 }: LensEffectProps) => {
  const style: CSSProperties = {
    position: "absolute",
    inset: 0,
    pointerEvents: "none",
    background: `radial-gradient(ellipse at center, transparent ${50 - (intensity * 20)}%, rgba(0,0,0,${intensity * 0.7 * opacity}) 100%)`,
  };
  return <div style={style} />;
};

export const ChromaticAberration = ({
  intensity = 0.5,
  opacity = 1,
}: LensEffectProps) => {
  const offset = intensity * 3;
  const style: CSSProperties = {
    position: "absolute",
    inset: 0,
    pointerEvents: "none",
    opacity,
    textShadow: `${offset}px 0 rgba(255,0,0,${intensity * 0.4}), ${-offset}px 0 rgba(0,255,255,${intensity * 0.4})`,
  };
  return <div style={style} />;
};

export const Fisheye = ({ intensity = 0.5 }: LensEffectProps) => {
  const radius = 50 + intensity * 30;
  const style: CSSProperties = {
    position: "absolute",
    inset: 0,
    pointerEvents: "none",
    background: `radial-gradient(ellipse at center, transparent ${radius - 10}%, rgba(0,0,0,${(1 - intensity) * 0.3}) ${radius}%, rgba(0,0,0,0.5) 100%)`,
  };
  return <div style={style} />;
};
