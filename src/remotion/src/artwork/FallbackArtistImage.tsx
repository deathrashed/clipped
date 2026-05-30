import { AbsoluteFill } from "remotion";
import type { Palette } from "../lib/palette";

type FallbackArtistImageProps = {
  width: number;
  height: number;
  palette: Palette;
  artistInitials?: string;
};

export const FallbackArtistImage = ({
  width,
  height,
  palette,
  artistInitials = "?",
}: FallbackArtistImageProps) => {
  return (
    <div
      style={{
        width,
        height,
        background: `
          linear-gradient(
            160deg,
            ${palette.bg} 0%,
            ${palette.panel} 45%,
            ${palette.bg} 100%
          )
        `,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        position: "relative",
        overflow: "hidden",
      }}
    >
      <div
        style={{
          position: "absolute",
          top: "-10%",
          left: "-10%",
          width: "60%",
          height: "60%",
          background: `radial-gradient(circle, ${palette.accent}11 0%, transparent 70%)`,
        }}
      />
      <div
        style={{
          position: "absolute",
          bottom: "-15%",
          right: "-10%",
          width: "50%",
          height: "50%",
          background: `radial-gradient(circle, ${palette.accent2}0d 0%, transparent 70%)`,
        }}
      />
      <span
        style={{
          fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
          fontSize: height * 0.18,
          fontWeight: 300,
          color: palette.muted,
          letterSpacing: "0.15em",
          opacity: 0.35,
          zIndex: 1,
        }}
      >
        {artistInitials.slice(0, 2).toUpperCase()}
      </span>
    </div>
  );
};
