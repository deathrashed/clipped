import { AbsoluteFill, Img, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import type { ClippedRenderProps } from "../types";
import { AudioLayer } from "../components/AudioLayer";
import { ArtworkBackground } from "../artwork/ArtworkBackground";
import { ArtworkFrame } from "../artwork/ArtworkFrame";
import { FallbackArtwork } from "../artwork/FallbackArtwork";
import { MetadataBlock } from "../components/Metadata";
import { PulseRings, SpectrumBars } from "../visualizers";
import { ColorGrade, AtmosphereLayer, BeatFlash } from "../effects";
import { ElementStack } from "../elements";
import { resolvePalette, motionFactor } from "../lib/palette";
import { cleanText, compactMeta } from "../lib/text";
import { resolveScenePreset } from "../presets/scene-presets";
import { useLayout } from "../layouts";
import { useAudioReactive } from "../hooks/useAudioReactive";
import { resolveAssets } from "../template-helpers/templateAssets";
import { useTimeline, easeIn } from "../template-helpers/templateTiming";

export const SpinnerPro = (props: ClippedRenderProps) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const palette = resolvePalette(props);
  const motion = motionFactor(props.options.motion);
  const scenePreset = resolveScenePreset("spinner");
  const layout = useLayout("centered");
  const coverSize = layout.artwork.size * 0.48;
  const audio = useAudioReactive(props.assets.audioSrc, 128, props.options.seed);
  const assets = resolveAssets(props);

  const timeline = useTimeline({ phase1Start: 0.5, phase2Start: 2, phase3Start: 4, outroStart: 1 });

  const rotation = interpolate(frame, [0, durationInFrames], [0, 360 * (3 + motion * 2)]);

  const spinReveal = easeIn(frame, timeline.phase1.startFrame, 18);

  const metaReveal = easeIn(frame, timeline.phase3.startFrame, 16);

  const speedUp = 1 + audio.bass * 0.5;
  const wobble = audio.bass * 8 * motion;

  const globalFade = frame > durationInFrames - 30
    ? interpolate(frame, [durationInFrames - 30, durationInFrames - 3], [1, 0])
    : 1;

  return (
    <AbsoluteFill style={{ backgroundColor: palette.bg }}>
      <AudioLayer props={props} />
      <ArtworkBackground src={props.assets.coverSrc} palette={palette} mode="atmospheric" />
      <div style={{ position: "absolute", inset: 0, background: "rgba(0,0,0,0.3)", pointerEvents: "none" }} />

      <div
        style={{
          position: "absolute",
          left: "50%",
          top: "50%",
          transform: `translate(-50%, -50%)`,
          width: coverSize * 1.6,
          height: coverSize * 1.6,
          borderRadius: "50%",
          background: `conic-gradient(${palette.accent}, ${palette.accent2 || palette.accent}, transparent, ${palette.accent})`,
          opacity: 0.15 * globalFade,
        }}
      />

      <div
        style={{
          position: "absolute",
          left: "50%",
          top: "50%",
          width: coverSize * 1.35,
          height: coverSize * 1.35,
          borderRadius: "50%",
          border: `2px solid ${palette.accent}`,
          transform: `translate(-50%, -50%) rotate(${rotation * 0.7 * speedUp}deg)`,
          opacity: (0.3 + audio.mid * 0.2) * globalFade,
        }}
      />

      <div
        style={{
          position: "absolute",
          left: "50%",
          top: "50%",
          transform: `translate(-50%, -50%) rotate(${rotation * speedUp}deg)`,
          opacity: spinReveal * globalFade,
          zIndex: 10,
          borderRadius: "50%",
          overflow: "hidden",
          width: coverSize,
          height: coverSize,
          boxShadow: `0 10px 50px rgba(0,0,0,0.5), 0 0 ${40 + wobble}px ${palette.accent}44`,
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

      <PulseRings audio={audio} palette={palette} ringCount={3} size={coverSize * 1.5} />

      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          bottom: layout.visualizer.bottom + 70,
          display: "flex",
          justifyContent: "center",
          opacity: metaReveal * globalFade,
          zIndex: 20,
        }}
      >
        <MetadataBlock
          title={cleanText(props.metadata.title, "Untitled")}
          artist={cleanText(props.metadata.artist, "Unknown Artist")}
          meta={compactMeta([props.metadata.year, props.metadata.genre]) || undefined}
          align="center"
          revealFrame={timeline.phase3.startFrame}
          typographyPreset={scenePreset.typographyPreset}
          style={{ color: palette.text, accent: palette.accent }}
        />
      </div>

      <ElementStack elements={[...(scenePreset.background || []), ...(scenePreset.effects || []), ...(scenePreset.lights || [])]} />
      <ColorGrade preset={scenePreset.colorGrade} />
      <AtmosphereLayer mode={scenePreset.atmosphere} intensity={1} />
      <BeatFlash props={props} palette={palette} intensity={0.12} />
    </AbsoluteFill>
  );
};
