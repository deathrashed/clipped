import {
  AbsoluteFill,
  Img,
  interpolate,
  random,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import type { ClippedRenderProps } from "../types";
import { AudioLayer } from "../components/AudioLayer";
import { ArtworkBackground } from "../artwork/ArtworkBackground";
import { ArtworkFrame } from "../artwork/ArtworkFrame";
import { FallbackArtwork } from "../artwork/FallbackArtwork";
import { MetadataBlock } from "../components/Metadata";
import { Captions } from "../components/lyrics/Captions";
import {
  BeatFlash,
  ChromaticAberration,
  FilmGrain,
  Scanlines,
  VHSTears,
  Vignette,
  ColorGrade,
  AtmosphereLayer,
  Halation,
  AmbientLight,
} from "../effects";
import { Oscilloscope, SpectrumBars } from "../visualizers";
import { ElementStack } from "../elements";
import { motionFactor, resolvePalette } from "../lib/palette";
import { cleanText, compactMeta } from "../lib/text";
import { resolveScenePreset } from "../presets/scene-presets";
import { useAudioReactive } from "../hooks/useAudioReactive";
import { useLayout } from "../layouts";
import { resolveAssets } from "../template-helpers/templateAssets";
import { useTimeline, easeIn, phaseOpacity } from "../template-helpers/templateTiming";

export const MetalVHSPro = (props: ClippedRenderProps) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const palette = resolvePalette(props);
  const motion = motionFactor(props.options.motion);
  const audio = useAudioReactive(props.assets.audioSrc, 128, props.options.seed);
  const scenePreset = resolveScenePreset("vhs-death");
  const layout = useLayout("centered");
  const artSize = layout.artwork.size;
  const artY = layout.artwork.cy - layout.height / 2;
  const assets = resolveAssets(props);

  const timeline = useTimeline({ phase1Start: 0, phase2Start: 2, phase3Start: 4.5, outroStart: 1 });

  const logoIn = easeIn(frame, timeline.phase1.startFrame + 5, 20);
  const logoOut = frame > timeline.phase1.endFrame - fps * 0.5
    ? interpolate(frame, [timeline.phase1.endFrame - fps * 0.5, timeline.phase1.endFrame], [1, 0])
    : 1;
  const logoOpacity = Math.min(logoIn, logoOut);

  const artReveal = spring({ frame: Math.max(0, frame - timeline.phase2.startFrame), fps, config: { damping: 18, stiffness: 80 } });
  const artScale = 0.92 + artReveal * 0.08;

  const metaReveal = easeIn(frame, timeline.phase2.startFrame + fps * 0.5, 18);

  const chromaStrength = audio.bass * 10 * motion;

  const jitter = (random(Math.floor(frame / 4)) - 0.5) * 6 * motion;

  const captionsStyle = (props.options.captions as string) || "off";

  const globalFade = frame > durationInFrames - 30
    ? interpolate(frame, [durationInFrames - 30, durationInFrames - 3], [1, 0])
    : 1;

  return (
    <AbsoluteFill style={{ backgroundColor: "#060606" }}>
      <AudioLayer props={props} />

      <ArtworkBackground src={props.assets.coverSrc} palette={palette} mode="atmospheric" />
      <div style={{ position: "absolute", inset: 0, background: "rgba(0,0,0,0.75)" }} />

      {assets.hasLogo && logoOpacity > 0 ? (
        <div
          style={{
            position: "absolute",
            left: "50%",
            top: "50%",
            transform: `translate(calc(-50% + ${jitter}px), -50%)`,
            opacity: logoOpacity * 0.95 * globalFade,
            zIndex: 20,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            filter: "drop-shadow(4px 0 #ff003c) drop-shadow(-4px 0 #00e5ff) drop-shadow(0 12px 30px black)",
          }}
        >
          <Img
            src={assets.logoSrc!}
            style={{ maxWidth: layout.width * 0.72, maxHeight: layout.height * 0.32, objectFit: "contain" }}
          />
        </div>
      ) : (
        <div
          style={{
            position: "absolute",
            left: "50%",
            top: layout.typography.top * 0.45,
            transform: `translate(calc(-50% + ${jitter}px), 0)`,
            opacity: logoOpacity * globalFade,
            zIndex: 20,
            textAlign: "center",
          }}
        >
          <div
            style={{
              fontSize: 28,
              letterSpacing: 6,
              textTransform: "uppercase",
              fontWeight: 900,
              color: palette.text,
              fontFamily: "Impact, Haettenschweiler, Arial Black, Helvetica, sans-serif",
              textShadow: "4px 0 #ff003c, -4px 0 #00e5ff, 0 8px 20px black",
            }}
          >
            {cleanText(props.metadata.artist, "Unknown Artist").toUpperCase()}
          </div>
        </div>
      )}

      {frame >= timeline.phase2.startFrame ? (
        <div
          style={{
            position: "absolute",
            left: "50%",
            top: "50%",
            transform: `translate(calc(-50% + ${jitter}px), calc(-50% + ${artY}px)) scale(${artScale})`,
            opacity: artReveal * globalFade,
            zIndex: 10,
            boxShadow: "0 20px 80px rgba(0,0,0,0.8), 6px 0 rgba(255,0,55,0.3), -6px 0 rgba(0,229,255,0.3)",
          }}
        >
          <ArtworkFrame size={artSize} preset="chrome">
            {assets.hasCover ? (
              <Img src={assets.coverSrc!} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
            ) : (
              <FallbackArtwork size={artSize} palette={palette} seed={props.metadata.title} />
            )}
          </ArtworkFrame>
        </div>
      ) : null}

      <div
        style={{
          position: "absolute",
          left: "50%",
          bottom: layout.height - layout.visualizer.bottom + 50,
          transform: "translateX(-50%)",
          opacity: 0.45 * globalFade,
        }}
      >
        <Oscilloscope audio={audio} palette={palette} width={layout.width * 0.8} height={28} strokeWidth={1.5} glow={scenePreset.visualizer.glow} />
      </div>

      <div
        style={{
          position: "absolute",
          left: "50%",
          bottom: layout.height - layout.visualizer.bottom,
          transform: "translateX(-50%)",
          opacity: 0.55 * globalFade,
        }}
      >
        <SpectrumBars audio={audio} palette={palette} count={32} width={layout.visualizer.width} height={40} />
      </div>

      {props.options.captions === "off" ? (
        <div
          style={{
            position: "absolute",
            left: layout.typography.left,
            top: layout.typography.top,
            width: layout.typography.width,
            opacity: metaReveal * globalFade,
            zIndex: 20,
          }}
        >
          <MetadataBlock
            title={cleanText(props.metadata.title, cleanText(props.metadata.sourceFilename, "Untitled"))}
            artist={cleanText(props.metadata.artist, "Unknown Artist")}
            meta={compactMeta([props.metadata.year, props.metadata.genre]) || undefined}
            align={layout.typography.align}
            revealFrame={timeline.phase2.startFrame + fps * 0.5}
            typographyPreset="vhs"
            style={{ color: palette.text, accent: palette.accent }}
          />
        </div>
      ) : null}

      <Captions
        lyricsSrc={props.assets.lyrics}
        lyricsJson={(props.assets as any).lyricsJson}
        captionsStyle={captionsStyle as any}
        originalStart={props.audio.originalStart}
        metadata={{ title: props.metadata.title, artist: props.metadata.artist, album: props.metadata.album }}
      />

      <ElementStack elements={[...(scenePreset.background || []), ...(scenePreset.effects || []), ...(scenePreset.lights || [])]} />

      <ColorGrade preset={scenePreset.colorGrade} />
      <AtmosphereLayer mode={scenePreset.atmosphere} intensity={1} />
      {scenePreset.halation.enabled && (
        <Halation opacity={scenePreset.halation.opacity} blur={scenePreset.halation.blur} warmth={scenePreset.halation.warmth} />
      )}
      {scenePreset.ambientLight.enabled && (
        <AmbientLight color={scenePreset.ambientLight.color} opacity={scenePreset.ambientLight.opacity} />
      )}

      <ChromaticAberration strength={chromaStrength} opacity={0.4} />
      <Scanlines opacity={0.15} />
      <VHSTears palette={palette} opacity={0.55} tearCount={3} />
      <Vignette opacity={0.8} />
      <FilmGrain opacity={0.12} cells={200} />
      <BeatFlash props={props} palette={palette} intensity={0.22} />
    </AbsoluteFill>
  );
};
