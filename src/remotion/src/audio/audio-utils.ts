import type { AudioData } from "@remotion/media-utils";
import { visualizeAudio } from "@remotion/media-utils";

export type AudioBand = "bass" | "lowMid" | "mid" | "highMid" | "treble" | "full";

export type AudioAnalysis = {
  ready: boolean;
  values: number[];
  bass: number;
  lowMid: number;
  mid: number;
  highMid: number;
  treble: number;
  full: number;
  rms: number;
  mapBand: (band: AudioBand, output: [number, number], input?: [number, number]) => number;
};

export const clamp = (value: number, min = 0, max = 1) => Math.min(max, Math.max(min, value));

export const lerp = (from: number, to: number, amount: number) => from + (to - from) * amount;

export const getRms = (values: number[]) => {
  if (!values.length) {
    return 0;
  }
  const sum = values.reduce((acc, value) => acc + value * value, 0);
  return Math.sqrt(sum / values.length);
};

export const averageRange = (values: number[], from: number, to: number) => {
  const start = Math.max(0, Math.floor(from));
  const end = Math.min(values.length, Math.max(start + 1, Math.floor(to)));
  const slice = values.slice(start, end);
  if (!slice.length) {
    return 0;
  }
  return clamp(slice.reduce((sum, value) => sum + value, 0) / slice.length);
};

export const fallbackAudioValues = (frame: number, samples: number, seed = "") =>
  Array.from({ length: samples }, (_, idx) => {
    const seedOffset = seed.length * 0.073;
    const phase = frame / 11 + idx * 0.42 + seedOffset;
    const slow = Math.sin(frame / 37 + idx * 0.11 + seedOffset) * 0.18;
    return clamp(0.12 + Math.abs(Math.sin(phase) * Math.cos(phase * 0.27)) * 0.72 + slow);
  });

export const analyzeValues = (values: number[]): AudioAnalysis => {
  const samples = Math.max(1, values.length);
  const bass = averageRange(values, 0, samples * 0.12);
  const lowMid = averageRange(values, samples * 0.12, samples * 0.28);
  const mid = averageRange(values, samples * 0.28, samples * 0.55);
  const highMid = averageRange(values, samples * 0.55, samples * 0.78);
  const treble = averageRange(values, samples * 0.78, samples);
  const full = averageRange(values, 0, samples);
  const rms = getRms(values);
  const bands: Record<AudioBand, number> = { bass, lowMid, mid, highMid, treble, full };

  return {
    ready: true,
    values,
    bass,
    lowMid,
    mid,
    highMid,
    treble,
    full,
    rms,
    mapBand: (band, output, input = [0, 1]) => {
      const value = clamp((bands[band] - input[0]) / Math.max(0.001, input[1] - input[0]));
      return lerp(output[0], output[1], value);
    },
  };
};

export const visualizeAudioValues = ({
  audioData,
  fps,
  frame,
  samples,
  seed = "",
}: {
  audioData: AudioData | null;
  fps: number;
  frame: number;
  samples: number;
  seed?: string;
}) => {
  if (!audioData) {
    return fallbackAudioValues(frame, samples, seed);
  }
  return visualizeAudio({
    fps,
    frame,
    audioData,
    numberOfSamples: samples,
    optimizeFor: "speed",
  }).map((value) => clamp(value));
};

