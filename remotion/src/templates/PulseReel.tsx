import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
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
import { VinylRecord } from "../components/vinyl/VinylRecord";
import { Captions } from "../components/lyrics/Captions";
import { BeatFlash, Vignette, FilmGrain } from "../effects";
import { RadialBars, SpectrumBars, WaveRibbon } from "../visualizers";
import { useAudioReactive } from "../hooks/useAudioReactive";
import { motionFactor, resolvePalette } from "../lib/palette";
import { effectPreset } from "../presets/effects";
import { useLayout } from "../layouts";

export const PulseReel = (props: ClippedRenderProps) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const palette = resolvePalette(props);
  const motion = motionFactor(props.options.motion);
  const preset = effectPreset(props);
  
  const layout = useLayout("centered");
  const coverSize = layout.artwork.size;
  const artY = layout.artwork.cy - layout.height / 2;
  const audio = useAudioReactive(props.assets.audioSrc, 128, props.options.seed);

  // ── Logo phase (0 → logoEnd) ────────────────────────────────────────────────
  const logoSrc = props.assets.logoSrc ? staticFile(props.assets.logoSrc) : null;
  const logoEnd = Math.min(fps * 4, durationInFrames * 0.2);
  const logoFadeInEnd = Math.max(1, Math.min(fps * 0.6, logoEnd * 0.38));
  const logoFadeOutStart = Math.max(logoFadeInEnd + 1, logoEnd - Math.min(fps * 0.8, logoEnd * 0.3));
  const logoOpacity = interpolate(
    frame,
    [0, logoFadeInEnd, logoFadeOutStart, logoEnd],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );
  const logoScale = spring({ frame, fps, config: { damping: 18, stiffness: 80 } });

  // ── Vinyl/record spinning phase ─────────────────────────────────────────────
  const recordStart = Math.min(fps * 3, durationInFrames * 0.18);
  const revealStart = Math.max(recordStart + fps * 2, Math.floor(durationInFrames * 0.72));

  const coverReveal = interpolate(
    frame,
    [revealStart, revealStart + fps * 1.2],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.bezier(0.16, 1, 0.3, 1) },
  );
  const recordFade = interpolate(
    frame,
    [revealStart - fps * 0.5, revealStart + fps * 0.8],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  // ── Metadata reveal ─────────────────────────────────────────────────────────
  const metaReveal = interpolate(
    frame,
    [recordStart + fps * 0.5, recordStart + fps * 1.5],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) },
  );
  const metaY = interpolate(metaReveal, [0, 1], [32, 0]);

  // Safe-area bottom: 12% from bottom for TikTok/IG safe zone
  const safeBottom = layout.safe.bottom;

  // Gradient overlay: stronger at top (for logo) and bottom (for metadata)
  const gradientOverlay =
    "linear-gradient(180deg, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0.08) 38%, rgba(0,0,0,0.08) 58%, rgba(0,0,0,0.78) 100%)";

  const captionsStyle = (props.options.captions as any) || "off";
  const showCaptions = captionsStyle !== "off" && captionsStyle !== "metadata";

  return (
    <AbsoluteFill style={{ backgroundColor: palette.bg }}>
      <AudioLayer props={props} />

      {/* ── Background ── */}
      <ArtworkBackground src={props.assets.coverSrc} palette={palette} mode="atmospheric" />

      {/* ── Gradient overlay for legible text zones ── */}
      <div style={{ position: "absolute", inset: 0, background: gradientOverlay, pointerEvents: "none" }} />

      {/* ── Logo ── */}
      {logoSrc ? (
        <Img
          src={logoSrc}
          style={{
            position: "absolute",
            left: "50%",
            top: layout.logo.top,
            width: layout.logo.width,
            maxHeight: layout.height * 0.22,
            objectFit: "contain",
            transform: `translate(-50%, 0) scale(${0.88 + logoScale * 0.12})`,
            opacity: logoOpacity,
            filter: `drop-shadow(0 0 28px ${palette.accent}88)`,
          }}
        />
      ) : null}

      {/* ── Record spinning phase ── */}
      <div style={{ opacity: recordFade }}>
        {["ring", "radial", "flower"].includes(String(props.options.waveform)) ? (
          <div
            style={{
              position: "absolute",
              left: "50%",
              top: "50%",
              transform: `translate(-50%, calc(-50% + ${artY}px))`,
            }}
          >
            <RadialBars
              audio={audio}
              palette={palette}
              size={layout.width * 0.88}
              innerRadius={coverSize * 0.55}
              count={88}
              mode={props.options.waveform === "flower" ? "flower" : "ring"}
            />
          </div>
        ) : null}
        <VinylRecord props={props} palette={palette} size={coverSize} y={artY} revealFrame={recordStart} />
      </div>

      {/* ── Cover reveal (replaces record) ── */}
      <div
        style={{
          position: "absolute",
          left: "50%",
          top: "50%",
          transform: `translate(-50%, calc(-50% + ${artY + coverReveal * 6}px)) scale(${0.92 + coverReveal * 0.08})`,
          opacity: coverReveal,
        }}
      >
        <ArtworkFrame size={coverSize} preset={props.options.style === "zine" ? "none" : "matte"}>
          {props.assets.coverSrc ? (
            <Img src={staticFile(props.assets.coverSrc)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
          ) : (
            <div style={{ width: "100%", height: "100%", display: "flex", alignItems: "center", justifyContent: "center", background: palette.panel, color: palette.muted, fontSize: 46 }}>No Artwork</div>
          )}
        </ArtworkFrame>
      </div>

      {/* ── Waveform bars ── */}
      {props.options.waveform === "bars" || props.options.waveform === "mirror" ? (
        <div style={{ position: "absolute", left: "50%", bottom: showCaptions ? 160 : safeBottom + 16, transform: "translateX(-50%)" }}>
          <SpectrumBars
            audio={audio}
            palette={palette}
            count={54}
            width={layout.visualizer.width}
            height={96}
            mirror={props.options.waveform === "mirror"}
          />
        </div>
      ) : null}
      {props.options.waveform === "ribbon" ? (
        <div style={{ position: "absolute", left: "50%", bottom: showCaptions ? 160 : safeBottom + 16, transform: "translateX(-50%)" }}>
          <WaveRibbon
            audio={audio}
            palette={palette}
            width={layout.visualizer.width}
            height={96}
          />
        </div>
      ) : null}

      {/* ── Metadata block ── */}
      <MetadataBlock
        props={props}
        palette={palette}
        align="center"
        revealFrame={recordStart + fps}
        compact
        style={{
          position: "absolute",
          left: "50%",
          top: layout.typography.top,
          width: "88%",
          transform: `translateX(-50%) translateY(${metaY}px)`,
          opacity: metaReveal,
        }}
      />

      {/* ── Captions / Lyrics ── */}
      <Captions
        lyricsSrc={props.assets.lyrics}
        lyricsJson={(props.assets as any).lyricsJson}
        captionsStyle={captionsStyle}
        originalStart={props.audio.originalStart}
        metadata={{
          title: props.metadata.title,
          artist: props.metadata.artist,
          album: props.metadata.album,
        }}
      />

      {/* ── Post FX ── */}
      <Vignette opacity={preset.vignetteOpacity ?? 0.72} />
      {props.options.effects !== "clean" ? <FilmGrain opacity={0.09} cells={120} /> : null}
      <BeatFlash props={props} palette={palette} intensity={0.1} />
    </AbsoluteFill>
  );
};

