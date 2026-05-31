import { AbsoluteFill, Img, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import type { CSSProperties } from "react";
import type { ClippedRenderProps } from "../types";
import { AudioLayer } from "../components/AudioLayer";
import { ArtworkBackground } from "../artwork/ArtworkBackground";
import { ArtworkFrame } from "../artwork/ArtworkFrame";
import { FallbackArtwork } from "../artwork/FallbackArtwork";
import { ColorGrade, AtmosphereLayer, Halation, AmbientLight } from "../effects";
import { ElementStack } from "../elements";
import { resolvePalette, motionFactor } from "../lib/palette";
import { cleanText } from "../lib/text";
import { resolveScenePreset } from "../presets/scene-presets";
import { useLayout } from "../layouts";
import { resolveAssets } from "../template-helpers/templateAssets";
import { useTimeline, easeIn } from "../template-helpers/templateTiming";

const fieldStyle = (delay: number, accent: string): CSSProperties => ({
  borderLeft: `3px solid ${accent}`,
  paddingLeft: 16,
  marginBottom: 22,
});

const labelStyle: CSSProperties = {
  fontSize: 18,
  letterSpacing: 4,
  textTransform: "uppercase",
  fontWeight: 700,
  opacity: 0.5,
  marginBottom: 4,
};

const valueStyle: CSSProperties = {
  fontSize: 36,
  fontWeight: 650,
  lineHeight: 1.08,
};

export const MetadataCardPro = (props: ClippedRenderProps) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const palette = resolvePalette(props);
  const motion = motionFactor(props.options.motion);
  const scenePreset = resolveScenePreset(props.options.style);
  const layout = useLayout("editorial-left");
  const coverSize = Math.min(layout.artwork.size, layout.width * 0.48);
  const assets = resolveAssets(props);

  const timeline = useTimeline({ phase1Start: 0, phase2Start: 2, phase3Start: 4.5, outroStart: 1 });

  const coverReveal = easeIn(frame, timeline.phase1.startFrame + 10, 20);
  const coverY = interpolate(coverReveal, [0, 1], [50, 0]);
  const coverScale = 0.88 + coverReveal * 0.12;

  const metaStart = timeline.phase2.startFrame + fps * 0.5;
  const metaOpacity = easeIn(frame, metaStart, 20);

  const fields = [
    { label: "TRACK", value: cleanText(props.metadata.title, cleanText(props.metadata.sourceFilename, "Untitled")) },
    { label: "ARTIST", value: cleanText(props.metadata.artist, "Unknown Artist") },
    { label: "ALBUM", value: cleanText(props.metadata.album) },
    { label: "YEAR", value: cleanText(props.metadata.year) },
    { label: "GENRE", value: cleanText(props.metadata.genre) },
  ].filter((f) => f.value);

  const globalFade = frame > durationInFrames - 30
    ? interpolate(frame, [durationInFrames - 30, durationInFrames - 3], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })
    : 1;

  const coverLeft = layout.typography.left;

  return (
    <AbsoluteFill style={{ backgroundColor: palette.bg }}>
      <AudioLayer props={props} />

      <ArtworkBackground src={props.assets.coverSrc} palette={palette} mode="atmospheric" />

      <div style={{ position: "absolute", inset: 0, background: "linear-gradient(135deg, rgba(0,0,0,0.5), rgba(0,0,0,0.2) 50%, rgba(0,0,0,0.6))", pointerEvents: "none" }} />

      <div
        style={{
          position: "absolute",
          left: coverLeft,
          top: layout.artwork.cy,
          transform: `translate(0, -50%) scale(${coverScale})`,
          opacity: coverReveal * globalFade,
          zIndex: 10,
        }}
      >
        <ArtworkFrame size={coverSize} preset="matte">
          {assets.hasCover ? (
            <Img src={assets.coverSrc!} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
          ) : (
            <FallbackArtwork size={coverSize} palette={palette} seed={props.metadata.title} />
          )}
        </ArtworkFrame>
      </div>

      <div
        style={{
          position: "absolute",
          left: coverLeft + coverSize + 40,
          right: layout.safe.right + 20,
          top: layout.artwork.cy,
          transform: "translateY(-50%)",
          opacity: metaOpacity * globalFade,
          zIndex: 20,
        }}
      >
        {fields.map((field, i) => {
          const reveal = easeIn(frame, metaStart + i * 6, 10);
          return (
            <div
              key={field.label}
              style={{
                ...fieldStyle(i * 6, palette.accent),
                opacity: reveal,
                transform: `translateX(${interpolate(reveal, [0, 1], [16, 0])}px)`,
              }}
            >
              <div style={{ ...labelStyle, color: palette.accent }}>{field.label}</div>
              <div style={{ ...valueStyle, color: palette.text }}>{field.value}</div>
            </div>
          );
        })}
      </div>

      <ElementStack
        elements={[
          ...(scenePreset.background || []),
          ...(scenePreset.effects || []),
          ...(scenePreset.lights || []),
        ]}
      />

      <ColorGrade preset={scenePreset.colorGrade} />
      <AtmosphereLayer mode={scenePreset.atmosphere} intensity={1} />
      {scenePreset.halation.enabled && (
        <Halation opacity={scenePreset.halation.opacity} blur={scenePreset.halation.blur} warmth={scenePreset.halation.warmth} />
      )}
      {scenePreset.ambientLight.enabled && (
        <AmbientLight color={scenePreset.ambientLight.color} opacity={scenePreset.ambientLight.opacity} />
      )}
    </AbsoluteFill>
  );
};
