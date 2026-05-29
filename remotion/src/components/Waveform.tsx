import { useMemo } from "react";
import { staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { useAudioData, visualizeAudio } from "@remotion/media-utils";
import type { ClippedRenderProps } from "../types";
import type { Palette } from "../lib/palette";
import { motionFactor } from "../lib/palette";

const fallbackSamples = (frame: number, count: number, seed = "") =>
  Array.from({ length: count }, (_, idx) => {
    const phase = frame / 12 + idx * 0.45 + seed.length;
    return 0.15 + Math.abs(Math.sin(phase) * Math.cos(phase * 0.31)) * 0.75;
  });

const powerOfTwoAtLeast = (value: number): number => 2 ** Math.ceil(Math.log2(Math.max(2, value)));

const Bars = ({ samples, palette, bottom }: { samples: number[]; palette: Palette; bottom: number }) => (
  <div
    style={{
      position: "absolute",
      left: 92,
      right: 92,
      bottom,
      height: 120,
      display: "flex",
      alignItems: "center",
      gap: 6,
    }}
  >
    {samples.map((sample, idx) => (
      <div
        key={idx}
        style={{
          flex: 1,
          height: `${10 + sample * 104}px`,
          borderRadius: 999,
          background: idx % 5 === 0 ? palette.accent2 : palette.accent,
          opacity: 0.55 + sample * 0.38,
          boxShadow: `0 0 ${10 + sample * 18}px ${palette.accent}66`,
        }}
      />
    ))}
  </div>
);

const AudioWaveformBars = ({
  audioSrc,
  palette,
  count,
  bottom,
}: {
  audioSrc: string;
  palette: Palette;
  count: number;
  bottom: number;
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const audioData = useAudioData(staticFile(audioSrc));
  const audioCount = powerOfTwoAtLeast(count);
  const samples = audioData
    ? visualizeAudio({ fps, frame, audioData, numberOfSamples: audioCount })
        .slice(0, count)
        .map((sample) => Math.max(0.08, sample))
    : fallbackSamples(frame, count, audioSrc);
  return <Bars samples={samples} palette={palette} bottom={bottom} />;
};

export const WaveformBars = ({
  props,
  palette,
  count = 52,
  bottom = 76,
}: {
  props: ClippedRenderProps;
  palette: Palette;
  count?: number;
  bottom?: number;
}) => {
  const frame = useCurrentFrame();
  const values = useMemo(() => fallbackSamples(frame, count, props.options.seed), [count, frame, props.options.seed]);

  if (props.options.waveform === "none") {
    return null;
  }
  if (props.assets.audioSrc) {
    return <AudioWaveformBars audioSrc={props.assets.audioSrc} palette={palette} count={count} bottom={bottom} />;
  }
  return <Bars samples={values} palette={palette} bottom={bottom} />;
};

const Radial = ({
  samples,
  props,
  palette,
  size,
  y,
  count,
  motion,
}: {
  samples: number[];
  props: ClippedRenderProps;
  palette: Palette;
  size: number;
  y: number;
  count: number;
  motion: number;
}) => {
  const frame = useCurrentFrame();
  return (
    <div
      style={{
        position: "absolute",
        left: "50%",
        top: "50%",
        width: size,
        height: size,
        transform: `translate(-50%, calc(-50% + ${y}px)) rotate(${frame * 0.12 * motion}deg)`,
        borderRadius: "50%",
      }}
    >
      {samples.map((sample, idx) => {
        const angle = (360 / count) * idx;
        const barHeight = props.options.waveform === "ring" ? 26 + sample * 78 : 48 + sample * 150;
        return (
          <div
            key={idx}
            style={{
              position: "absolute",
              left: "50%",
              top: "50%",
              width: 4,
              height: barHeight,
              borderRadius: 999,
              transformOrigin: `50% ${size / 2}px`,
              transform: `translate(-50%, -${size / 2}px) rotate(${angle}deg)`,
              background: idx % 6 === 0 ? palette.accent2 : palette.accent,
              opacity: 0.34 + sample * 0.5,
              boxShadow: `0 0 ${12 + sample * 18}px ${palette.accent}88`,
            }}
          />
        );
      })}
    </div>
  );
};

const AudioRadialWaveform = ({
  audioSrc,
  props,
  palette,
  size,
  y,
  count,
  motion,
}: {
  audioSrc: string;
  props: ClippedRenderProps;
  palette: Palette;
  size: number;
  y: number;
  count: number;
  motion: number;
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const audioData = useAudioData(staticFile(audioSrc));
  const audioCount = powerOfTwoAtLeast(count);
  const samples = audioData
    ? visualizeAudio({ fps, frame, audioData, numberOfSamples: audioCount })
        .slice(0, count)
        .map((sample) => Math.max(0.04, sample))
    : fallbackSamples(frame, count, audioSrc);
  return <Radial samples={samples} props={props} palette={palette} size={size} y={y} count={count} motion={motion} />;
};

export const RadialWaveform = ({
  props,
  palette,
  size,
  y = 0,
  count = 72,
}: {
  props: ClippedRenderProps;
  palette: Palette;
  size: number;
  y?: number;
  count?: number;
}) => {
  const frame = useCurrentFrame();
  const motion = motionFactor(props.options.motion);

  if (!["radial", "ring"].includes(String(props.options.waveform))) {
    return null;
  }
  if (props.assets.audioSrc) {
    return (
      <AudioRadialWaveform
        audioSrc={props.assets.audioSrc}
        props={props}
        palette={palette}
        size={size}
        y={y}
        count={count}
        motion={motion}
      />
    );
  }

  const samples = fallbackSamples(frame, count, props.options.seed);
  return <Radial samples={samples} props={props} palette={palette} size={size} y={y} count={count} motion={motion} />;
};
