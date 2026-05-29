import type { CSSProperties, ReactNode } from "react";

type BlurModifierProps = {
  children: ReactNode;
  amount?: number;
  enabled?: boolean;
};

export const BlurModifier = ({
  children,
  amount = 2,
  enabled = true,
}: BlurModifierProps) => {
  if (!enabled) return <>{children}</>;

  const style: CSSProperties = {
    filter: `blur(${amount}px)`,
  };

  return <div style={style}>{children}</div>;
};
