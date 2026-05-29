import { useCurrentFrame, useVideoConfig } from "remotion";
import type { ClippedRenderProps } from "../types";
import type { Palette } from "../lib/palette";
import { cleanText, compactMeta } from "../lib/text";
import { MetadataStack, fonts } from "../typography";

export const MetadataBlock = ({
  props,
  palette,
  y,
  align = "center",
  revealFrame = 20,
  compact = false,
  style,
}: {
  props: ClippedRenderProps;
  palette: Palette;
  y?: number;
  align?: "center" | "left" | "right";
  revealFrame?: number;
  compact?: boolean;
  style?: React.CSSProperties;
}) => {
  const title = cleanText(props.metadata.title, cleanText(props.metadata.sourceFilename, "Untitled"));
  const artist = cleanText(props.metadata.artist, "Unknown Artist");
  const meta = compactMeta([props.metadata.album, props.metadata.year, props.metadata.genre]);

  // Resolve style preset
  const stylePreset = props.options.style === "brutal" ? "brutal" : 
                      props.options.style === "vhs" ? "vhs" : 
                      props.options.style === "minimal" ? "minimal" : "cinematic";

  return (
    <div
      style={{
        width: "100%",
        marginTop: y,
        zIndex: 50,
        ...style,
      }}
    >
      <MetadataStack
        title={title}
        artist={artist}
        meta={meta || undefined}
        preset={stylePreset}
        textColor={palette.text}
        accentColor={palette.accent}
        revealFrame={revealFrame}
        align={align}
      />
    </div>
  );
};

export const LowerThird = ({ props, palette }: { props: ClippedRenderProps; palette: Palette }) => {
  if (props.options.captions !== "metadata") {
    return null;
  }
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
      }}
    >
      <span>{cleanText(props.metadata.artist, "Unknown Artist")}</span>
      <span style={{ color: palette.accent }}>{cleanText(props.metadata.title, "Untitled")}</span>
    </div>
  );
};

