import { Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import type { Palette } from "../lib/palette";

export type BackgroundMode = "atmospheric" | "editorial" | "minimal" | "color";

/**
 * ArtworkBackground — cinematic blurred background field.
 *
 * atmospheric: heavy blur (40px), desaturated (0.45), color-graded dark
 * editorial:   moderate blur (20px), moderate saturation (0.7), higher contrast
 * minimal:     no image — solid bg color
 * color:       solid extracted/palette color (set via `solidColor` prop)
 *
 * Replaces BackgroundField. BackgroundField stays in Artwork.tsx as a
 * re-export alias for backwards compatibility.
 */
export const ArtworkBackground = ({
  src,
  palette,
  mode = "atmospheric",
  solidColor,
  driftIntensity = 0.035,
}: {
  src: string | null;
  palette: Palette;
  mode?: BackgroundMode;
  solidColor?: string;
  driftIntensity?: number;
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const resolvedSrc = src ? staticFile(src) : null;

  if (mode === "minimal" || mode === "color") {
    return (
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundColor: solidColor ?? palette.bg,
        }}
      />
    );
  }

  const blurAmount = mode === "editorial" ? 20 : 40;
  const saturation = mode === "editorial" ? 0.70 : 0.45;
  const brightness = mode === "editorial" ? 0.50 : 0.38;
  const scale = interpolate(frame, [0, durationInFrames], [1, 1.04 + driftIntensity]);

  return (
    <div style={{ position: "absolute", inset: 0, overflow: "hidden", backgroundColor: palette.bg }}>
      {resolvedSrc ? (
        <Img
          src={resolvedSrc}
          style={{
            position: "absolute",
            inset: "-8%",
            width: "116%",
            height: "116%",
            objectFit: "cover",
            transform: `scale(${scale})`,
            filter: `blur(${blurAmount}px) brightness(${brightness}) saturate(${saturation})`,
          }}
        />
      ) : (
        <div style={{ position: "absolute", inset: 0, backgroundColor: palette.bg }} />
      )}
      {/* Vignette gradient — dark edges, transparent center */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: "radial-gradient(circle at center, transparent 30%, rgba(0,0,0,0.72) 100%)",
        }}
      />
    </div>
  );
};
