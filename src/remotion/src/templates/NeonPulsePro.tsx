import { AbsoluteFill, Img, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import type { ClippedRenderProps } from "../types";
import { AudioLayer } from "../components/AudioLayer";
import { ArtworkBackground } from "../artwork/ArtworkBackground";
import { ArtworkFrame } from "../artwork/ArtworkFrame";
import { FallbackArtwork } from "../artwork/FallbackArtwork";
import { MetadataBlock } from "../components/Metadata";
import { SpectrumBars } from "../visualizers";
import { ColorGrade, AtmosphereLayer, Halation, AmbientLight, BeatFlash, PostFxStack } from "../effects";
import { ElementStack } from "../elements";
import { resolvePalette, motionFactor } from "../lib/palette";
import { cleanText, compactMeta } from "../lib/text";
import { resolveScenePreset } from "../presets/scene-presets";
import { useLayout } from "../layouts";
import { useAudioReactive } from "../hooks/useAudioReactive";
import { resolveAssets } from "../template-helpers/templateAssets";
import { useTimeline, easeIn } from "../template-helpers/templateTiming";
import { resolveGenrePalette } from "../template-helpers/genrePalettes";

export const NeonPulsePro = (props: ClippedRenderProps) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const palette = resolvePalette(props);
  const motion = motionFactor(props.options.motion);
  const scenePreset = resolveScenePreset("neon");
  const layout = useLayout("centered");
  const coverSize = layout.artwork.size;
  const artY = layout.artwork.cy - layout.height / 2;
  const audio = useAudioReactive(props.assets.audioSrc, 128, props.options.seed);
  const assets = resolveAssets(props);
  const genrePalette = resolveGenrePalette(props.metadata.genre);

  const timeline = useTimeline({ phase1Start: 1.5, phase2Start: 3.5, phase3Start: 5.5, outroStart: 1 });

  const logoIn = easeIn(frame, 5, 18);

  const glowPulse = interpolate(
    Math.sin(frame / 12 * motion + audio.bass * 3),
    [-1, 1],
    [0.7, 1.2],
  );

  const coverReveal = easeIn(frame, timeline.phase2.startFrame, 20);
  const coverScale = 0.85 + coverReveal * 0.15;

  const metaReveal = easeIn(frame, timeline.phase3.startFrame, 16);

  const globalFade = frame > durationInFrames - 30
    ? interpolate(frame, [durationInFrames - 30, durationInFrames - 3], [1, 0])
    : 1;

  return (
    <AbsoluteFill style={{ backgroundColor: genrePalette.bg }}>
      <AudioLayer props={props} />
      <ArtworkBackground src={props.assets.coverSrc} palette={palette} mode="atmospheric" />
      <div style={{ position: "absolute", inset: 0, background: "rgba(0,0,0,0.4)", pointerEvents: "none" }} />

      <div
        style={{
          position: "absolute",
          left: "50%",
          top: "50%",
          width: coverSize * 1.1,
          height: coverSize * 1.1,
          transform: `translate(-50%, calc(-50% + ${artY}px)) scale(${glowPulse})`,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${genrePalette.glow}, transparent 70%)`,
          opacity: 0.6 + audio.bass * 0.3,
        }}
      />

      {frame >= timeline.phase2.startFrame ? (
        <div
          style={{
            position: "absolute",
            left: "50%",
            top: "50%",
            transform: `translate(-50%, calc(-50% + ${artY}px)) scale(${coverScale})`,
            opacity: coverReveal * globalFade,
            zIndex: 10,
            boxShadow: `0 0 ${60 + audio.bass * 60}px ${genrePalette.glow}`,
            borderRadius: 18,
            overflow: "hidden",
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

      {props.options.waveform !== "none" ? (
        <div
          style={{
            position: "absolute",
            left: "50%",
            bottom: layout.height - layout.visualizer.bottom + 20,
            transform: "translateX(-50%)",
            opacity: globalFade,
          }}
        >
          <SpectrumBars
            audio={audio}
            palette={{ ...palette, accent: genrePalette.accent }}
            count={48}
            width={layout.visualizer.width}
            height={80}
            mirror={props.options.waveform === "mirror"}
          />
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
          style={{ maxWidth: layout.width * 0.84, color: palette.text, accent: genrePalette.accent }}
        />
      </div>

      <ElementStack elements={[...(scenePreset.background || []), ...(scenePreset.effects || []), ...(scenePreset.lights || [])]} />
      <ColorGrade preset={scenePreset.colorGrade} />
      <AtmosphereLayer mode={scenePreset.atmosphere} intensity={1} />
      <BeatFlash props={props} palette={palette} intensity={0.18} />
      <PostFxStack props={props} palette={palette} grainOpacity={0.05} />
    </AbsoluteFill>
  );
};
