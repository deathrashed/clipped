/**
 * fluid_scene — Square metallic fluid/blob center scene
 *
 * Inspired by the Leaf Dog "Hide Those Eyes" reference:
 *   - Black star/particle field background
 *   - Animated metallic fluid blob at center
 *   - Compact typography at the bottom
 *   - Optional synced lyrics overlay
 */
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import type { ClippedRenderProps } from "../types";
import { AudioLayer } from "../components/AudioLayer";
import { MetadataBlock } from "../components/Metadata";
import { Captions } from "../components/lyrics/Captions";
import { BeatFlash, ChromaticAberration, FilmGrain, StarField, Vignette } from "../effects";
import { Oscilloscope, PulseRings } from "../visualizers";
import { useAudioReactive } from "../hooks/useAudioReactive";
import { motionFactor, resolvePalette } from "../lib/palette";
import { useLayout } from "../layouts";

export const FluidScene = (props: ClippedRenderProps) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const palette = resolvePalette(props);
  const motion = motionFactor(props.options.motion);
  const audio = useAudioReactive(props.assets.audioSrc, 128, props.options.seed);

  const layout = useLayout("centered");
  const blobSize = layout.artwork.size;
  const blobY = layout.artwork.cy - layout.height / 2;

  // Intro: title swoops in after 0.6s
  const introReveal = spring({ frame: frame - fps * 0.6, fps, config: { damping: 22, stiffness: 100 } });

  // Blob animation — morph between rounded shapes
  const bassScale = 1 + audio.bass * 0.22 * motion;
  const blobPulse = bassScale * (0.97 + Math.sin(frame / 22) * 0.03 * motion);

  // Chromatic aberration on heavy bass hits
  const chromaStrength = audio.bass * 8 * motion;
  const captionsStyle = (props.options.captions as string) || "off";

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <AudioLayer props={props} />

      {/* ── Star field background ── */}
      <StarField starCount={180} speed={0.3 + audio.full * 0.2} opacity={0.85} />

      {/* ── Metallic fluid blob at center ── */}
      <div
        style={{
          position: "absolute",
          left: "50%",
          top: "50%",
          width: blobSize,
          height: blobSize,
          transform: `translate(-50%, calc(-50% + ${blobY}px)) scale(${blobPulse})`,
          borderRadius: `${48 + Math.sin(frame / 14) * 14}% ${52 - Math.sin(frame / 18) * 12}% ${46 + Math.cos(frame / 16) * 15}% ${54 - Math.cos(frame / 12) * 11}% / ${50 + Math.sin(frame / 20) * 10}% ${48 - Math.sin(frame / 15) * 10}% ${52 + Math.cos(frame / 17) * 12}% ${50 - Math.cos(frame / 13) * 9}%`,
          background: `
            radial-gradient(ellipse at ${32 + Math.sin(frame / 28) * 18}% ${38 + Math.cos(frame / 22) * 16}%,
              ${palette.accent2}cc 0%,
              ${palette.accent}88 28%,
              #1a1a2e 55%,
              transparent 100%)
          `,
          boxShadow: `
            0 0 ${60 + audio.bass * 80}px ${palette.accent}66,
            0 0 ${120 + audio.bass * 120}px ${palette.accent2}33,
            inset 0 0 50px rgba(255,255,255,0.08)
          `,
          filter: `blur(${0.5 + audio.treble * 1.5}px)`,
        }}
      />

      {/* ── Pulse rings emanating from blob ── */}
      <div
        style={{
          position: "absolute",
          left: "50%",
          top: "50%",
          transform: `translate(-50%, calc(-50% + ${blobY}px))`,
        }}
      >
        <PulseRings
          audio={audio}
          palette={palette}
          size={blobSize * 3}
          ringCount={5}
        />
      </div>

      {/* ── Oscilloscope strip at bottom of visual area ── */}
      <div
        style={{
          position: "absolute",
          left: "50%",
          bottom: layout.height - layout.visualizer.bottom,
          transform: "translateX(-50%)",
          opacity: 0.62,
        }}
      >
        <Oscilloscope
          audio={audio}
          palette={palette}
          width={layout.visualizer.width}
          height={48}
          strokeWidth={2}
          glow
        />
      </div>

      {/* ── Chromatic aberration on bass hits ── */}
      <ChromaticAberration strength={chromaStrength} opacity={0.45} />

      {/* ── Compact metadata ── */}
      {props.options.captions === "off" ? (
        <MetadataBlock
          props={props}
          palette={palette}
          y={layout.typography.top}
          revealFrame={fps * 0.6}
          compact
        />
      ) : null}

      {/* ── Captions / Lyrics ── */}
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

      {/* ── Post FX ── */}
      <BeatFlash props={props} palette={palette} intensity={0.14} />
      <Vignette opacity={0.55} />
      <FilmGrain opacity={0.06} cells={100} />
    </AbsoluteFill>
  );
};

