import type { CSSProperties } from "react";
import type { TypographyPreset } from "../tokens/typography";
import { TrackTitle } from "./TrackTitle";
import { ArtistName } from "./ArtistName";
import { MetaLine } from "./MetaLine";
import { sp } from "../tokens/spacing";

export const MetadataStack = ({
  title,
  artist,
  meta,
  preset = "cinematic",
  accentColor,
  textColor,
  revealFrame = 0,
  align = "center",
  gap,
}: {
  title: string;
  artist: string;
  meta?: string;
  preset?: TypographyPreset;
  accentColor?: string;
  textColor?: string;
  revealFrame?: number;
  align?: CSSProperties["textAlign"];
  gap?: number;
}) => {
  const gapPx = gap ?? sp.metaGap;

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: align === "center" ? "center" : align === "left" ? "flex-start" : "flex-end", gap: gapPx }}>
      <TrackTitle  text={title}  preset={preset} color={textColor}        revealFrame={revealFrame}      align={align} />
      <ArtistName  text={artist} preset={preset}                          revealFrame={revealFrame + 8}  align={align} />
      {meta ? <MetaLine text={meta} preset={preset} color={accentColor} revealFrame={revealFrame + 16} align={align} /> : null}
    </div>
  );
};
