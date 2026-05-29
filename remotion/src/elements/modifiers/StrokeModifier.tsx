import type { CSSProperties, ReactNode } from "react";

type StrokeModifierProps = {
  children: ReactNode;
  width?: number;
  color?: string;
  opacity?: number;
  enabled?: boolean;
};

export const StrokeModifier = ({
  children,
  width = 2,
  color = "#FFFFFF",
  opacity = 1,
  enabled = true,
}: StrokeModifierProps) => {
  if (!enabled) return <>{children}</>;

  const style: CSSProperties = {
    WebkitTextStroke: `${width}px ${color}`,
    paintOrder: "stroke fill",
    opacity,
  };

  return <div style={style}>{children}</div>;
};
