import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import type { CSSProperties } from "react";
import type { TypographyPreset } from "../tokens/typography";
import { resolveTypeScale, typeSize } from "../tokens/typography";
import { resolveFont } from "./fonts";

export const TrackTitle = ({
  text,
  preset = "cinematic",
  color = "white",
  revealFrame = 0,
  align = "center",
  maxWidth,
}: {
  text: string;
  preset?: TypographyPreset;
  color?: string;
  revealFrame?: number;
  align?: CSSProperties["textAlign"];
  maxWidth?: number | string;
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const scale = resolveTypeScale(preset);
  const t = scale.trackTitle;
  const minDim = Math.min(width, height);
  const size = typeSize(t.sizeFactor, minDim);
  const isBrutal = preset === "brutal";

  const reveal = spring({ frame: frame - revealFrame, fps, config: { damping: 26, stiffness: 120 } });
  const opacity = interpolate(reveal, [0, 1], [0, 1]);
  const translateY = interpolate(reveal, [0, 1], [18, 0]);

  return (
    <div
      style={{
        fontFamily: resolveFont(t.fontFamily, isBrutal),
        fontSize: size,
        fontWeight: t.weight,
        letterSpacing: `${t.tracking}em`,
        textTransform: t.transform,
        color,
        textAlign: align,
        lineHeight: 1.1,
        textShadow: "0 3px 14px rgba(0,0,0,0.65)",
        opacity,
        transform: `translateY(${translateY}px)`,
        maxWidth: maxWidth ?? "100%",
      }}
    >
      {text}
    </div>
  );
};
