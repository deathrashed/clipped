import { AbsoluteFill, Img, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import type { ClippedRenderProps } from "../types";
import { AudioLayer } from "../components/AudioLayer";
import { ArtworkBackground } from "../artwork/ArtworkBackground";
import { ArtworkFrame } from "../artwork/ArtworkFrame";
import { FallbackArtwork } from "../artwork/FallbackArtwork";
import { MetadataBlock } from "../components/Metadata";
import { RadialBars, PulseRings } from "../visualizers";
import { ColorGrade, AtmosphereLayer, BeatFlash, PostFxStack } from "../effects";
import { ElementStack } from "../elements";
import { cleanText, compactMeta } from "../lib/text";
import { resolvePalette, motionFactor } from "../lib/palette";
import { resolveScenePreset } from "../presets/scene-presets";
import { useLayout } from "../layouts";
import { useAudioReactive } from "../hooks/useAudioReactive";
import { resolveAssets } from "../template-helpers/templateAssets";
import { useTimeline, easeIn } from "../template-helpers/templateTiming";
import { resolveGenrePalette } from "../template-helpers/genrePalettes";

export const AudioOrb = (props: ClippedRenderProps) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const palette = resolvePalette(props);
  const motion = motionFactor(props.options.motion);
  const scenePreset = resolveScenePreset("ambient");
  const layout = useLayout("centered");
  const coverSize = layout.artwork.size * 0.4;
  const coverY = layout.artwork.cy - layout.height / 2;
  const audio = useAudioReactive(props.assets.audioSrc, 128, props.options.seed);
  const assets = resolveAssets(props);
  const genrePalette = resolveGenrePalette(props.metadata.genre);

  const timeline = useTimeline({ phase1Start: 0.5, phase2Start: 2, phase3Start: 4, outroStart: 1 });

  const orbReveal = easeIn(frame, timeline.phase1.startFrame, 22);

  const coverReveal = easeIn(frame, timeline.phase2.startFrame, 18);

  const metaReveal = easeIn(frame, timeline.phase3.startFrame, 16);

  const orbScale = 1 + audio.bass * 0.3 + audio.mid * 0.15;
  const orbOpacity = 0.3 + audio.bass * 0.4;

  const globalFade = frame > durationInFrames - 30
    ? interpolate(frame, [durationInFrames - 30, durationInFrames - 3], [1, 0])
    : 1;

  return (
    <AbsoluteFill style={{ backgroundColor: genrePalette.bg }}>
      <AudioLayer props={props} />
      <ArtworkBackground src={props.assets.coverSrc} palette={palette} mode="atmospheric" />

      <div
        style={{
          position: "absolute",
          left: "50%",
          top: "50%",
          transform: `translate(-50%, calc(-50% + ${coverY * 0.5}px)) scale(${orbScale})`,
          width: layout.width * 0.6,
          height: layout.width * 0.6,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${genrePalette.glow}44 0%, ${genrePalette.accent}11 40%, transparent 65%)`,
          opacity: orbReveal * orbOpacity * globalFade,
          filter: "blur(40px)",
          zIndex: 3,
        }}
      />

      <PulseRings audio={audio} palette={{ ...palette, accent: genrePalette.accent }} ringCount={3} size={layout.width * 0.55} />

      {frame >= timeline.phase2.startFrame ? (
        <div
          style={{
            position: "absolute",
            left: "50%",
            top: "50%",
            transform: `translate(-50%, calc(-50% + ${coverY * 0.5}px))`,
            opacity: coverReveal * globalFade,
            zIndex: 10,
            borderRadius: "50%",
            overflow: "hidden",
            width: coverSize,
            height: coverSize,
            boxShadow: `0 0 60px ${genrePalette.glow}44`,
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
          title={cleanText(props.metadata.title, "Untitled")}
          artist={cleanText(props.metadata.artist, "Unknown Artist")}
          meta={compactMeta([props.metadata.album, props.metadata.year]) || undefined}
          align="center"
          revealFrame={timeline.phase3.startFrame}
          typographyPreset="minimal"
          style={{ color: palette.text, accent: genrePalette.accent }}
        />
      </div>

      <ElementStack elements={[...(scenePreset.background || []), ...(scenePreset.effects || []), ...(scenePreset.lights || [])]} />
      <ColorGrade preset={scenePreset.colorGrade} />
      <AtmosphereLayer mode={scenePreset.atmosphere} intensity={0.6} />
      <BeatFlash props={props} palette={palette} intensity={0.06} />
      <PostFxStack props={props} palette={palette} grainOpacity={0.04} />
    </AbsoluteFill>
  );
};
