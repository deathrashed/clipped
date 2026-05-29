import {
  AbsoluteFill,
  Img,
  spring,
  staticFile,
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
import { useAudioReactive } from "../hooks/useAudioReactive";
import { motionFactor, resolvePalette } from "../lib/palette";
import { useLayout } from "../layouts";
import { cleanText, compactMeta } from "../lib/text";
import { resolveScenePreset } from "../presets/scene-presets";

export const MetalVHS = (props: ClippedRenderProps) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const palette = resolvePalette(props);
  const motion = motionFactor(props.options.motion);
  const audio = useAudioReactive(props.assets.audioSrc, 128, props.options.seed);
  const scenePreset = resolveScenePreset(props.options.style);

  const layout = useLayout("centered");
  const artSize = layout.artwork.size;
  const artY = layout.artwork.cy - layout.height / 2;

  const artReveal = spring({ frame: frame - fps * 0.3, fps, config: { damping: 18, stiffness: 80 } });
  const artScale = 0.94 + artReveal * 0.06;

  const chromaStrength = audio.bass * 10 * motion;
  const captionsStyle = (props.options.captions as string) || "metadata";

  const coverSrc = props.assets.coverSrc ? staticFile(props.assets.coverSrc) : null;

  return (
    <AbsoluteFill style={{ backgroundColor: "#060606" }}>
      <AudioLayer props={props} />

      {/* ── Very dark blurred background ── */}
      <ArtworkBackground src={props.assets.coverSrc} palette={palette} mode="atmospheric" />

      {/* ── Heavy dark overlay ── */}
      <div style={{ position: "absolute", inset: 0, background: "rgba(0,0,0,0.72)" }} />

      {/* ── Cover art with VHS-style border ── */}
      {coverSrc ? (
        <div
          style={{
            position: "absolute",
            left: "50%",
            top: "50%",
            transform: `translate(-50%, calc(-50% + ${artY}px)) scale(${artScale})`,
            opacity: artReveal,
            zIndex: 10,
          }}
        >
          <ArtworkFrame size={artSize} preset="chrome">
            <Img src={coverSrc} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
          </ArtworkFrame>
        </div>
      ) : (
        <div
          style={{
            position: "absolute",
            left: "50%",
            top: "50%",
            transform: `translate(-50%, calc(-50% + ${artY}px)) scale(${artScale})`,
            opacity: artReveal,
            zIndex: 10,
          }}
        >
          <ArtworkFrame size={artSize} preset="chrome">
            <FallbackArtwork size={artSize} palette={palette} seed={props.metadata.title} />
          </ArtworkFrame>
        </div>
      )}

      {/* ── Oscilloscope below art ── */}
      <div
        style={{
          position: "absolute",
          left: "50%",
          bottom: layout.height - layout.visualizer.bottom + 56,
          transform: "translateX(-50%)",
          opacity: 0.5,
        }}
      >
        <Oscilloscope
          audio={audio}
          palette={palette}
          width={layout.width * 0.82}
          height={36}
          strokeWidth={1.5}
          glow={scenePreset.visualizer.glow}
        />
      </div>

      {/* ── Spectrum bars below art ── */}
      <div
        style={{
          position: "absolute",
          left: "50%",
          bottom: layout.height - layout.visualizer.bottom,
          transform: "translateX(-50%)",
          opacity: 0.65,
        }}
      >
        <SpectrumBars audio={audio} palette={palette} count={36} width={layout.visualizer.width} height={48} />
      </div>

      {/* ── Compact metadata ── */}
      {props.options.captions === "off" ? (
        <MetadataBlock
          title={cleanText(props.metadata.title, cleanText(props.metadata.sourceFilename, "Untitled"))}
          artist={cleanText(props.metadata.artist, "Unknown Artist")}
          meta={compactMeta([props.metadata.album, props.metadata.year, props.metadata.genre]) || undefined}
          align={layout.typography.align}
          revealFrame={fps * 0.3}
          typographyPreset={scenePreset.typographyPreset}
          style={{
            position: "absolute",
            left: layout.typography.left,
            top: layout.typography.top,
            width: layout.typography.width,
            color: palette.text,
            accent: palette.accent,
          }}
        />
      ) : null}

      {/* ── Captions ── */}
      <Captions
        lyricsSrc={props.assets.lyrics}
        lyricsJson={(props.assets as any).lyricsJson}
        captionsStyle={captionsStyle as any}
        originalStart={props.audio.originalStart}
        metadata={{
          title: props.metadata.title,
          artist: props.metadata.artist,
          album: props.metadata.album,
        }}
      />

      {/* ── Element Stack (effects, lights, depth, backgrounds) ── */}
      <ElementStack
        elements={[
          ...(scenePreset.background || []),
          ...(scenePreset.effects || []),
          ...(scenePreset.lights || []),
        ]}
      />

      {/* ── Cinematic PostFX Overlays ── */}
      <ColorGrade preset={scenePreset.colorGrade} />
      <AtmosphereLayer mode={scenePreset.atmosphere} intensity={1} />
      {scenePreset.halation.enabled && (
        <Halation
          opacity={scenePreset.halation.opacity}
          blur={scenePreset.halation.blur}
          warmth={scenePreset.halation.warmth}
        />
      )}
      {scenePreset.ambientLight.enabled && (
        <AmbientLight
          color={scenePreset.ambientLight.color}
          opacity={scenePreset.ambientLight.opacity}
        />
      )}

      {/* ── VHS post FX ── */}
      <ChromaticAberration strength={chromaStrength} opacity={0.4} />
      <Scanlines opacity={0.15} />
      <VHSTears palette={palette} opacity={0.65} tearCount={4} />
      <Vignette opacity={0.82} />
      <FilmGrain opacity={0.14} cells={200} />
      <BeatFlash props={props} palette={palette} intensity={0.22} />
    </AbsoluteFill>
  );
};
