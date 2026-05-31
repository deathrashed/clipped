import { AbsoluteFill, Easing, Img, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import type { ClippedRenderProps } from "../types";
import { AudioLayer } from "../components/AudioLayer";
import { ArtworkBackground } from "../artwork/ArtworkBackground";
import { ArtworkFrame } from "../artwork/ArtworkFrame";
import { FallbackArtwork } from "../artwork/FallbackArtwork";
import { MetadataBlock } from "../components/Metadata";
import { BlurDissolve } from "../transitions/BlurDissolve";
import { ColorGrade, AtmosphereLayer, Halation, AmbientLight, BeatFlash, PostFxStack } from "../effects";
import { ElementStack } from "../elements";
import { motionFactor, resolvePalette } from "../lib/palette";
import { cleanText, compactMeta } from "../lib/text";
import { resolveScenePreset } from "../presets/scene-presets";
import { useLayout } from "../layouts";
import { resolveAssets } from "../template-helpers/templateAssets";
import { useTimeline, easeIn, easeOut } from "../template-helpers/templateTiming";

export const VinylSleevePro = (props: ClippedRenderProps) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const palette = resolvePalette(props);
  const motion = motionFactor(props.options.motion);
  const scenePreset = resolveScenePreset(props.options.style);
  const layout = useLayout("centered");
  const coverSize = layout.artwork.size;
  const artY = layout.artwork.cy - layout.height / 2;
  const assets = resolveAssets(props);

  const timeline = useTimeline({
    phase1Start: 2.5,
    phase2Start: 4.5,
    phase3Start: 7,
    outroStart: 1,
  });

  const sleeveSlide = easeIn(frame, timeline.phase1.startFrame, 20);
  const sleeveX = interpolate(sleeveSlide, [0, 1], [160, 0]);

  const recordScale = spring({ frame: Math.max(0, frame - timeline.phase1.startFrame), fps, config: { damping: 22, stiffness: 70 } });

  const sleeveOut = easeOut(frame, timeline.phase2.endFrame, 15);
  const sleeveOutX = interpolate(sleeveOut, [0, 1], [-120, 0]);

  const coverReveal = easeIn(frame, timeline.phase2.startFrame, 20);

  const metaReveal = easeIn(frame, timeline.phase2.startFrame + fps * 0.5, 18);

  const globalFade = frame > durationInFrames - Math.min(fps, 30)
    ? interpolate(frame, [durationInFrames - 30, durationInFrames - 3], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })
    : 1;

  return (
    <AbsoluteFill style={{ backgroundColor: palette.bg }}>
      <AudioLayer props={props} />

      <ArtworkBackground src={props.assets.coverSrc} palette={palette} mode="atmospheric" />

      <div style={{ position: "absolute", inset: 0, background: "linear-gradient(180deg, rgba(0,0,0,0.4) 0%, rgba(0,0,0,0.05) 40%, rgba(0,0,0,0.05) 60%, rgba(0,0,0,0.6) 100%)", pointerEvents: "none" }} />

      {assets.hasLogo && frame < timeline.phase1.endFrame ? (
        <div
          style={{
            position: "absolute",
            left: "50%",
            top: layout.logo.top,
            width: layout.logo.width,
            maxHeight: layout.height * 0.2,
            transform: "translate(-50%, 0)",
            opacity: interpolate(frame, [0, fps * 0.6, timeline.phase1.endFrame - fps * 0.6, timeline.phase1.endFrame], [0, 1, 1, 0]),
            zIndex: 20,
          }}
        >
          <Img src={assets.logoSrc!} style={{ width: "100%", height: "100%", objectFit: "contain" }} />
        </div>
      ) : null}

      {frame < timeline.phase2.endFrame ? (
        <div
          style={{
            position: "absolute",
            left: "50%",
            top: "50%",
            width: coverSize,
            height: coverSize,
            transform: `translate(calc(-50% + ${sleeveOutX}px), calc(-50% + ${artY}px)) translateX(${sleeveX}px)`,
            zIndex: 10,
            opacity: sleeveOut,
          }}
        >
          <ArtworkFrame size={coverSize} preset="matte">
            {assets.hasCover ? (
              <Img src={assets.coverSrc!} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
            ) : (
              <FallbackArtwork size={coverSize} palette={palette} seed={props.metadata.title} />
            )}
          </ArtworkFrame>
        </div>
      ) : null}

      <div
        style={{
          position: "absolute",
          left: "50%",
          top: "50%",
          width: coverSize,
          height: coverSize,
          transform: `translate(-50%, calc(-50% + ${artY}px)) scale(${0.5 + recordScale * 0.5})`,
          opacity: easeIn(frame, timeline.phase1.startFrame, 12) * (1 - easeIn(frame, timeline.phase2.startFrame - 10, 12)),
          zIndex: 8,
          borderRadius: "50%",
          overflow: "hidden",
          border: `4px solid ${palette.border}`,
          backgroundColor: palette.panel,
        }}
      >
        {assets.hasCover ? (
          <Img src={assets.coverSrc!} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
        ) : (
          <FallbackArtwork size={coverSize} palette={palette} seed={props.metadata.title} />
        )}
        <div
          style={{
            position: "absolute",
            inset: "36%",
            borderRadius: "50%",
            background: palette.bg,
            border: `3px solid ${palette.border}`,
            boxShadow: `inset 0 0 30px rgba(0,0,0,0.5)`,
          }}
        />
      </div>

      {frame >= timeline.phase2.startFrame ? (
        <div
          style={{
            position: "absolute",
            left: "50%",
            top: "50%",
            transform: `translate(-50%, calc(-50% + ${artY}px)) scale(${0.88 + coverReveal * 0.12})`,
            opacity: coverReveal * globalFade,
            zIndex: 12,
          }}
        >
          <BlurDissolve progress={0.4 + coverReveal * 0.6} maxBlur={18}>
            <ArtworkFrame size={coverSize} preset="matte">
              {assets.hasCover ? (
                <Img src={assets.coverSrc!} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
              ) : (
                <FallbackArtwork size={coverSize} palette={palette} seed={props.metadata.title} />
              )}
            </ArtworkFrame>
          </BlurDissolve>
        </div>
      ) : null}

      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: layout.typography.top,
          display: "flex",
          justifyContent: "center",
          opacity: metaReveal * globalFade,
          zIndex: 20,
        }}
      >
        <MetadataBlock
          title={cleanText(props.metadata.title, cleanText(props.metadata.sourceFilename, "Untitled"))}
          artist={cleanText(props.metadata.artist, "Unknown Artist")}
          meta={compactMeta([props.metadata.album, props.metadata.year, props.metadata.genre]) || undefined}
          align="center"
          revealFrame={timeline.phase2.startFrame + fps}
          typographyPreset={scenePreset.typographyPreset}
          style={{ maxWidth: layout.width * 0.84, color: palette.text, accent: palette.accent }}
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
      <BeatFlash props={props} palette={palette} intensity={0.08} />
      <PostFxStack props={props} palette={palette} grainOpacity={0.06} />
    </AbsoluteFill>
  );
};
