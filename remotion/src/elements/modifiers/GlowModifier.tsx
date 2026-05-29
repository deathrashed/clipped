import type { CSSProperties, ReactNode } from "react";

type GlowModifierProps = {
  children: ReactNode;
  intensity?: number;
  radius?: number;
  color?: string;
  enabled?: boolean;
};

export const GlowModifier = ({
  children,
  intensity = 0.3,
  radius = 20,
  color = "#FFFFFF",
  enabled = true,
}: GlowModifierProps) => {
  if (!enabled) return <>{children}</>;

  const style: CSSProperties = {
    filter: `drop-shadow(0 0 ${radius * intensity}px ${color}) drop-shadow(0 0 ${radius * intensity * 0.5}px ${color})`,
  };

  return <div style={style}>{children}</div>;
};
