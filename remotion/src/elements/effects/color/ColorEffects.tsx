import type { CSSProperties } from "react";

type ColorEffectProps = {
  intensity?: number;
  opacity?: number;
};

export const BrightnessContrast = ({ intensity = 0.5 }: ColorEffectProps) => {
  const v = intensity * 0.5;
  const style: CSSProperties = {
    position: "absolute",
    inset: 0,
    pointerEvents: "none",
    backdropFilter: `brightness(${1 + v}) contrast(${1 + v * 0.3})`,
  };
  return <div style={style} />;
};

export const HueSaturation = ({ intensity = 0.5 }: ColorEffectProps) => {
  const hue = intensity * 360;
  const sat = 1 + (intensity - 0.5) * 0.6;
  const style: CSSProperties = {
    position: "absolute",
    inset: 0,
    pointerEvents: "none",
    backdropFilter: `hue-rotate(${hue}deg) saturate(${sat})`,
  };
  return <div style={style} />;
};

export const FilterEffect = ({ intensity = 0.5 }: ColorEffectProps) => {
  const sepia = intensity * 0.8;
  const blur = intensity * 2;
  const style: CSSProperties = {
    position: "absolute",
    inset: 0,
    pointerEvents: "none",
    backdropFilter: `sepia(${sepia}) blur(${blur}px)`,
  };
  return <div style={style} />;
};

export const ToneMapping = ({ intensity = 0.5 }: ColorEffectProps) => {
  const contrast = 1 + intensity * 0.8;
  const brightness = 1 + intensity * 0.3;
  const style: CSSProperties = {
    position: "absolute",
    inset: 0,
    pointerEvents: "none",
    backdropFilter: `contrast(${contrast}) brightness(${brightness})`,
  };
  return <div style={style} />;
};

export const BlackWhite = ({ intensity = 0.5 }: ColorEffectProps) => {
  const style: CSSProperties = {
    position: "absolute",
    inset: 0,
    pointerEvents: "none",
    backdropFilter: `grayscale(${intensity})`,
  };
  return <div style={style} />;
};

export const Inversion = ({ intensity = 0.5 }: ColorEffectProps) => {
  const style: CSSProperties = {
    position: "absolute",
    inset: 0,
    pointerEvents: "none",
    backdropFilter: `invert(${intensity * 0.8})`,
  };
  return <div style={style} />;
};
