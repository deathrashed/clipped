import { AbsoluteFill, Easing, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import type { ClippedRenderProps } from "../types";
import { AudioLayer } from "../components/AudioLayer";
import { ArtworkBackground } from "../artwork/ArtworkBackground";
import { ArtworkFrame } from "../artwork/ArtworkFrame";
import { MetadataBlock } from "../components/Metadata";
import { BeatFlash, LightSweep, PostFxStack, ReactiveHalo } from "../effects";
import { SpectrumBars, WaveRibbon } from "../visualizers";
import { useAudioReactive } from "../hooks/useAudioReactive";
import { motionFactor, resolvePalette } from "../lib/palette";
import { effectPreset } from "../presets/effects";
import { Captions } from "../components/lyrics/Captions";
import { useLayout } from "../layouts";

export const GallerySquare = (props: ClippedRenderProps) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const palette = resolvePalette(props);
  const motion = motionFactor(props.options.motion);
  const audio = useAudioReactive(props.assets.audioSrc, 128, props.options.seed);
  const preset = effectPreset(props);
  
  const layout = useLayout("centered");
  const coverSize = layout.artwork.size;
  const artY = layout.artwork.cy - layout.height / 2;

  const alternateImage = props.assets.artistImageSrc || props.assets.logoSrc || props.assets.coverSrc;
  const showAlternate = props.options.scene_pack === "gallery" && alternateImage && frame > durationInFrames * 0.48;
  const titleY = props.options.waveform === "none" ? layout.height - 214 : layout.height - 258;
  
  const slide = interpolate(
    frame,
    [durationInFrames * 0.46, durationInFrames * 0.55],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.bezier(0.16, 1, 0.3, 1) },
  );

  const framePreset = props.options.style === "brutal" ? "chrome" : 
                      props.options.style === "zine" ? "none" : "matte";

  return (
    <AbsoluteFill style={{ backgroundColor: palette.bg }}>
      <AudioLayer props={props} />
      <ArtworkBackground src={props.assets.coverSrc} palette={palette} mode="atmospheric" />
      <ReactiveHalo props={props} palette={palette} size={coverSize * 1.6} y={artY} opacity={preset.haloOpacity} />
      {preset.lightSweep ? <LightSweep palette={palette} opacity={0.2} /> : null}
      
      <div
        style={{
          position: "absolute",
          left: "50%",
          top: "50%",
          transform: `translate(-50%, calc(-50% + ${artY + Math.sin(frame / 86) * 4 * motion}px)) scale(${0.96 + slide * 0.04})`,
          zIndex: 10,
        }}
      >
        {showAlternate && alternateImage ? (
          <div style={{ opacity: slide, transform: `rotate(${(1 - slide) * -2}deg)` }}>
            <ArtworkFrame size={coverSize} preset={framePreset}>
              <Img
                src={staticFile(alternateImage)}
                style={{
                  width: "100%",
                  height: "100%",
                  objectFit: "cover",
                }}
              />
            </ArtworkFrame>
          </div>
        ) : (
          <ArtworkFrame size={coverSize} preset={framePreset}>
            {props.assets.coverSrc ? (
              <Img
                src={staticFile(props.assets.coverSrc)}
                style={{
                  width: "100%",
                  height: "100%",
                  objectFit: "cover",
                }}
              />
            ) : (
              <div
                style={{
                  width: "100%",
                  height: "100%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: palette.muted,
                  fontSize: 42,
                }}
              >
                No Artwork
              </div>
            )}
          </ArtworkFrame>
        )}
      </div>

      {props.options.captions === "off" ? (
        <MetadataBlock
          props={props}
          palette={palette}
          revealFrame={20}
          compact
          style={{
            position: "absolute",
            left: layout.typography.left,
            top: layout.typography.top,
            width: layout.typography.width,
          }}
        />
      ) : null}
      {props.options.waveform === "bars" || props.options.waveform === "mirror" ? (
        <div style={{ position: "absolute", left: "50%", bottom: layout.height - layout.visualizer.bottom, transform: "translateX(-50%)" }}>
          <SpectrumBars audio={audio} palette={palette} count={42} width={layout.visualizer.width} height={96} mirror={props.options.waveform === "mirror"} />
        </div>
      ) : null}
      {props.options.waveform === "ribbon" ? (
        <div style={{ position: "absolute", left: "50%", bottom: layout.height - layout.visualizer.bottom, transform: "translateX(-50%)" }}>
          <WaveRibbon audio={audio} palette={palette} width={layout.visualizer.width} height={112} />
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
      <BeatFlash props={props} palette={palette} intensity={0.11} />
      <PostFxStack props={props} palette={palette} grainOpacity={preset.grainOpacity} />
    </AbsoluteFill>
  );
};

