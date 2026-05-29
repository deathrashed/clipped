import type { CSSProperties, ReactNode } from "react";

type DitherModifierProps = {
  children: ReactNode;
  amount?: number;
  pattern?: "bayer" | "random" | "blue-noise";
  colors?: number;
  enabled?: boolean;
};

export const DitherModifier = ({
  children,
  amount = 0.5,
  pattern = "bayer",
  colors = 16,
  enabled = true,
}: DitherModifierProps) => {
  if (!enabled) return <>{children}</>;

  const noiseOpacity = amount * 0.06;
  const style: CSSProperties = {
    position: "relative",
    imageRendering: pattern === "bayer" ? "crisp-edges" : "auto",
  };

  const ditherStyle: CSSProperties = {
    position: "absolute",
    inset: 0,
    pointerEvents: "none",
    opacity: noiseOpacity,
    backgroundImage:
      "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 4 4' xmlns='http://www.w3.org/2000/svg'%3E%3Crect width='1' height='1' fill='%23000' opacity='0.5'/%3E%3C/svg%3E\")",
    backgroundRepeat: "repeat",
    backgroundSize: `${Math.max(2, 24 - colors * 0.3)}px ${Math.max(2, 24 - colors * 0.3)}px`,
    mixBlendMode: "multiply",
  };

  return (
    <div style={style}>
      {children}
      <div style={ditherStyle} />
    </div>
  );
};
