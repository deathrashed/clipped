import { AbsoluteFill, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import type { ClippedRenderProps } from "../types";
import { AudioLayer } from "../components/AudioLayer";
import { ArtworkBackground } from "../artwork/ArtworkBackground";
import { ArtworkFrame } from "../materials";
import { MetadataBlock } from "../components/Metadata";
import { Captions } from "../components/lyrics/Captions";
import { resolvePalette } from "../lib/palette";
import { useLayout } from "../layouts";

export const PremiumCard = (props: ClippedRenderProps) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const palette = resolvePalette(props);

  const hasLogo = !!props.assets.logoSrc;
  
  // ── Layout & Sizes ────────────────────────────────────────────────────────
  const layout = useLayout("editorial-left");
  const coverSize = layout.artwork.size;

  // ── Animation Timings ──────────────────────────────────────────────────────
  // 1. Logo Intro Phase (0s - 3s)
  const logoFadeInStart = 0;
  const logoFadeInEnd = 24; // 0.8s
  const logoFadeOutStart = 66; // 2.2s
  const logoFadeOutEnd = 90; // 3.0s

  const logoOpacity = hasLogo
    ? interpolate(
        frame,
        [logoFadeInStart, logoFadeInEnd, logoFadeOutStart, logoFadeOutEnd],
        [0, 1, 1, 0],
        { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
      )
    : 0;

  // 2. Cover & Metadata Reveal Phase
  const coverRevealFrame = hasLogo ? 90 : 0;
  const coverReveal = spring({
    frame: frame - coverRevealFrame,
    fps,
    config: { damping: 20, stiffness: 90 },
  });

  const textRevealFrame = coverRevealFrame + 25;
  const textReveal = interpolate(
    frame,
    [textRevealFrame, textRevealFrame + 20],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // 3. Global Outro Fade Out (last 1s / 30 frames)
  const outroFadeStart = durationInFrames - 30;
  const globalFadeOpacity = interpolate(
    frame,
    [outroFadeStart, durationInFrames - 3],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const coverSrc = props.assets.coverSrc ? staticFile(props.assets.coverSrc) : null;
  const logoSrc = props.assets.logoSrc ? staticFile(props.assets.logoSrc) : null;

  const showMetadata = props.options.captions === "off";

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <AudioLayer props={props} />

      {/* ── 1. Blurred Zooming Background ── */}
      <ArtworkBackground src={props.assets.coverSrc} palette={palette} mode="atmospheric" />

      {/* ── 2. Centered Logo Intro (No Frame) ── */}
      {hasLogo && logoSrc && frame < logoFadeOutEnd + 5 ? (
        <div
          style={{
            position: "absolute",
            left: "50%",
            top: "50%",
            transform: "translate(-50%, -50%)",
            opacity: logoOpacity * globalFadeOpacity,
            zIndex: 30,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <Img
            src={logoSrc}
            style={{
              maxWidth: layout.width * 0.7,
              maxHeight: layout.height * 0.45,
              objectFit: "contain",
            }}
          />
        </div>
      ) : null}

      {/* ── 3. Album Cover Card (Reveals after logo) ── */}
      {coverSrc && frame >= coverRevealFrame ? (
        <div
          style={{
            position: "absolute",
            left: layout.artwork.cx,
            top: layout.artwork.cy,
            transform: `translate(-50%, -50%) scale(${0.96 + coverReveal * 0.04})`,
            opacity: coverReveal * globalFadeOpacity,
            zIndex: 10,
          }}
        >
          <ArtworkFrame size={coverSize} preset="matte">
            <Img src={coverSrc} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
          </ArtworkFrame>
        </div>
      ) : null}

      {/* ── 4. Static Fading Title / Artist Metadata (Only if Captions are Off) ── */}
      {showMetadata && frame >= textRevealFrame ? (
        <div
          style={{
            position: "absolute",
            left: layout.typography.left,
            top: layout.typography.top,
            width: layout.typography.width,
            opacity: textReveal * globalFadeOpacity,
            zIndex: 20,
          }}
        >
          <MetadataBlock
            props={props}
            palette={palette}
            y={0}
            align={layout.typography.align}
            revealFrame={textRevealFrame}
          />
        </div>
      ) : null}

      {/* ── 5. Synced Lyrics / Captions ── */}
      {frame >= coverRevealFrame ? (
        <Captions
          lyricsSrc={props.assets.lyrics}
          lyricsJson={(props.assets as any).lyricsJson}
          captionsStyle={props.options.captions as any}
          originalStart={props.audio.originalStart}
          metadata={{
            title: props.metadata.title,
            artist: props.metadata.artist,
            album: props.metadata.album,
          }}
        />
      ) : null}
    </AbsoluteFill>
  );
};

