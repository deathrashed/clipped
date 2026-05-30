import type { CSSProperties, ReactNode } from "react";

type AdjustModifierProps = {
  children: ReactNode;
  brightness?: number;
  contrast?: number;
  saturation?: number;
  hue?: number;
  enabled?: boolean;
};

export const AdjustModifier = ({
  children,
  brightness = 0,
  contrast = 0,
  saturation = 0,
  hue = 0,
  enabled = true,
}: AdjustModifierProps) => {
  if (!enabled) return <>{children}</>;

  const b = 1 + brightness;
  const c = 1 + contrast;
  const s = 1 + saturation;

  const style: CSSProperties = {
    filter: `brightness(${b}) contrast(${c}) saturate(${s}) hue-rotate(${hue}deg)`,
  };

  return <div style={style}>{children}</div>;
};
