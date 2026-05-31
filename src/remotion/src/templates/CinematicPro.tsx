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
import { resolveAssets } from "../template-helpers/templateAssets";
import { useTimeline, easeIn } from "../template-helpers/templateTiming";

export const CinematicPro = (props: ClippedRenderProps) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const palette = resolvePalette(props);
  const motion = motionFactor(props.options.motion);
  const scenePreset = resolveScenePreset("cinematic");
  const layout = useLayout("editorial-left");
  const coverSize = layout.artwork.size * 0.65;
  const assets = resolveAssets(props);

  const timeline = useTimeline({ phase1Start: 1, phase2Start: 3, phase3Start: 5, outroStart: 1.5 });

  const artistBgReveal = easeIn(frame, timeline.phase1.startFrame, 20);

  const logoReveal = easeIn(frame, 5, 20);
  const logoFade = interpolate(
    frame,
    [timeline.phase2.startFrame - 30, timeline.phase2.startFrame],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );
  const logoOpacity = Math.min(logoReveal, logoFade);

  const coverSlide = spring({
    frame: Math.max(0, frame - timeline.phase1.startFrame),
    fps,
    config: { damping: 14, stiffness: 70 },
  });
  const coverX = interpolate(coverSlide, [0, 1], [-layout.width * 0.5, 0]);

  const metaReveal = easeIn(frame, timeline.phase3.startFrame, 18);

  const globalFade = frame > durationInFrames - 30
    ? interpolate(frame, [durationInFrames - 30, durationInFrames - 3], [1, 0])
    : 1;

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <AudioLayer props={props} />

      <ArtworkBackground src={props.assets.coverSrc} palette={palette} mode="atmospheric" />

      {assets.hasArtistImage ? (
        <div
          style={{
            position: "absolute",
            inset: 0,
            opacity: artistBgReveal * 0.5,
            zIndex: 5,
          }}
        >
          <Img
            src={assets.artistImageSrc!}
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
          />
        </div>
      ) : null}

      <div
        style={{
          position: "absolute",
          inset: 0,
          background: "linear-gradient(to right, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.3) 50%, rgba(0,0,0,0.4) 100%)",
          zIndex: 6,
          pointerEvents: "none",
        }}
      />

      {assets.hasLogo && logoOpacity > 0 ? (
        <div
          style={{
            position: "absolute",
            left: "50%",
            top: layout.safe.top + 20,
            transform: "translateX(-50%)",
            zIndex: 12,
            opacity: logoOpacity * globalFade,
            maxWidth: layout.width * 0.35,
          }}
        >
          <Img
            src={assets.logoSrc!}
            style={{
              width: "100%",
              height: "auto",
              maxHeight: 90,
              objectFit: "contain",
              filter: "drop-shadow(0 8px 30px rgba(0,0,0,0.8))",
            }}
          />
        </div>
      ) : null}

      <div
        style={{
          position: "absolute",
          left: layout.safe.left,
          top: "50%",
          transform: `translateY(-50%)`,
          zIndex: 10,
          opacity: globalFade,
        }}
      >
        <div
          style={{
            transform: `translateX(${coverX}px)`,
            boxShadow: `0 20px 100px rgba(0,0,0,0.7), 0 0 0 3px rgba(255,255,255,0.1)`,
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
      </div>

      <div
        style={{
          position: "absolute",
          left: layout.safe.left + coverSize + 40,
          top: "50%",
          transform: "translateY(-50%)",
          zIndex: 10,
          opacity: metaReveal * globalFade,
          maxWidth: layout.width * 0.38,
        }}
      >
        <MetadataBlock
          title={cleanText(props.metadata.title, "Untitled")}
          artist={cleanText(props.metadata.artist, "Unknown Artist")}
          meta={compactMeta([props.metadata.album, props.metadata.year, props.metadata.genre]) || undefined}
          align="left"
          revealFrame={timeline.phase3.startFrame}
          typographyPreset="cinematic"
          style={{ color: palette.text, accent: palette.accent }}
        />
      </div>

      <div
        style={{
          position: "absolute",
          left: "50%",
          bottom: 50,
          transform: "translateX(-50%)",
          width: layout.width * 0.5,
          height: 2,
          background: `linear-gradient(to right, transparent, ${palette.accent}, transparent)`,
          opacity: metaReveal * 0.4 * globalFade,
        }}
      />

      <ElementStack elements={[...(scenePreset.background || []), ...(scenePreset.effects || []), ...(scenePreset.lights || [])]} />
      <ColorGrade preset={scenePreset.colorGrade} />
      <AtmosphereLayer mode={scenePreset.atmosphere} intensity={0.8} />
      {scenePreset.halation.enabled && (
        <Halation opacity={scenePreset.halation.opacity} blur={scenePreset.halation.blur} warmth={scenePreset.halation.warmth} />
      )}
      {scenePreset.ambientLight.enabled && (
        <AmbientLight color={scenePreset.ambientLight.color} opacity={scenePreset.ambientLight.opacity} />
      )}
      <Vignette opacity={0.5} />
      <FilmGrain opacity={0.04} cells={100} />
      <BeatFlash props={props} palette={palette} intensity={0.08} />
    </AbsoluteFill>
  );
};
