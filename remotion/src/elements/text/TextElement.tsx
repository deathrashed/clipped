import type { CSSProperties } from "react";
import { TextFadeUp } from "../../transitions/TextFadeUp";
import { TextTrackIn } from "../../transitions/TextTrackIn";

type TextReveal = "none" | "fade-up" | "track-in" | "mask";

type TextElementProps = {
  text: string;
  preset?: "cinematic" | "minimal" | "brutal" | "mono";
  reveal?: TextReveal;
  align?: "left" | "center" | "right";
  intensity?: number;
};

const presetStyles: Record<string, CSSProperties> = {
  cinematic: {
    fontFamily: "'Oswald', -apple-system, sans-serif",
    fontWeight: 500,
    fontSize: 48,
    letterSpacing: "0.02em",
    lineHeight: 1.15,
  },
  minimal: {
    fontFamily: "'Inter', -apple-system, sans-serif",
    fontWeight: 400,
    fontSize: 36,
    letterSpacing: "0.01em",
    lineHeight: 1.3,
  },
  brutal: {
    fontFamily: "'Inter', -apple-system, sans-serif",
    fontWeight: 900,
    fontSize: 56,
    letterSpacing: "-0.02em",
    lineHeight: 1.05,
    textTransform: "uppercase",
  },
  mono: {
    fontFamily: "'SpaceMono', 'SF Mono', monospace",
    fontWeight: 400,
    fontSize: 28,
    letterSpacing: "0.04em",
    lineHeight: 1.4,
  },
};

export const TextElement = ({
  text,
  preset = "cinematic",
  reveal = "fade-up",
  align = "center",
  intensity = 0.5,
}: TextElementProps) => {
  const progress = Math.min(1, intensity * 1.2);

  const inner = (
    <span
      style={{
        ...presetStyles[preset],
        textAlign: align,
        display: "block",
        width: "100%",
        color: "inherit",
      }}
    >
      {text}
    </span>
  );

  if (reveal === "fade-up") {
    return <TextFadeUp progress={progress}>{inner}</TextFadeUp>;
  }
  if (reveal === "track-in") {
    return <TextTrackIn progress={progress}>{inner}</TextTrackIn>;
  }
  return inner;
};
