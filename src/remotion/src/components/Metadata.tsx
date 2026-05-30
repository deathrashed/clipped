import type React from "react";
import { cleanText, compactMeta } from "../lib/text";
import { MetadataStack, fonts } from "../typography";
import type { TypographyPreset } from "../tokens/typography";
import type { Palette } from "../lib/palette";

export const MetadataBlock = ({
  title,
  artist,
  meta,
  align = "center",
  revealFrame = 20,
  typographyPreset = "cinematic",
  style,
}: {
  title: string;
  artist: string;
  meta?: string;
  align?: "center" | "left" | "right";
  revealFrame?: number;
  typographyPreset?: TypographyPreset;
  style?: React.CSSProperties & { accent?: string };
}) => {
  const { accent, ...domStyle } = style || {};

  return (
    <div
      style={{
        width: "100%",
        zIndex: 50,
        ...domStyle,
      }}
    >
      <MetadataStack
        title={title}
        artist={artist}
        meta={meta}
        preset={typographyPreset}
        textColor={style?.color}
        accentColor={accent}
        revealFrame={revealFrame}
        align={align}
      />
    </div>
  );
};

export const LowerThird = ({
  artist,
  title,
  palette,
  style,
}: {
  artist: string;
  title: string;
  palette: Palette;
  style?: React.CSSProperties;
}) => {
  return (
    <div
      style={{
        position: "absolute",
        left: 54,
        right: 54,
        bottom: 44,
        padding: "18px 24px",
        borderRadius: 12,
        background: palette.panel,
        color: palette.text,
        fontFamily: fonts.body,
        fontSize: 24,
        display: "flex",
        justifyContent: "space-between",
        gap: 22,
        zIndex: 50,
        ...style,
      }}
    >
      <span>{cleanText(artist, "Unknown Artist")}</span>
      <span style={{ color: palette.accent }}>{cleanText(title, "Untitled")}</span>
    </div>
  );
};
