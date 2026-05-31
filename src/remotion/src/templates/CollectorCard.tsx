import { AbsoluteFill, Img, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import type { ClippedRenderProps } from "../types";
import { AudioLayer } from "../components/AudioLayer";
import { ArtworkBackground } from "../artwork/ArtworkBackground";
import { ArtworkFrame } from "../artwork/ArtworkFrame";
import { FallbackArtwork } from "../artwork/FallbackArtwork";
import { MetadataBlock } from "../components/Metadata";
import { SpectrumBars } from "../visualizers";
import { ColorGrade, AtmosphereLayer, Halation, AmbientLight, BeatFlash, FilmGrain, Vignette } from "../effects";
import { ElementStack } from "../elements";
import { resolvePalette, motionFactor } from "../lib/palette";
import { cleanText, compactMeta } from "../lib/text";
import { resolveScenePreset } from "../presets/scene-presets";
import { useLayout } from "../layouts";
import { resolveAssets } from "../template-helpers/templateAssets";
import { useTimeline, easeIn } from "../template-helpers/templateTiming";

export const CollectorCard = (props: ClippedRenderProps) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const palette = resolvePalette(props);
  const motion = motionFactor(props.options.motion);
  const scenePreset = resolveScenePreset("collector");
  const layout = useLayout("centered");
  const coverSize = layout.artwork.size * 0.35;
  const coverY = layout.artwork.cy - layout.height / 2 - coverSize * 0.35;
  const assets = resolveAssets(props);

  const timeline = useTimeline({ phase1Start: 0.3, phase2Start: 1.5, phase3Start: 3, outroStart: 1 });

  const cardSlide = spring({
    frame: Math.max(0, frame - timeline.phase1.startFrame),
    fps,
    config: { damping: 16, stiffness: 100 },
  });
  const cardY = interpolate(cardSlide, [0, 1], [60, 0]);

  const logoReveal = easeIn(frame, timeline.phase1.startFrame + 3, 14);
  const logoOpacity = interpolate(
    frame,
    [timeline.phase1.startFrame + 3, timeline.phase1.startFrame + 17, timeline.phase3.startFrame - 15, timeline.phase3.startFrame],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  const coverReveal = easeIn(frame, timeline.phase1.startFrame + 8, 16);

  const metaReveal = easeIn(frame, timeline.phase2.startFrame, 18);

  const labelReveal = easeIn(frame, timeline.phase3.startFrame, 14);

  const globalFade = frame > durationInFrames - 30
    ? interpolate(frame, [durationInFrames - 30, durationInFrames - 3], [1, 0])
    : 1;

  return (
    <AbsoluteFill style={{ backgroundColor: "#0a0a0a" }}>
      <AudioLayer props={props} />
      <ArtworkBackground src={props.assets.coverSrc} palette={palette} mode="atmospheric" />
      <div style={{ position: "absolute", inset: 0, background: "rgba(0,0,0,0.35)", pointerEvents: "none" }} />

      <div
        style={{
          position: "absolute",
          left: "50%",
          top: "50%",
          width: layout.width * 0.62,
          height: layout.height * 0.7,
          borderRadius: 20,
          background: `linear-gradient(180deg, ${palette.panel}cc, ${palette.bg}ee)`,
          border: `1px solid ${palette.border}44`,
          boxShadow: `0 20px 80px rgba(0,0,0,0.6)`,
          opacity: cardSlide * globalFade,
          transform: `translate(-50%, calc(-50% + ${cardY}px))`,
          zIndex: 5,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          padding: "30px 20px",
          overflow: "hidden",
        }}
      >
        {assets.hasLogo && logoOpacity > 0 ? (
          <div
            style={{
              opacity: logoOpacity,
              marginBottom: 16,
              height: 48,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <Img
              src={assets.logoSrc!}
              style={{
                maxWidth: layout.width * 0.4,
                maxHeight: 48,
                objectFit: "contain",
                filter: "drop-shadow(0 4px 12px rgba(0,0,0,0.4))",
              }}
            />
          </div>
        ) : null}

        <div
          style={{
            width: coverSize,
            height: coverSize,
            borderRadius: 14,
            overflow: "hidden",
            opacity: coverReveal,
            boxShadow: `0 8px 30px rgba(0,0,0,0.5)`,
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

        <div style={{ opacity: metaReveal, marginTop: 20, textAlign: "center" }}>
          <MetadataBlock
            title={cleanText(props.metadata.title, "Untitled")}
            artist={cleanText(props.metadata.artist, "Unknown Artist")}
            meta={compactMeta([props.metadata.year, props.metadata.genre, props.metadata.album]) || undefined}
            align="center"
            revealFrame={timeline.phase2.startFrame}
            typographyPreset="editorial"
            style={{ color: palette.text, accent: palette.accent }}
          />
        </div>

        {props.metadata.album ? (
          <div
            style={{
              marginTop: 10,
              opacity: labelReveal,
              fontSize: 12,
              letterSpacing: 3,
              textTransform: "uppercase",
              color: palette.muted,
              fontFamily: "Helvetica, Arial, sans-serif",
            }}
          >
            {props.metadata.album}
          </div>
        ) : null}
      </div>

      <ElementStack elements={[...(scenePreset.background || []), ...(scenePreset.effects || []), ...(scenePreset.lights || [])]} />
      <ColorGrade preset={scenePreset.colorGrade} />
      <AtmosphereLayer mode={scenePreset.atmosphere} intensity={0.7} />
      {scenePreset.halation.enabled && <Halation opacity={scenePreset.halation.opacity} blur={scenePreset.halation.blur} warmth={scenePreset.halation.warmth} />}
      {scenePreset.ambientLight.enabled && <AmbientLight color={scenePreset.ambientLight.color} opacity={scenePreset.ambientLight.opacity} />}
      <Vignette opacity={0.4} />
      <BeatFlash props={props} palette={palette} intensity={0.06} />
    </AbsoluteFill>
  );
};
