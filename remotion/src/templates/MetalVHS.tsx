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
import { MetadataBlock } from "../components/Metadata";
import { Captions } from "../components/lyrics/Captions";
import {
  BeatFlash,
  ChromaticAberration,
  FilmGrain,
  Scanlines,
  VHSTears,
  Vignette,
} from "../effects";
import { Oscilloscope, SpectrumBars } from "../visualizers";
import { useAudioReactive } from "../hooks/useAudioReactive";
import { motionFactor, resolvePalette } from "../lib/palette";
import { useLayout } from "../layouts";

export const MetalVHS = (props: ClippedRenderProps) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const palette = resolvePalette(props);
  const motion = motionFactor(props.options.motion);
  const audio = useAudioReactive(props.assets.audioSrc, 128, props.options.seed);

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
      ) : null}

      {/* ── Oscilloscope above art ── */}
      <div
        style={{
          position: "absolute",
          top: layout.logo.top,
          left: "50%",
          transform: "translateX(-50%)",
          opacity: 0.7,
        }}
      >
        <Oscilloscope
          audio={audio}
          palette={palette}
          width={layout.width * 0.82}
          height={44}
          strokeWidth={2}
          glow
        />
      </div>

      {/* ── Spectrum bars below art ── */}
      <div
        style={{
          position: "absolute",
          left: "50%",
          bottom: layout.height - layout.visualizer.bottom,
          transform: "translateX(-50%)",
          opacity: 0.8,
        }}
      >
        <SpectrumBars audio={audio} palette={palette} count={36} width={layout.visualizer.width} height={64} />
      </div>

      {/* ── Compact metadata ── */}
      {props.options.captions === "off" ? (
        <MetadataBlock
          props={props}
          palette={palette}
          revealFrame={fps * 0.3}
          compact
          style={{
            position: "absolute",
            left: layout.typography.left,
            top: layout.typography.top,
            width: layout.typography.width,
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

