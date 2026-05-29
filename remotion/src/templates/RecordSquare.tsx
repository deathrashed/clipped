import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import type { ClippedRenderProps } from "../types";
import { AudioLayer } from "../components/AudioLayer";
import { BackgroundField } from "../components/Artwork";
import { MetadataBlock } from "../components/Metadata";
import { VinylRecord } from "../components/vinyl/VinylRecord";
import { BeatFlash, LightSweep, PostFxStack, ReactiveHalo } from "../effects";
import { RadialBars, SpectrumBars, WaveRibbon } from "../visualizers";
import { useAudioReactive } from "../hooks/useAudioReactive";
import { motionFactor, resolvePalette } from "../lib/palette";
import { effectPreset } from "../presets/effects";
import { Captions } from "../components/lyrics/Captions";
import { useLayout } from "../layouts";

export const RecordSquare = (props: ClippedRenderProps) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const palette = resolvePalette(props);
  const motion = motionFactor(props.options.motion);
  const audio = useAudioReactive(props.assets.audioSrc, 160, props.options.seed);
  const preset = effectPreset(props);
  
  const layout = useLayout("centered");
  const artSize = layout.artwork.size;
  const artY = layout.artwork.cy - layout.height / 2;

  const pulse = interpolate(
    Math.sin((frame / 18) * motion),
    [-1, 1],
    [0.94, 1.03],
  );

  return (
    <AbsoluteFill style={{ backgroundColor: palette.bg }}>
      <AudioLayer props={props} />
      <BackgroundField props={props} palette={palette} intensity={1.18} />
      <ReactiveHalo props={props} palette={palette} size={artSize * 1.64} y={artY} opacity={preset.haloOpacity} />
      {preset.lightSweep ? <LightSweep palette={palette} opacity={0.24} /> : null}
      <div
        style={{
          position: "absolute",
          left: "50%",
          top: "50%",
          width: artSize * 1.28,
          height: artSize * 1.28,
          transform: `translate(-50%, calc(-50% + ${artY}px)) scale(${pulse})`,
          borderRadius: "50%",
          border: `2px solid ${palette.accent}44`,
          boxShadow: `0 0 90px ${palette.accent}22`,
        }}
      />
      {["ring", "radial", "flower"].includes(String(props.options.waveform)) ? (
        <div
          style={{
            position: "absolute",
            left: "50%",
            top: "50%",
            transform: `translate(-50%, calc(-50% + ${artY}px)) scale(${pulse})`,
          }}
        >
          <RadialBars
            audio={audio}
            palette={palette}
            size={artSize * 1.44}
            innerRadius={artSize * 0.55}
            count={108}
            mode={props.options.waveform === "flower" ? "flower" : "ring"}
          />
        </div>
      ) : null}
      <VinylRecord props={props} palette={palette} size={artSize} y={artY} />
      {props.options.captions === "off" ? (
        <MetadataBlock props={props} palette={palette} y={layout.typography.top} revealFrame={20} compact />
      ) : null}
      {props.options.waveform === "bars" || props.options.waveform === "mirror" ? (
        <div style={{ position: "absolute", left: "50%", bottom: layout.height - layout.visualizer.bottom, transform: "translateX(-50%)" }}>
          <SpectrumBars audio={audio} palette={palette} count={44} width={layout.visualizer.width} height={88} mirror={props.options.waveform === "mirror"} />
        </div>
      ) : null}
      {props.options.waveform === "ribbon" ? (
        <div style={{ position: "absolute", left: "50%", bottom: layout.height - layout.visualizer.bottom, transform: "translateX(-50%)" }}>
          <WaveRibbon audio={audio} palette={palette} width={layout.visualizer.width + 10} height={96} />
        </div>
      ) : null}
      <Captions
        lyricsSrc={props.assets.lyrics}
        lyricsJson={(props.assets as any).lyricsJson}
        captionsStyle={(props.options.captions as any) || "metadata"}
        originalStart={props.audio.originalStart}
        metadata={{
          title: props.metadata.title,
          artist: props.metadata.artist,
          album: props.metadata.album,
        }}
      />
      <BeatFlash props={props} palette={palette} intensity={0.12} />
      <PostFxStack props={props} palette={palette} grainOpacity={preset.grainOpacity} />
      <div
        style={{
          position: "absolute",
          left: layout.safe.left,
          right: layout.safe.right,
          bottom: layout.safe.bottom / 2,
          height: 1,
          background: `linear-gradient(90deg, transparent, ${palette.accent}, transparent)`,
          opacity: frame > durationInFrames - 60 ? 0.35 : 0.18,
        }}
      />
    </AbsoluteFill>
  );
};

