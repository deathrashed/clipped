import type { CSSProperties } from "react";

type TextureEffectProps = {
  intensity?: number;
  opacity?: number;
};

export const Noise = ({ intensity = 0.5, opacity = 1 }: TextureEffectProps) => {
  const style: CSSProperties = {
    position: "absolute",
    inset: 0,
    pointerEvents: "none",
    opacity: intensity * opacity * 0.08,
    backgroundImage:
      "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\")",
    backgroundRepeat: "repeat",
    backgroundSize: "256px 256px",
  };
  return <div style={style} />;
};

export const Scanline = ({ intensity = 0.5, opacity = 1 }: TextureEffectProps) => {
  const style: CSSProperties = {
    position: "absolute",
    inset: 0,
    pointerEvents: "none",
    opacity: intensity * opacity * 0.15,
    backgroundImage:
      "repeating-linear-gradient(0deg, transparent, transparent 1px, rgba(0,0,0,0.3) 1px, rgba(0,0,0,0.3) 2px)",
    backgroundSize: "100% 2px",
  };
  return <div style={style} />;
};

export const VHS = ({ intensity = 0.5, opacity = 1 }: TextureEffectProps) => {
  const style: CSSProperties = {
    position: "absolute",
    inset: 0,
    pointerEvents: "none",
    opacity: intensity * opacity * 0.12,
    backgroundImage:
      "repeating-linear-gradient(0deg, transparent 0px, transparent 3px, rgba(0,0,0,0.15) 3px, rgba(0,0,0,0.15) 5px, transparent 5px, transparent 8px)",
    backgroundSize: "100% 8px",
  };
  return <div style={style} />;
};

export const Pixelation = ({ intensity = 0.5, opacity = 1 }: TextureEffectProps) => {
  const blockSize = Math.max(3, Math.round((1 - intensity) * 20 + 3));
  const style: CSSProperties = {
    position: "absolute",
    inset: 0,
    pointerEvents: "none",
    opacity,
    backdropFilter: `blur(${blockSize * 0.5}px)`,
    backgroundImage: [
      `repeating-linear-gradient(90deg, transparent 0px, transparent ${blockSize - 0.5}px, rgba(0,0,0,0.05) ${blockSize - 0.5}px, rgba(0,0,0,0.05) ${blockSize}px)`,
      `repeating-linear-gradient(0deg, transparent 0px, transparent ${blockSize - 0.5}px, rgba(0,0,0,0.05) ${blockSize - 0.5}px, rgba(0,0,0,0.05) ${blockSize}px)`,
    ].join(", "),
    backgroundSize: `${blockSize}px ${blockSize}px`,
  };
  return <div style={style} />;
};
