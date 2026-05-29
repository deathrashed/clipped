import { AbsoluteFill, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import type { ClippedRenderProps } from "../types";
import { AudioLayer } from "../components/AudioLayer";
import { ArtworkBackground } from "../artwork/ArtworkBackground";
import { ArtworkFrame } from "../artwork/ArtworkFrame";
import { FallbackArtwork } from "../artwork/FallbackArtwork";
import { MetadataBlock } from "../components/Metadata";
import { Captions } from "../components/lyrics/Captions";
import { resolvePalette } from "../lib/palette";
import { useLayout } from "../layouts";
import { cleanText, compactMeta } from "../lib/text";
import { resolveScenePreset } from "../presets/scene-presets";
import { ColorGrade, AtmosphereLayer, Halation, AmbientLight, RimLight } from "../effects";
import { BlurDissolve } from "../transitions/BlurDissolve";
import { TextTrackIn } from "../transitions/TextTrackIn";
import { ElementStack } from "../elements";

export const PremiumCard = (props: ClippedRenderProps) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const palette = resolvePalette(props);
  const scenePreset = resolveScenePreset(props.options.style);

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

      {/* ── 3. Album Cover Card (Reveals after logo, wrapped in BlurDissolve) ── */}
      {frame >= coverRevealFrame ? (
        <div
          style={{
            position: "absolute",
            left: layout.artwork.cx,
            top: layout.artwork.cy,
            transform: `translate(-50%, -50%) scale(${0.96 + coverReveal * 0.04})`,
            zIndex: 10,
          }}
        >
          <BlurDissolve progress={0.5 + coverReveal * 0.5} maxBlur={24} style={{ opacity: globalFadeOpacity }}>
            <ArtworkFrame size={coverSize} preset="matte">
              {coverSrc ? (
                <Img src={coverSrc} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
              ) : (
                <FallbackArtwork size={coverSize} palette={palette} seed={props.metadata.title} />
              )}
              {scenePreset.rimLight.enabled && (
                <RimLight
                  color={scenePreset.rimLight.color}
                  opacity={scenePreset.rimLight.opacity}
                  side="all"
                />
              )}
            </ArtworkFrame>
          </BlurDissolve>
        </div>
      ) : null}

      {/* ── 4. Title / Artist Metadata with editorial track-in ── */}
      {showMetadata && frame >= textRevealFrame ? (
        <TextTrackIn
          progress={textReveal}
          startTracking={0.18}
          targetTracking={-0.02}
          style={{
            position: "absolute",
            left: layout.typography.left,
            top: layout.typography.top,
            width: layout.typography.width,
            opacity: globalFadeOpacity,
            zIndex: 20,
          }}
        >
          <MetadataBlock
            title={cleanText(props.metadata.title, cleanText(props.metadata.sourceFilename, "Untitled"))}
            artist={cleanText(props.metadata.artist, "Unknown Artist")}
            meta={compactMeta([props.metadata.album, props.metadata.year, props.metadata.genre]) || undefined}
            align={layout.typography.align}
            revealFrame={textRevealFrame}
            typographyPreset={scenePreset.typographyPreset}
            style={{
              color: palette.text,
              accent: palette.accent,
            }}
          />
        </TextTrackIn>
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

      {/* ── Element Stack (effects, lights, depth, backgrounds, modifiers) ── */}
      <ElementStack
        elements={[
          ...(scenePreset.background || []),
          ...(scenePreset.effects || []),
          ...(scenePreset.lights || []),
        ]}
      />

      {/* ── 6. Cinematic PostFX Overlays ── */}
      <ColorGrade preset={scenePreset.colorGrade} />
      <AtmosphereLayer mode={scenePreset.atmosphere} intensity={1} />
      {scenePreset.halation.enabled && (
        <Halation
          opacity={scenePreset.halation.opacity}
          blur={scenePreset.halation.blur}
          warmth={scenePreset.halation.warmth}
        />
      )}
      {scenePreset.ambientLight.enabled && (
        <AmbientLight
          color={scenePreset.ambientLight.color}
          opacity={scenePreset.ambientLight.opacity}
        />
      )}
    </AbsoluteFill>
  );
};
