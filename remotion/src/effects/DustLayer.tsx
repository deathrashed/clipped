import React from "react";
import { AbsoluteFill, random, useCurrentFrame } from "remotion";

export type DustLayerProps = {
  count?: number;
  opacity?: number;
  drift?: number;
  seed?: number;
  color?: string;
};

export const DustLayer: React.FC<DustLayerProps> = ({
  count = 40,
  opacity = 0.08,
  drift = 0.5,
  seed = 42,
  color = "rgba(255, 255, 255, 0.7)",
}) => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill style={{ pointerEvents: "none", opacity, mixBlendMode: "screen", zIndex: 85 }}>
      {Array.from({ length: count }).map((_, idx) => {
        const pSeed = `${seed}-${idx}`;
        const startX = random(pSeed + "-x") * 100;
        const startY = random(pSeed + "-y") * 100;
        const size = 1.0 + random(pSeed + "-size") * 2.5;
        const speedX = (0.2 + random(pSeed + "-speedx") * 0.4) * drift;
        const speedY = -(0.3 + random(pSeed + "-speedy") * 0.5) * drift;

        const x = (startX + frame * speedX) % 100;
        const y = (startY + frame * speedY + 100) % 100;
        const twinkle = 0.3 + 0.7 * Math.abs(Math.sin(frame * 0.02 + idx * 0.5));

        return (
          <div
            key={idx}
            style={{
              position: "absolute",
              left: `${x}%`,
              top: `${y}%`,
              width: size,
              height: size,
              borderRadius: "50%",
              backgroundColor: color,
              opacity: twinkle,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

