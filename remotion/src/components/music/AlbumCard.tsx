import { Img, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import type { ClippedRenderProps } from "../../types";
import type { Palette } from "../../lib/palette";

export const BorderedAlbumCard = ({
  props,
  palette,
  size,
  y = 0,
  radius = 22,
  revealFrame = 0,
}: {
  props: ClippedRenderProps;
  palette: Palette;
  size: number;
  y?: number;
  radius?: number;
  revealFrame?: number;
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const src = props.assets.coverSrc ? staticFile(props.assets.coverSrc) : null;
  const reveal = spring({ frame: frame - revealFrame, fps, config: { damping: 20, stiffness: 92 } });
  const shadow = "0 36px 120px rgba(0,0,0,0.72), 0 0 0 1px rgba(255,255,255,0.15)";

  return (
    <div
      style={{
        position: "absolute",
        left: "50%",
        top: "50%",
        width: size,
        height: size,
        transform: `translate(-50%, calc(-50% + ${y + (1 - reveal) * 36}px)) scale(${0.96 + reveal * 0.04})`,
        opacity: reveal,
        borderRadius: radius,
        padding: 7,
        background: "rgba(255,255,255,0.9)",
        boxShadow: shadow,
      }}
    >
      <div
        style={{
          width: "100%",
          height: "100%",
          overflow: "hidden",
          borderRadius: Math.max(0, radius - 6),
          background: palette.panel,
        }}
      >
        {src ? (
          <Img src={src} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
        ) : (
          <div
            style={{
              width: "100%",
              height: "100%",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: palette.muted,
              fontFamily: "Arial, Helvetica, sans-serif",
              fontSize: 42,
            }}
          >
            No Artwork
          </div>
        )}
      </div>
    </div>
  );
};

export const CompactCaption = ({ props, palette, y }: { props: ClippedRenderProps; palette: Palette; y: number }) => (
  <div
    style={{
      position: "absolute",
      left: "50%",
      top: y,
      transform: "translateX(-50%)",
      width: "80%",
      color: palette.text,
      textAlign: "center",
      fontFamily: "Arial, Helvetica, sans-serif",
      textShadow: "0 8px 26px rgba(0,0,0,0.8)",
    }}
  >
    <div style={{ fontSize: 38, lineHeight: 1.1, fontWeight: 700 }}>{props.metadata.title || "Untitled"}</div>
    <div style={{ marginTop: 10, fontSize: 23, color: palette.muted }}>{props.metadata.artist || "Unknown Artist"}</div>
  </div>
);

