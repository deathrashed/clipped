import type { CSSProperties } from "react";
import { Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import type { ClippedRenderProps } from "../types";
import type { Palette } from "../lib/palette";
import { motionFactor } from "../lib/palette";
import { ArtworkBackground } from "../artwork/ArtworkBackground";

const fallbackStyle = (palette: Palette): CSSProperties => ({
  width: "100%",
  height: "100%",
  backgroundColor: palette.panel,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  color: palette.muted,
  fontSize: 46,
  fontFamily: "Arial, Helvetica, sans-serif",
  textAlign: "center",
  padding: 56,
});

export const BackgroundField = ({
  props,
  palette,
  intensity = 1,
}: {
  props: ClippedRenderProps;
  palette: Palette;
  intensity?: number;
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  // Prefer explicit background override, fallback to cover art
  const bgSrc = (props.assets as any).backgroundSrc ?? props.assets.coverSrc;
  const src = bgSrc ? staticFile(bgSrc) : null;
  const move = interpolate(frame, [0, durationInFrames], [1, 1.05 + intensity * 0.035]);
  const brightness = props.options.style === "zine" ? 0.54 : 0.42;

  return (
    <div style={{ position: "absolute", inset: 0, overflow: "hidden", backgroundColor: palette.bg }}>
      {src ? (
        <Img
          src={src}
          style={{
            position: "absolute",
            inset: "-8%",
            width: "116%",
            height: "116%",
            objectFit: "cover",
            transform: `scale(${move})`,
            filter: `blur(${28 + intensity * 12}px) brightness(${brightness}) saturate(0.92)`,
          }}
        />
      ) : (
        <div style={{ position: "absolute", inset: 0, backgroundColor: palette.bg }} />
      )}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            props.options.style === "brutal"
              ? "linear-gradient(180deg, rgba(0,0,0,0.25), rgba(0,0,0,0.75))"
              : "radial-gradient(circle at center, rgba(255,255,255,0.06), rgba(0,0,0,0.72))",
        }}
      />
    </div>
  );
};


export const FramedArtwork = ({
  props,
  palette,
  size,
  radius = 28,
  y = 0,
  revealFrame = 0,
  rotate = 0,
}: {
  props: ClippedRenderProps;
  palette: Palette;
  size: number;
  radius?: number;
  y?: number;
  revealFrame?: number;
  rotate?: number;
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const src = props.assets.coverSrc ? staticFile(props.assets.coverSrc) : null;
  const motion = motionFactor(props.options.motion);
  const reveal = spring({ frame: frame - revealFrame, fps, config: { damping: 18, stiffness: 90 } });
  const drift = Math.sin(frame / (60 / motion)) * 4 * motion;
  const scale = 0.92 + reveal * 0.08;

  return (
    <div
      style={{
        position: "absolute",
        left: "50%",
        top: "50%",
        width: size,
        height: size,
        transform: `translate(-50%, calc(-50% + ${y + drift}px)) scale(${scale}) rotate(${rotate}deg)`,
        borderRadius: radius,
        padding: 8,
        background: palette.border,
        boxShadow: `0 ${30 + 20 * motion}px ${90 + 20 * motion}px rgba(0,0,0,0.62)`,
        opacity: reveal,
      }}
    >
      <div style={{ width: "100%", height: "100%", overflow: "hidden", borderRadius: Math.max(0, radius - 7) }}>
        {src ? (
          <Img src={src} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
        ) : (
          <div style={fallbackStyle(palette)}>No Artwork</div>
        )}
      </div>
    </div>
  );
};

export const RecordArtwork = ({
  props,
  palette,
  size,
  y = 0,
  revealFrame = 0,
}: {
  props: ClippedRenderProps;
  palette: Palette;
  size: number;
  y?: number;
  revealFrame?: number;
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const src = props.assets.coverSrc ? staticFile(props.assets.coverSrc) : null;
  const motion = motionFactor(props.options.motion);
  const reveal = spring({ frame: frame - revealFrame, fps, config: { damping: 20, stiffness: 85 } });
  const rotation = frame * 0.48 * motion;

  return (
    <div
      style={{
        position: "absolute",
        left: "50%",
        top: "50%",
        width: size,
        height: size,
        transform: `translate(-50%, calc(-50% + ${y}px)) scale(${0.9 + reveal * 0.1}) rotate(${rotation}deg)`,
        borderRadius: "50%",
        overflow: "hidden",
        opacity: reveal,
        border: `6px solid ${palette.border}`,
        boxShadow: `0 34px 100px rgba(0,0,0,0.7), 0 0 70px ${palette.accent}44`,
        backgroundColor: palette.panel,
      }}
    >
      {src ? (
        <Img src={src} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
      ) : (
        <div style={fallbackStyle(palette)}>No Artwork</div>
      )}
      <div
        style={{
          position: "absolute",
          inset: "42%",
          borderRadius: "50%",
          background: palette.bg,
          border: `4px solid ${palette.border}`,
        }}
      />
    </div>
  );
};

// Backwards-compat alias. New code should import from artwork/ArtworkBackground.
export { ArtworkBackground } from "../artwork/ArtworkBackground";
/** @deprecated Use ArtworkBackground from artwork/ArtworkBackground */
export const BackgroundFieldV2 = ArtworkBackground;
