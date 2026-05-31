import { AbsoluteFill, Img, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import type { ClippedRenderProps } from "../types";
import { AudioLayer } from "../components/AudioLayer";
import { ArtworkBackground } from "../artwork/ArtworkBackground";
import { ArtworkFrame } from "../artwork/ArtworkFrame";
import { FallbackArtwork } from "../artwork/FallbackArtwork";
import { MetadataBlock } from "../components/Metadata";
import { ColorGrade, AtmosphereLayer, Halation, AmbientLight, BeatFlash, PostFxStack } from "../effects";
import { ElementStack } from "../elements";
import { resolvePalette, motionFactor } from "../lib/palette";
import { cleanText, compactMeta } from "../lib/text";
import { resolveScenePreset } from "../presets/scene-presets";
import { useLayout } from "../layouts";
import { resolveAssets } from "../template-helpers/templateAssets";
import { useTimeline, easeIn } from "../template-helpers/templateTiming";

export const GlassCardPro = (props: ClippedRenderProps) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const palette = resolvePalette(props);
  const motion = motionFactor(props.options.motion);
  const scenePreset = resolveScenePreset(props.options.style);
  const layout = useLayout("centered");
  const coverSize = layout.artwork.size * 0.55;
  const assets = resolveAssets(props);

  const timeline = useTimeline({ phase1Start: 0.5, phase2Start: 2, phase3Start: 4, outroStart: 1 });

  const coverReveal = easeIn(frame, timeline.phase1.startFrame + 10, 20);
  const coverY = interpolate(coverReveal, [0, 1], [30, 0]);

  const cardIn = easeIn(frame, timeline.phase1.startFrame + 5, 18);
  const cardOpacity = interpolate(cardIn, [0, 1], [0, 1]);

  const metaReveal = easeIn(frame, timeline.phase2.startFrame, 16);

  const globalFade = frame > durationInFrames - 30
    ? interpolate(frame, [durationInFrames - 30, durationInFrames - 3], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })
    : 1;

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <AudioLayer props={props} />
      <ArtworkBackground src={props.assets.coverSrc} palette={palette} mode="atmospheric" />
      <div style={{ position: "absolute", inset: 0, background: "rgba(0,0,0,0.3)", pointerEvents: "none" }} />

      <div
        style={{
          position: "absolute",
          left: "50%",
          top: "50%",
          transform: "translate(-50%, -50%)",
          width: layout.width * 0.78,
          height: layout.height * 0.48,
          borderRadius: 28,
          background: `linear-gradient(135deg, ${palette.panel}, rgba(255,255,255,0.05))`,
          backdropFilter: "blur(20px)",
          border: `1px solid rgba(255,255,255,0.12)`,
          boxShadow: `0 30px 80px rgba(0,0,0,0.5)`,
          opacity: cardOpacity * globalFade,
          zIndex: 5,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          gap: 20,
        }}
      >
        <div
          style={{
            width: coverSize,
            height: coverSize,
            borderRadius: 18,
            overflow: "hidden",
            boxShadow: `0 10px 40px rgba(0,0,0,0.5)`,
            transform: `translateY(${coverY}px)`,
            opacity: coverReveal,
          }}
        >
          <ArtworkFrame size={coverSize} preset="none">
            {assets.hasCover ? (
              <Img src={assets.coverSrc!} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
            ) : (
              <FallbackArtwork size={coverSize} palette={palette} seed={props.metadata.title} />
            )}
          </ArtworkFrame>
        </div>

        {assets.hasLogo ? (
          <div style={{ opacity: easeIn(frame, timeline.phase2.startFrame, 12) }}>
            <Img src={assets.logoSrc!} style={{ maxWidth: layout.width * 0.5, maxHeight: 60, objectFit: "contain" }} />
          </div>
        ) : null}

        <div style={{ opacity: metaReveal }}>
          <MetadataBlock
            title={cleanText(props.metadata.title, cleanText(props.metadata.sourceFilename, "Untitled"))}
            artist={cleanText(props.metadata.artist, "Unknown Artist")}
            meta={compactMeta([props.metadata.year, props.metadata.genre]) || undefined}
            align="center"
            revealFrame={timeline.phase2.startFrame}
            typographyPreset={scenePreset.typographyPreset}
            style={{ color: palette.text, accent: palette.accent }}
          />
        </div>
      </div>

      <ElementStack elements={[...(scenePreset.background || []), ...(scenePreset.effects || []), ...(scenePreset.lights || [])]} />
      <ColorGrade preset={scenePreset.colorGrade} />
      <AtmosphereLayer mode={scenePreset.atmosphere} intensity={1} />
      {scenePreset.halation.enabled && (
        <Halation opacity={scenePreset.halation.opacity} blur={scenePreset.halation.blur} warmth={scenePreset.halation.warmth} />
      )}
      {scenePreset.ambientLight.enabled && (
        <AmbientLight color={scenePreset.ambientLight.color} opacity={scenePreset.ambientLight.opacity} />
      )}
      <BeatFlash props={props} palette={palette} intensity={0.06} />
    </AbsoluteFill>
  );
};
