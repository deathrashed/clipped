import { Composition, type CalculateMetadataFunction } from "remotion";
import type { ReactElement } from "react";
import defaultProps from "./default-props.json";
import manifest from "../templates.manifest.json";
import type { ClippedRenderProps, RemotionCompositionId, RemotionTemplateId } from "./types";
import { GallerySquare } from "./templates/GallerySquare";
import { PulseReel } from "./templates/PulseReel";
import { RecordSquare } from "./templates/RecordSquare";
import { FluidScene } from "./templates/FluidScene";
import { MetalVHS } from "./templates/MetalVHS";
import { PremiumCard } from "./templates/PremiumCard";

const typedDefaultProps = defaultProps as ClippedRenderProps;

const components: Record<RemotionCompositionId, (props: ClippedRenderProps) => ReactElement> = {
  "pulse-reel": PulseReel,
  "gallery-square": GallerySquare,
  "record-square": RecordSquare,
  "fluid-scene": FluidScene,
  "metal-vhs": MetalVHS,
  "premium-card": PremiumCard,
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
