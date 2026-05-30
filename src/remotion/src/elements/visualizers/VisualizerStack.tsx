import type { CSSProperties } from "react";
import type { AudioAnalysis } from "../../audio/audio-utils";
import type { Palette } from "../../lib/palette";
import type { VisualizerElementProps } from "../types";
import { SpectrumBars } from "../../visualizers/SpectrumBars";
import { Oscilloscope } from "../../visualizers/Oscilloscope";
import { RadialBars } from "../../visualizers/RadialBars";
import { PulseRings } from "../../visualizers/PulseRings";
import { FerroFluid } from "./FerroFluid";

export const VisualizerStack = ({
  id,
  audio,
  palette,
  appearance,
  intensity = 0.5,
  color,
  primaryColor,
  secondaryColor,
  density,
  pattern: patternVal,
  volume,
  width = 860,
  height = 96,
}: VisualizerElementProps & { id: string }) => {
  const opacity = appearance?.opacity ?? 1;
  switch (id) {
    case "spectre":
      return (
        <SpectrumBars
          audio={audio}
          palette={palette}
          count={48}
          width={width}
          height={height}
          color={color}
        />
      );
    case "oscilloscope":
      return (
        <Oscilloscope
          audio={audio}
          palette={palette}
          width={width}
          height={height}
          color={color}
          strokeWidth={1.5}
        />
      );
    case "pulsar":
      return (
        <PulseRings
          audio={audio}
          palette={palette}
          size={Math.min(width, height) * 1.2}
          ringCount={Math.round(patternVal || 4) + 4}
          color={primaryColor || color}
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
          mode="ring"
        />
      );
    case "waveform":
      return (
        <Oscilloscope
          audio={audio}
          palette={palette}
          width={width}
          height={height}
          color={color}
          strokeWidth={3}
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
            opacity: (intensity || 0.5) * 0.7 + 0.3,
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
