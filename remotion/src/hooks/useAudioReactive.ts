import { useMemo } from "react";
import { staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { useAudioData } from "@remotion/media-utils";
import type { AudioAnalysis } from "../audio/audio-utils";
import { analyzeValues, fallbackAudioValues, visualizeAudioValues } from "../audio/audio-utils";

const silentAnalysis = (frame: number, samples: number, seed = ""): AudioAnalysis =>
  analyzeValues(fallbackAudioValues(frame, samples, seed));

export const useAudioReactive = (audioSrc: string | null | undefined, samples = 128, seed = "") => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const sampleCount = 2 ** Math.ceil(Math.log2(Math.max(2, samples)));
  const resolvedSrc = audioSrc ? staticFile(audioSrc) : staticFile("silence.wav");
  const audioData = useAudioData(resolvedSrc);

  return useMemo(() => {
    if (!audioSrc) {
      return silentAnalysis(frame, sampleCount, seed);
    }
    const values = visualizeAudioValues({
      audioData,
      fps,
      frame,
      samples: sampleCount,
      seed: audioSrc + seed,
    });
    return { ...analyzeValues(values), ready: Boolean(audioData) };
  }, [audioData, audioSrc, fps, frame, sampleCount, seed]);
};
