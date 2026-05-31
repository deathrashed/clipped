import { AbsoluteFill, Img, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import type { ClippedRenderProps } from "../types";
import { AudioLayer } from "../components/AudioLayer";
import { ArtworkBackground } from "../artwork/ArtworkBackground";
import { ArtworkFrame } from "../artwork/ArtworkFrame";
import { FallbackArtwork } from "../artwork/FallbackArtwork";
import { MetadataBlock } from "../components/Metadata";
import { ColorGrade, AtmosphereLayer, Halation, AmbientLight, BeatFlash, FilmGrain } from "../effects";
import { ElementStack } from "../elements";
import { resolvePalette, motionFactor } from "../lib/palette";
import { cleanText, compactMeta } from "../lib/text";
import { resolveScenePreset } from "../presets/scene-presets";
import { useLayout } from "../layouts";
import { resolveAssets } from "../template-helpers/templateAssets";
import { useTimeline, easeIn } from "../template-helpers/templateTiming";

export const ConcertPosterPro = (props: ClippedRenderProps) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const palette = resolvePalette(props);
  const motion = motionFactor(props.options.motion);
  const scenePreset = resolveScenePreset("concert");
  const layout = useLayout("editorial-left");
  const coverSize = layout.artwork.size * 0.7;
  const assets = resolveAssets(props);

  const timeline = useTimeline({ phase1Start: 0.5, phase2Start: 2.5, phase3Start: 4.5, outroStart: 1 });

  const titleSlide = easeIn(frame, timeline.phase1.startFrame, 22);
  const titleX = interpolate(titleSlide, [0, 1], [-60, 0]);

  const coverReveal = easeIn(frame, timeline.phase2.startFrame, 18);

  const metaReveal = easeIn(frame, timeline.phase3.startFrame, 16);

  const globalFade = frame > durationInFrames - 30
    ? interpolate(frame, [durationInFrames - 30, durationInFrames - 3], [1, 0])
    : 1;

  return (
    <AbsoluteFill style={{ backgroundColor: palette.bg }}>
      <AudioLayer props={props} />
      <ArtworkBackground src={props.assets.coverSrc} palette={palette} mode="atmospheric" />

      <div
        style={{
          position: "absolute",
          left: layout.safe.left,
          top: layout.height * 0.12,
          opacity: titleSlide * globalFade,
          transform: `translateX(${titleX}px)`,
          zIndex: 20,
        }}
      >
        <div
          style={{
            fontSize: 48,
            fontWeight: 900,
            letterSpacing: 8,
            textTransform: "uppercase",
            color: palette.text,
            fontFamily: "Impact, Haettenschweiler, Arial Black, sans-serif",
            textShadow: `4px 4px 0 ${palette.accent}`,
            marginBottom: 8,
            lineHeight: 1,
          }}
        >
          {cleanText(props.metadata.artist, "Unknown Artist").toUpperCase()}
        </div>
        <div
          style={{
            fontSize: 36,
            fontWeight: 700,
            color: palette.accent,
            fontStyle: "italic",
            fontFamily: "Georgia, serif",
            lineHeight: 1.1,
          }}
        >
          {cleanText(props.metadata.title, "Untitled")}
        </div>
      </div>

      {frame >= timeline.phase2.startFrame ? (
        <div
          style={{
            position: "absolute",
            left: layout.width - layout.safe.right - coverSize - 20,
            top: "50%",
            transform: "translateY(-50%)",
            opacity: coverReveal * globalFade,
            zIndex: 10,
            boxShadow: `-8px 8px 0 ${palette.accent}`,
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

      {assets.hasLogo ? (
        <div
          style={{
            position: "absolute",
            right: layout.safe.right,
            top: layout.height * 0.12,
            opacity: easeIn(frame, timeline.phase2.startFrame, 14) * globalFade,
          }}
        >
          <Img src={assets.logoSrc!} style={{ maxWidth: 120, maxHeight: 80, objectFit: "contain" }} />
        </div>
      ) : null}

      <div
        style={{
          position: "absolute",
          left: layout.safe.left,
          top: layout.height * 0.65,
          opacity: metaReveal * globalFade,
          zIndex: 20,
        }}
      >
        <MetadataBlock
          title={cleanText(props.metadata.title, "Untitled")}
          artist={cleanText(props.metadata.artist, "Unknown Artist")}
          meta={compactMeta([props.metadata.album, props.metadata.year]) || undefined}
          align="left"
          revealFrame={timeline.phase3.startFrame}
          typographyPreset={scenePreset.typographyPreset}
          style={{ color: palette.text, accent: palette.accent }}
        />
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
      <FilmGrain opacity={0.06} cells={150} />
    </AbsoluteFill>
  );
};
