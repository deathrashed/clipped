import { AbsoluteFill, Img, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import type { ClippedRenderProps } from "../types";
import { AudioLayer } from "../components/AudioLayer";
import { ArtworkBackground } from "../artwork/ArtworkBackground";
import { ArtworkFrame } from "../artwork/ArtworkFrame";
import { FallbackArtwork } from "../artwork/FallbackArtwork";
import { MetadataBlock } from "../components/Metadata";
import { ColorGrade, AtmosphereLayer, Halation, AmbientLight, BeatFlash, PostFxStack } from "../effects";
import { SpectrumBars } from "../visualizers";
import { ElementStack } from "../elements";
import { motionFactor, resolvePalette } from "../lib/palette";
import { cleanText, compactMeta } from "../lib/text";
import { resolveScenePreset } from "../presets/scene-presets";
import { useLayout } from "../layouts";
import { useAudioReactive } from "../hooks/useAudioReactive";
import { resolveAssets } from "../template-helpers/templateAssets";
import { useTimeline, easeIn } from "../template-helpers/templateTiming";

export const WaveformStagePro = (props: ClippedRenderProps) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const palette = resolvePalette(props);
  const motion = motionFactor(props.options.motion);
  const scenePreset = resolveScenePreset(props.options.style);
  const layout = useLayout("centered");
  const coverSize = layout.artwork.size * 0.55;
  const audio = useAudioReactive(props.assets.audioSrc, 128, props.options.seed);
  const assets = resolveAssets(props);

  const timeline = useTimeline({ phase1Start: 0, phase2Start: 2, phase3Start: 4.5, outroStart: 1 });

  const waveIn = easeIn(frame, timeline.phase1.startFrame, 20);
  const waveScale = interpolate(waveIn, [0, 1], [0.92, 1]);

  const coverIn = easeIn(frame, timeline.phase2.startFrame, 18);
  const coverY = interpolate(coverIn, [0, 1], [40, 0]);
  const coverScale = 0.88 + coverIn * 0.12;

  const metaReveal = easeIn(frame, timeline.phase3.startFrame, 16);

  const globalFade = frame > durationInFrames - 30
    ? interpolate(frame, [durationInFrames - 30, durationInFrames - 3], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })
    : 1;

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <AudioLayer props={props} />

      <ArtworkBackground src={props.assets.coverSrc} palette={palette} mode="atmospheric" />

      <div style={{ position: "absolute", inset: 0, background: "rgba(0,0,0,0.55)", pointerEvents: "none" }} />

      <div
        style={{
          position: "absolute",
          left: "50%",
          bottom: "50%",
          transform: "translate(-50%, 50%)",
          opacity: waveIn,
          zIndex: 5,
        }}
      >
        <div
          style={{
            width: layout.visualizer.width * 0.9,
            height: layout.width * 0.32,
            transform: `scale(${waveScale})`,
            filter: `drop-shadow(0 0 60px ${palette.accent}44)`,
          }}
        >
          <SpectrumBars
            audio={audio}
            palette={palette}
            count={72}
            width={layout.visualizer.width * 0.9}
            height={layout.width * 0.32}
            mirror={false}
          />
        </div>
      </div>

      {frame >= timeline.phase2.startFrame ? (
        <div
          style={{
            position: "absolute",
            left: "50%",
            top: layout.artwork.cy,
            transform: `translate(-50%, calc(-50% + ${coverY}px)) scale(${coverScale})`,
            opacity: coverIn * globalFade,
            zIndex: 10,
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
          revealFrame={timeline.phase3.startFrame}
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
      <BeatFlash props={props} palette={palette} intensity={0.12} />
      <PostFxStack props={props} palette={palette} grainOpacity={0.06} />
    </AbsoluteFill>
  );
};
