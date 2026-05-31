import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import type { SpringConfig } from "remotion";

export type PhaseTiming = {
  startFrame: number;
  endFrame: number;
  duration: number;
};

export type TimelinePhases = {
  logo: PhaseTiming;
  phase1: PhaseTiming;
  phase2: PhaseTiming;
  phase3: PhaseTiming;
  outro: PhaseTiming;
};

export const useTimeline = (opts: {
  logoDuration?: number;
  phase1Start?: number;
  phase2Start?: number;
  phase3Start?: number;
  outroStart?: number;
}): TimelinePhases => {
  const { fps, durationInFrames } = useVideoConfig();

  const logoEnd = opts.phase1Start != null
    ? Math.min(opts.phase1Start * fps, durationInFrames * 0.3)
    : Math.min(fps * 2.5, durationInFrames * 0.2);

  const phase1Start = opts.phase1Start != null
    ? opts.phase1Start * fps
    : logoEnd;

  const phase2Start = opts.phase2Start != null
    ? opts.phase2Start * fps
    : Math.floor(durationInFrames * 0.45);

  const phase3Start = opts.phase3Start != null
    ? opts.phase3Start * fps
    : Math.floor(durationInFrames * 0.72);

  const outroStart = opts.outroStart != null
    ? Math.floor(durationInFrames - opts.outroStart * fps)
    : durationInFrames - Math.min(fps, Math.floor(durationInFrames * 0.1));

  return {
    logo: { startFrame: 0, endFrame: logoEnd, duration: logoEnd },
    phase1: { startFrame: phase1Start, endFrame: phase2Start, duration: phase2Start - phase1Start },
    phase2: { startFrame: phase2Start, endFrame: phase3Start, duration: phase3Start - phase2Start },
    phase3: { startFrame: phase3Start, endFrame: outroStart, duration: outroStart - phase3Start },
    outro: { startFrame: outroStart, endFrame: durationInFrames, duration: durationInFrames - outroStart },
  };
};

export const phaseOpacity = (frame: number, start: number, end: number, fadeIn = 12, fadeOut = 12): number => {
  return interpolate(
    frame,
    [start, start + fadeIn, end - fadeOut, end],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );
};

export const phaseSlide = (frame: number, start: number, end: number, distance = 40, fadeIn = 15): number => {
  const progress = interpolate(
    frame,
    [start, start + fadeIn, end - 10, end],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );
  return distance * (1 - progress);
};

export const easeIn = (frame: number, start: number, duration = 15): number =>
  interpolate(frame, [start, start + duration], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

export const easeOut = (frame: number, end: number, duration = 12): number =>
  interpolate(frame, [end - duration, end], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

export const useSpringReveal = (startFrame: number, config?: Partial<SpringConfig>) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return spring({
    frame: Math.max(0, frame - startFrame),
    fps,
    config: { damping: 18, stiffness: 90, ...config },
  });
};
