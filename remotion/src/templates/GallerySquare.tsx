import { AbsoluteFill, Easing, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import type { ClippedRenderProps } from "../types";
import { AudioLayer } from "../components/AudioLayer";
import { ArtworkBackground } from "../artwork/ArtworkBackground";
import { ArtworkFrame } from "../artwork/ArtworkFrame";
import { FallbackArtwork } from "../artwork/FallbackArtwork";
import { MetadataBlock } from "../components/Metadata";
import { BeatFlash, PostFxStack, ReactiveHalo, ColorGrade, AtmosphereLayer, Halation, AmbientLight, RimLight } from "../effects";
import { SpectrumBars, WaveRibbon } from "../visualizers";
import { ElementStack } from "../elements";
import { useAudioReactive } from "../hooks/useAudioReactive";
import { motionFactor, resolvePalette } from "../lib/palette";
import { Captions } from "../components/lyrics/Captions";
import { useLayout } from "../layouts";
import { cleanText, compactMeta } from "../lib/text";
import { resolveScenePreset } from "../presets/scene-presets";

export const GallerySquare = (props: ClippedRenderProps) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const palette = resolvePalette(props);
  const motion = motionFactor(props.options.motion);
  const audio = useAudioReactive(props.assets.audioSrc, 128, props.options.seed);
  const scenePreset = resolveScenePreset(props.options.style);
  
  const layout = useLayout(props.options.scene_pack === "gallery" ? "editorial-left" : "centered");
  const coverSize = layout.artwork.size;
  const artY = layout.artwork.cy - layout.height / 2;

  const alternateImage = props.assets.artistImageSrc || props.assets.logoSrc || props.assets.coverSrc;
  const showAlternate = props.options.scene_pack === "gallery" && alternateImage && frame > durationInFrames * 0.48;
  
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
      
      {scenePreset.halo.enabled && (
        <ReactiveHalo
          props={props}
          palette={palette}
          size={coverSize * 1.6}
          y={artY}
          opacity={scenePreset.halo.opacity}
        />
      )}
      
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
              {scenePreset.rimLight.enabled && (
                <RimLight
                  color={scenePreset.rimLight.color}
                  opacity={scenePreset.rimLight.opacity}
                  side="all"
                />
              )}
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
              <FallbackArtwork size={coverSize} palette={palette} seed={props.metadata.title} />
            )}
            {scenePreset.rimLight.enabled && (
              <RimLight
                color={scenePreset.rimLight.color}
                opacity={scenePreset.rimLight.opacity}
                side="all"
              />
            )}
          </ArtworkFrame>
        )}
      </div>

      {props.options.captions === "off" ? (
        <MetadataBlock
          title={cleanText(props.metadata.title, cleanText(props.metadata.sourceFilename, "Untitled"))}
          artist={cleanText(props.metadata.artist, "Unknown Artist")}
          meta={compactMeta([props.metadata.album, props.metadata.year, props.metadata.genre]) || undefined}
          align={layout.typography.align}
          revealFrame={20}
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
      
      {/* ── Element Stack (effects, lights, depth, backgrounds, modifiers) ── */}
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

      <BeatFlash props={props} palette={palette} intensity={0.11} />
      <PostFxStack props={props} palette={palette} grainOpacity={0.08} />
    </AbsoluteFill>
  );
};
