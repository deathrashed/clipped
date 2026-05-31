import { AbsoluteFill, Img, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import type { ClippedRenderProps } from "../types";
import { AudioLayer } from "../components/AudioLayer";
import { ArtworkFrame } from "../artwork/ArtworkFrame";
import { FallbackArtwork } from "../artwork/FallbackArtwork";
import { FallbackArtistImage } from "../artwork/FallbackArtistImage";
import { MetadataBlock } from "../components/Metadata";
import { ColorGrade, AtmosphereLayer, Halation, AmbientLight, RimLight } from "../effects";
import { ElementStack } from "../elements";
import { resolvePalette, motionFactor } from "../lib/palette";
import { cleanText, compactMeta } from "../lib/text";
import { resolveScenePreset } from "../presets/scene-presets";
import { useLayout } from "../layouts";
import { resolveAssets } from "../template-helpers/templateAssets";
import { useTimeline, easeIn } from "../template-helpers/templateTiming";

export const ArtistFocusPro = (props: ClippedRenderProps) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const palette = resolvePalette(props);
  const motion = motionFactor(props.options.motion);
  const scenePreset = resolveScenePreset(props.options.style);
  const layout = useLayout("editorial-left");
  const coverSize = layout.artwork.size;
  const assets = resolveAssets(props);

  const timeline = useTimeline({ phase1Start: 0, phase2Start: 2.5, phase3Start: 5, outroStart: 1.2 });
  const heroImg = assets.artistImageSrc || assets.coverSrc;

  const heroZoom = interpolate(frame, [0, durationInFrames], [1.04, 1.14]);
  const heroBrightness = interpolate(
    frame,
    [0, timeline.phase2.startFrame, timeline.phase3.startFrame],
    [0.35, 0.55, 0.5],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  const logoIn = easeIn(frame, timeline.phase1.startFrame + 8, 18);
  const logoOpacity = interpolate(
    frame,
    [timeline.phase1.startFrame + 8, timeline.phase1.startFrame + 26, timeline.phase2.startFrame + fps, timeline.phase2.startFrame + fps + 15],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  const coverReveal = easeIn(frame, timeline.phase2.startFrame, 18);
  const coverY = interpolate(coverReveal, [0, 1], [60, 0]);
  const coverScale = 0.88 + coverReveal * 0.12;

  const metaReveal = easeIn(frame, timeline.phase2.startFrame + fps * 0.4, 16);

  const globalFade = frame > durationInFrames - 30
    ? interpolate(frame, [durationInFrames - 30, durationInFrames - 3], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })
    : 1;

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <AudioLayer props={props} />

      <div style={{ position: "absolute", inset: 0, overflow: "hidden" }}>
        {heroImg ? (
          <Img
            src={heroImg}
            style={{
              position: "absolute",
              inset: "-8%",
              width: "116%",
              height: "116%",
              objectFit: "cover",
              transform: `scale(${heroZoom})`,
              filter: `blur(6px) brightness(${heroBrightness}) saturate(0.85)`,
            }}
          />
        ) : (
          <div style={{ position: "absolute", inset: 0, background: palette.bg }} />
        )}
        <div
          style={{
            position: "absolute",
            inset: 0,
            background: "linear-gradient(180deg, rgba(0,0,0,0.6) 0%, rgba(0,0,0,0.15) 30%, rgba(0,0,0,0.3) 70%, rgba(0,0,0,0.7) 100%)",
          }}
        />
      </div>

      {assets.hasLogo && logoOpacity > 0 ? (
        <div
          style={{
            position: "absolute",
            left: "50%",
            top: "50%",
            transform: "translate(-50%, -50%)",
            opacity: logoOpacity * globalFade,
            zIndex: 20,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <Img
            src={assets.logoSrc!}
            style={{
              maxWidth: layout.width * 0.7,
              maxHeight: layout.height * 0.35,
              objectFit: "contain",
              filter: "drop-shadow(0 10px 40px rgba(0,0,0,0.7))",
            }}
          />
        </div>
      ) : null}

      {frame >= timeline.phase2.startFrame ? (
        <div
          style={{
            position: "absolute",
            left: layout.artwork.cx,
            top: layout.artwork.cy,
            transform: `translate(-50%, calc(-50% + ${coverY}px)) scale(${coverScale})`,
            opacity: coverReveal * globalFade,
            zIndex: 10,
          }}
        >
          <ArtworkFrame size={coverSize} preset="matte">
            {props.assets.coverSrc ? (
              <Img src={assets.coverSrc!} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
            ) : (
              <FallbackArtwork size={coverSize} palette={palette} seed={props.metadata.title} />
            )}
            {scenePreset.rimLight.enabled && (
              <RimLight color={scenePreset.rimLight.color} opacity={scenePreset.rimLight.opacity} side="all" />
            )}
          </ArtworkFrame>
        </div>
      ) : null}

      <div
        style={{
          position: "absolute",
          left: layout.typography.left,
          top: layout.typography.top,
          width: layout.typography.width,
          opacity: metaReveal * globalFade,
          zIndex: 20,
        }}
      >
        <MetadataBlock
          title={cleanText(props.metadata.title, cleanText(props.metadata.sourceFilename, "Untitled"))}
          artist={cleanText(props.metadata.artist, "Unknown Artist")}
          meta={compactMeta([props.metadata.album, props.metadata.year, props.metadata.genre]) || undefined}
          align={layout.typography.align}
          revealFrame={timeline.phase2.startFrame + fps}
          typographyPreset={scenePreset.typographyPreset}
          style={{ color: palette.text, accent: palette.accent }}
        />
      </div>

      <ElementStack
        elements={[
          ...(scenePreset.background || []),
          ...(scenePreset.effects || []),
          ...(scenePreset.lights || []),
        ]}
      />

      <ColorGrade preset={scenePreset.colorGrade} />
      <AtmosphereLayer mode={scenePreset.atmosphere} intensity={1} />
      {scenePreset.halation.enabled && (
        <Halation opacity={scenePreset.halation.opacity} blur={scenePreset.halation.blur} warmth={scenePreset.halation.warmth} />
      )}
      {scenePreset.ambientLight.enabled && (
        <AmbientLight color={scenePreset.ambientLight.color} opacity={scenePreset.ambientLight.opacity} />
      )}
    </AbsoluteFill>
  );
};
