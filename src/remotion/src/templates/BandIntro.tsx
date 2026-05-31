import { AbsoluteFill, Img, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import type { ClippedRenderProps } from "../types";
import { AudioLayer } from "../components/AudioLayer";
import { ArtworkBackground } from "../artwork/ArtworkBackground";
import { ArtworkFrame } from "../artwork/ArtworkFrame";
import { FallbackArtwork } from "../artwork/FallbackArtwork";
import { MetadataBlock } from "../components/Metadata";
import { ColorGrade, AtmosphereLayer, Halation, AmbientLight, BeatFlash, FilmGrain, Vignette } from "../effects";
import { ElementStack } from "../elements";
import { resolvePalette, motionFactor } from "../lib/palette";
import { cleanText, compactMeta } from "../lib/text";
import { resolveScenePreset } from "../presets/scene-presets";
import { useLayout } from "../layouts";
import { useAudioReactive } from "../hooks/useAudioReactive";
import { resolveAssets } from "../template-helpers/templateAssets";
import { useTimeline, easeIn } from "../template-helpers/templateTiming";

export const BandIntro = (props: ClippedRenderProps) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const palette = resolvePalette(props);
  const motion = motionFactor(props.options.motion);
  const scenePreset = resolveScenePreset("band-intro");
  const layout = useLayout("editorial-left");
  const coverSize = layout.artwork.size * 0.5;
  const audio = useAudioReactive(props.assets.audioSrc, 128, props.options.seed);
  const assets = resolveAssets(props);

  const timeline = useTimeline({ phase1Start: 0.5, phase2Start: 2, phase3Start: 4, outroStart: 1 });

  const artistIn = easeIn(frame, timeline.phase1.startFrame, 24);

  const logoReveal = easeIn(frame, 5, 18);
  const logoFade = interpolate(
    frame,
    [timeline.phase1.endFrame - 15, timeline.phase1.endFrame],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );
  const logoOpacity = Math.min(logoReveal, logoFade);

  const coverSlide = spring({
    frame: Math.max(0, frame - timeline.phase2.startFrame),
    fps,
    config: { damping: 12, stiffness: 90 },
  });

  const metaReveal = easeIn(frame, timeline.phase3.startFrame, 18);

  const globalFade = frame > durationInFrames - 30
    ? interpolate(frame, [durationInFrames - 30, durationInFrames - 3], [1, 0])
    : 1;

  return (
    <AbsoluteFill style={{ backgroundColor: "#050505" }}>
      <AudioLayer props={props} />

      <ArtworkBackground src={props.assets.coverSrc} palette={palette} mode="atmospheric" />

      {assets.hasArtistImage ? (
        <div
          style={{
            position: "absolute",
            inset: 0,
            opacity: 0.35,
            zIndex: 5,
          }}
        >
          <Img
            src={assets.artistImageSrc!}
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
          />
        </div>
      ) : null}

      <div style={{ position: "absolute", inset: 0, background: "linear-gradient(to right, rgba(0,0,0,0.85), rgba(0,0,0,0.4))", zIndex: 6, pointerEvents: "none" }} />

      {assets.hasLogo && logoOpacity > 0 ? (
        <div
          style={{
            position: "absolute",
            left: layout.safe.left + 30,
            top: layout.safe.top + 20,
            zIndex: 11,
            opacity: logoOpacity * globalFade,
            maxWidth: 240,
          }}
        >
          <Img
            src={assets.logoSrc!}
            style={{
              width: "100%",
              height: "auto",
              maxHeight: 80,
              objectFit: "contain",
              filter: "drop-shadow(0 4px 12px rgba(0,0,0,0.6))",
            }}
          />
        </div>
      ) : null}

      <div
        style={{
          position: "absolute",
          left: layout.safe.left + 30,
          top: "50%",
          transform: "translateY(-70%)",
          zIndex: 10,
          opacity: artistIn * globalFade,
          maxWidth: layout.width * 0.5,
        }}
      >
        <div
          style={{
            fontSize: 52,
            fontWeight: 900,
            letterSpacing: 6,
            color: palette.text,
            fontFamily: "Impact, Haettenschweiler, sans-serif",
            textShadow: `0 4px 12px ${palette.accent}88`,
            lineHeight: 1,
            marginBottom: 8,
          }}
        >
          {cleanText(props.metadata.artist, "Unknown Artist").toUpperCase()}
        </div>

        <div
          style={{
            fontSize: 14,
            letterSpacing: 4,
            color: palette.muted,
            textTransform: "uppercase",
            fontFamily: "Helvetica, Arial, sans-serif",
          }}
        >
          {props.metadata.genre || "Various"}
        </div>
      </div>

      {frame >= timeline.phase2.startFrame ? (
        <div
          style={{
            position: "absolute",
            left: layout.safe.left + 30,
            top: "50%",
            transform: `translateY(-10%)`,
            opacity: coverSlide * globalFade,
            zIndex: 10,
            display: "flex",
            alignItems: "center",
            gap: 30,
          }}
        >
          <ArtworkFrame size={coverSize} preset="none">
            {assets.hasCover ? (
              <Img src={assets.coverSrc!} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
            ) : (
              <FallbackArtwork size={coverSize} palette={palette} seed={props.metadata.title} />
            )}
          </ArtworkFrame>

          <div style={{ opacity: metaReveal }}>
            <MetadataBlock
              title={cleanText(props.metadata.title, "Untitled")}
              artist={cleanText(props.metadata.artist, "Unknown Artist")}
              meta={compactMeta([props.metadata.year, props.metadata.album]) || undefined}
              align="left"
              revealFrame={timeline.phase3.startFrame}
              typographyPreset={scenePreset.typographyPreset}
              style={{ color: palette.text, accent: palette.accent }}
            />
          </div>
        </div>
      ) : null}

      <ElementStack elements={[...(scenePreset.background || []), ...(scenePreset.effects || []), ...(scenePreset.lights || [])]} />
      <ColorGrade preset={scenePreset.colorGrade} />
      <AtmosphereLayer mode={scenePreset.atmosphere} intensity={0.8} />
      {scenePreset.halation.enabled && <Halation opacity={scenePreset.halation.opacity} blur={scenePreset.halation.blur} warmth={scenePreset.halation.warmth} />}
      {scenePreset.ambientLight.enabled && <AmbientLight color={scenePreset.ambientLight.color} opacity={scenePreset.ambientLight.opacity} />}
      <Vignette opacity={0.45} />
      <FilmGrain opacity={0.04} cells={120} />
      <BeatFlash props={props} palette={palette} intensity={0.08} />
    </AbsoluteFill>
  );
};
