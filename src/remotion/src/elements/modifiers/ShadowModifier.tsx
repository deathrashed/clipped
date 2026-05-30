import type { CSSProperties, ReactNode } from "react";

type ShadowModifierProps = {
  children: ReactNode;
  x?: number;
  y?: number;
  blur?: number;
  color?: string;
  opacity?: number;
  enabled?: boolean;
};

export const ShadowModifier = ({
  children,
  x = 4,
  y = 4,
  blur = 10,
  color = "#000000",
  opacity = 0.3,
  enabled = true,
}: ShadowModifierProps) => {
  if (!enabled) return <>{children}</>;

  const alpha = Math.round(opacity * 255).toString(16).padStart(2, "0");
  const style: CSSProperties = {
    filter: `drop-shadow(${x}px ${y}px ${blur}px ${color}${alpha})`,
  };

  return <div style={style}>{children}</div>;
};
