import type { CSSProperties } from "react";
import type { AudioAnalysis } from "../../audio/audio-utils";
import type { Palette } from "../../lib/palette";
import { SpectrumBars } from "../../visualizers/SpectrumBars";
import { Oscilloscope } from "../../visualizers/Oscilloscope";
import { RadialBars } from "../../visualizers/RadialBars";
import { FerroFluid } from "./FerroFluid";

export type VisualizerElementProps = {
  audio: AudioAnalysis;
  palette: Palette;
  intensity?: number;
  opacity?: number;
  glow?: boolean;
  variant?: string;
  width?: number;
  height?: number;
};

export const VisualizerStack = ({
  id,
  audio,
  palette,
  intensity = 0.5,
  glow = false,
  variant,
  width = 860,
  height = 96,
}: VisualizerElementProps & { id: string }) => {
  switch (id) {
    case "spectre":
      return (
        <SpectrumBars
          audio={audio}
          palette={palette}
          count={48}
          width={width}
          height={height}
          mirror={variant === "mirror"}
          glow={glow}
        />
      );
    case "oscilloscope":
      return (
        <Oscilloscope
          audio={audio}
          palette={palette}
          width={width}
          height={height}
          strokeWidth={1.5}
          glow={glow}
        />
      );
    case "pulsar":
      return (
        <RadialBars
          audio={audio}
          palette={palette}
          size={Math.min(width, height) * 1.2}
          innerRadius={Math.min(width, height) * 0.35}
          count={32}
          mode="ring"
        />
      );
    case "circle":
      return (
        <RadialBars
          audio={audio}
          palette={palette}
          size={Math.min(width, height) * 1.4}
          innerRadius={Math.min(width, height) * 0.35}
          count={64}
          mode={variant === "flower" ? "flower" : "ring"}
        />
      );
    case "ferro-fluid":
      return (
        <div
          style={{
            width,
            height,
            position: "relative",
            overflow: "hidden",
            opacity: intensity * 0.7 + 0.3,
          }}
        >
          <FerroFluid
            audio={audio}
            palette={palette}
            intensity={intensity}
            width={width}
            height={height}
          />
        </div>
      );
    default:
      return null;
  }
};
