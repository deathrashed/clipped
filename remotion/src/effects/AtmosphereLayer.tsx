import React from "react";
import { DustLayer } from "./DustLayer";
import { FogLayer } from "./FogLayer";

export type AtmosphereMode = "none" | "dust" | "fog" | "smoke" | "ash";

export type AtmosphereLayerProps = {
  mode?: AtmosphereMode;
  intensity?: number;
  seed?: number;
};

export const AtmosphereLayer: React.FC<AtmosphereLayerProps> = ({
  mode = "none",
  intensity = 1.0,
  seed = 42,
}) => {
  if (mode === "none") return null;

  switch (mode) {
    case "dust":
      return (
        <DustLayer
          count={Math.round(40 * intensity)}
          opacity={0.08 * intensity}
          drift={0.4}
          seed={seed}
        />
      );
    case "fog":
    case "smoke":
      return (
        <FogLayer
          opacity={0.12 * intensity}
          density={1.0 * intensity}
          drift={0.3}
        />
      );
    case "ash":
      return (
        <DustLayer
          count={Math.round(25 * intensity)}
          opacity={0.15 * intensity}
          drift={0.8} // ash falls/drifts faster
          seed={seed + 100}
          color="rgba(180, 180, 180, 0.5)" // greyish ash flakes
        />
      );
    default:
      return null;
  }
};
