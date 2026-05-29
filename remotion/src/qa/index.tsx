import { AbsoluteFill } from "remotion";
import { Pixelation } from "../elements/effects/texture";
import { Strobe } from "../elements/effects/glow";
import { FerroFluid } from "../elements/visualizers";
import type { AudioAnalysis } from "../audio/audio-utils";
import type { Palette } from "../lib/palette";

const mockAudio: AudioAnalysis = {
  ready: true,
  values: Array.from({ length: 128 }, (_, i) => {
    const phase = i * 0.12;
    return 0.15 + Math.abs(Math.sin(phase)) * 0.7 + Math.random() * 0.15;
  }),
  bass: 0.4,
  lowMid: 0.5,
  mid: 0.6,
  highMid: 0.4,
  treble: 0.3,
  full: 0.5,
  rms: 0.3,
  mapBand: (_band: string, output: [number, number], _input?: [number, number]) => {
    const t = 0.5;
    return output[0] + (output[1] - output[0]) * t;
  },
};

const mockPalette: Palette = {
  bg: "#111111",
  panel: "rgba(17,17,17,0.68)",
  text: "#ffffff",
  muted: "#888888",
  accent: "#ff6b6b",
  accent2: "#ffd93d",
  border: "rgba(255,107,107,0.82)",
};

export const QAPixelation = () => (
  <AbsoluteFill style={{ backgroundColor: "#222" }}>
    <div
      style={{
        position: "absolute",
        inset: 0,
        background: "linear-gradient(135deg, #ff6b6b 0%, #6bcbff 50%, #a66cff 100%)",
      }}
    />
    <Pixelation intensity={0.5} opacity={1} />
  </AbsoluteFill>
);

export const QAFerroFluid = () => (
  <AbsoluteFill style={{ backgroundColor: "#111" }}>
    <FerroFluid audio={mockAudio} palette={mockPalette} intensity={0.7} width={1080} height={1080} />
  </AbsoluteFill>
);

export const QAStrobe = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#222" }}>
      <Strobe intensity={0.5} />
    </AbsoluteFill>
  );
};
