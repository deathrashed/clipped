import { useCurrentFrame } from "remotion";
import type { CSSProperties, ReactNode } from "react";

type WobbleModifierProps = {
  children: ReactNode;
  amplitude?: number;
  speed?: number;
  enabled?: boolean;
};

export const WobbleModifier = ({
  children,
  amplitude = 2,
  speed = 3,
  enabled = true,
}: WobbleModifierProps) => {
  const frame = useCurrentFrame();

  if (!enabled) return <>{children}</>;

  const t = frame * speed * 0.05;
  const dx = Math.sin(t) * amplitude;
  const dy = Math.cos(t * 1.3) * amplitude * 0.7;
  const skew = Math.sin(t * 0.7) * amplitude * 0.15;

  const style: CSSProperties = {
    transform: `translate(${dx}px, ${dy}px) skew(${skew}deg)`,
    transition: "none",
  };

  return (
    <div style={{ position: "relative" }}>
      <div style={style}>{children}</div>
      <div
        style={{
          position: "absolute",
          inset: 0,
          pointerEvents: "none",
          opacity: 0.03,
          backgroundImage:
            "repeating-linear-gradient(0deg, transparent 0px, transparent 1px, rgba(0,0,255,0.06) 1px, rgba(0,0,255,0.06) 2px)",
          backgroundSize: "100% 2px",
          transform: `translate(${-dx * 0.5}px, ${-dy * 0.5}px)`,
        }}
      />
    </div>
  );
};
