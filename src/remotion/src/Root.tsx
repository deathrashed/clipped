import { Composition, type CalculateMetadataFunction } from "remotion";
import type { ReactElement } from "react";
import defaultProps from "./default-props.json";
import manifest from "../../../data/templates.manifest.json";
import type { ClippedRenderProps, RemotionCompositionId, RemotionTemplateId } from "./types";
import { GallerySquare } from "./templates/GallerySquare";
import { PulseReel } from "./templates/PulseReel";
import { RecordSquare } from "./templates/RecordSquare";
import { FluidScene } from "./templates/FluidScene";
import { MetalVHS } from "./templates/MetalVHS";
import { PremiumCard } from "./templates/PremiumCard";
import { VinylSleevePro } from "./templates/VinylSleevePro";
import { ArtistFocusPro } from "./templates/ArtistFocusPro";
import { MetadataCardPro } from "./templates/MetadataCardPro";
import { WaveformStagePro } from "./templates/WaveformStagePro";
import { MetalVHSPro } from "./templates/MetalVHSPro";
import { GlassCardPro } from "./templates/GlassCardPro";
import { NeonPulsePro } from "./templates/NeonPulsePro";
import { ConcertPosterPro } from "./templates/ConcertPosterPro";
import { CinematicPro } from "./templates/CinematicPro";
import { SpinnerPro } from "./templates/SpinnerPro";
import { CollectorCard } from "./templates/CollectorCard";
import { BandIntro } from "./templates/BandIntro";
import { AudioOrb } from "./templates/AudioOrb";
import { QAPixelation, QAFerroFluid, QAStrobe } from "./qa";

const typedDefaultProps = defaultProps as ClippedRenderProps;

const components: Record<RemotionCompositionId, (props: ClippedRenderProps) => ReactElement> = {
  "pulse-reel": PulseReel,
  "gallery-square": GallerySquare,
  "record-square": RecordSquare,
  "fluid-scene": FluidScene,
  "metal-vhs": MetalVHS,
  "premium-card": PremiumCard,
  "vinyl-sleeve-pro": VinylSleevePro,
  "artist-focus-pro": ArtistFocusPro,
  "metadata-card-pro": MetadataCardPro,
  "waveform-stage-pro": WaveformStagePro,
  "metal-vhs-pro": MetalVHSPro,
  "glass-card-pro": GlassCardPro,
  "neon-pulse-pro": NeonPulsePro,
  "concert-poster-pro": ConcertPosterPro,
  "cinematic-pro": CinematicPro,
  "spinner-pro": SpinnerPro,
  "collector-card": CollectorCard,
  "band-intro": BandIntro,
  "audio-orb": AudioOrb,
};

const calculateMetadata: CalculateMetadataFunction<ClippedRenderProps> = ({ props }) => {
  const fps = props.fps || 30;
  const durationFrames =
    props.durationFrames || Math.max(1, Math.round((props.durationSeconds || 8) * fps));
  return {
    durationInFrames: durationFrames,
    fps,
    width: props.width || 1080,
    height: props.height || 1080,
    props: {
      ...typedDefaultProps,
      ...props,
      assets: { ...typedDefaultProps.assets, ...props.assets },
      metadata: { ...typedDefaultProps.metadata, ...props.metadata },
      audio: { ...typedDefaultProps.audio, ...props.audio },
      options: { ...typedDefaultProps.options, ...props.options },
      encoding: { ...typedDefaultProps.encoding, ...props.encoding },
      durationFrames,
      fps,
    },
  };
};

export const RemotionRoot = () => {
  return (
    <>
      {/* ── QA Bench: element verification ── */}
      <Composition id="qa-pixelation" component={QAPixelation} durationInFrames={1} fps={30} width={1080} height={1080} />
      <Composition id="qa-ferrofluid" component={QAFerroFluid} durationInFrames={1} fps={30} width={1080} height={1080} />
      <Composition id="qa-strobe" component={QAStrobe} durationInFrames={30} fps={30} width={1080} height={1080} />

      {manifest.templates.map((template) => {
        const id = template.composition_id as RemotionCompositionId;
        const component = components[id];
        if (!component) {
          return null;
        }
        const [width, height] = template.aspect;
        return (
          <Composition
            key={id}
            id={id}
            component={component}
            durationInFrames={typedDefaultProps.durationFrames}
            fps={typedDefaultProps.fps}
            width={width}
            height={height}
            defaultProps={{
              ...typedDefaultProps,
              templateId: template.name as RemotionTemplateId,
              compositionId: id,
              width,
              height,
              options: { ...typedDefaultProps.options, ...template.defaults },
            }}
            calculateMetadata={calculateMetadata}
          />
        );
      })}
    </>
  );
};
