import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import type { CSSProperties } from "react";
import type { TypographyPreset } from "../tokens/typography";
import { resolveTypeScale, typeSize } from "../tokens/typography";
import { resolveFont } from "./fonts";

export const ArtistName = ({
  text,
  preset = "cinematic",
  color,
  revealFrame = 8,
  align = "center",
}: {
  text: string;
  preset?: TypographyPreset;
  color?: string;
  revealFrame?: number;
  align?: CSSProperties["textAlign"];
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const scale = resolveTypeScale(preset);
  const t = scale.artistName;
  const minDim = Math.min(width, height);
  const size = typeSize(t.sizeFactor, minDim);
  const isBrutal = preset === "brutal";

  const reveal = spring({ frame: frame - revealFrame, fps, config: { damping: 26, stiffness: 120 } });
  const opacity = interpolate(reveal, [0, 1], [0, 1]);
  const translateY = interpolate(reveal, [0, 1], [14, 0]);

  return (
    <div
      style={{
        fontFamily: resolveFont(t.fontFamily, isBrutal),
        fontSize: size,
        fontWeight: t.weight,
        letterSpacing: `${t.tracking}em`,
        textTransform: t.transform,
        color: color ?? "rgba(255,255,255,0.72)",
        textAlign: align,
        lineHeight: 1.2,
        textShadow: "0 2px 10px rgba(0,0,0,0.55)",
        opacity,
        transform: `translateY(${translateY}px)`,
      }}
    >
      {text}
    </div>
  );
};
