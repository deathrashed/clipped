import type { ElementStackProps, ElementInstance } from "./types";
import registry from "./registry";
import { ModifierWrapper } from "./modifiers/ModifierWrapper";
import { Vignette, ChromaticAberration, Fisheye } from "./effects/lens";
import { Noise, Scanline, VHS, Pixelation } from "./effects/texture";
import { Bloom, Strobe } from "./effects/glow";
import {
  BrightnessContrast,
  HueSaturation,
  ColorGrading,
  FilterEffect,
  ToneMapping,
  BlackWhite,
  Inversion,
} from "./effects/color";
import { DepthFog, DepthBlur } from "./depth";
import { ShaderBackground, GradientBackground, NoiseBackground } from "./backgrounds";
import { AmbientLightLayer, PointLightLayer, LightPreset } from "./lights";

const WARN_PREFIX = "[ElementStack]";

function resolveElementProps(el: ElementInstance) {
  const def = registry.find((d) => d.id === el.id);
  const base = def?.defaultProps || {};
  const merged = { ...base, ...el.props };
  if (el.appearance?.opacity !== undefined) {
    merged.opacity = el.appearance.opacity;
  }
  return merged;
}

export const ElementStack = ({
  elements,
  allowExperimental = false,
  enable3D = false,
}: ElementStackProps) => {
  if (!elements || elements.length === 0) return null;

  const warnings: string[] = [];

  const nodes = elements
    .filter((el) => el.enabled !== false)
    .map((el, idx) => {
      const def = registry.find((d) => d.id === el.id);
      const { id, effects } = el;
      const mergedProps = resolveElementProps(el);
      const intensity = (mergedProps.intensity as number) ?? 0.5;
      const opacity = (mergedProps.opacity as number) ?? 1;

      if (!def) {
        warnings.push(`Unknown element ID "${id}" — skipping.`);
        return null;
      }

      if (def.tier === "disabled") {
        return null;
      }

      if (def.tier === "experimental" && !allowExperimental) {
        return null;
      }

      if (def.requires3D && !enable3D) {
        return null;
      }

      if (!def.implemented) {
        warnings.push(`Element "${id}" is not yet implemented — skipping.`);
        return null;
      }

      const key = `el-${id}-${idx}`;

      const renderElement = () => {
        switch (id) {
          case "vignette":
            return <Vignette key={key} {...mergedProps} intensity={intensity} opacity={opacity} />;
          case "chromatic-aberration":
            return <ChromaticAberration key={key} {...mergedProps} intensity={intensity} opacity={opacity} />;
          case "fisheye":
            return <Fisheye key={key} {...mergedProps} intensity={intensity} />;
          case "noise":
            return <Noise key={key} {...mergedProps} intensity={intensity} opacity={opacity} />;
          case "scanline":
            return <Scanline key={key} {...mergedProps} intensity={intensity} opacity={opacity} />;
          case "vhs":
            return <VHS key={key} {...mergedProps} intensity={intensity} opacity={opacity} />;
          case "pixelation":
            return <Pixelation key={key} {...mergedProps} intensity={intensity} opacity={opacity} />;
          case "bloom":
            return <Bloom key={key} {...mergedProps} intensity={intensity} opacity={opacity} />;
          case "strobe":
            return <Strobe key={key} {...mergedProps} intensity={intensity} opacity={opacity} />;
          case "brightness-contrast":
            return <BrightnessContrast key={key} {...mergedProps} intensity={intensity} />;
          case "hue-saturation":
            return <HueSaturation key={key} {...mergedProps} intensity={intensity} />;
          case "color-grading":
            return <ColorGrading key={key} preset={(mergedProps.preset) as any} intensity={intensity} />;
          case "filter-effect":
            return <FilterEffect key={key} {...mergedProps} intensity={intensity} />;
          case "tone-mapping":
            return <ToneMapping key={key} intensity={intensity} />;
          case "black-white":
            return <BlackWhite key={key} {...mergedProps} intensity={intensity} />;
          case "inversion":
            return <Inversion key={key} {...mergedProps} intensity={intensity} />;
          case "fog":
            return <DepthFog key={key} {...mergedProps} intensity={intensity} />;
          case "depth-blur":
            return <DepthBlur key={key} {...mergedProps} intensity={intensity} />;
          case "shader-bg":
            return <ShaderBackground key={key} {...mergedProps} intensity={intensity} />;
          case "gradient-bg":
            return <GradientBackground key={key} {...mergedProps} intensity={intensity} />;
          case "noise-bg":
            return <NoiseBackground key={key} {...mergedProps} intensity={intensity} />;
          case "ambient-light":
            return (
              <AmbientLightLayer
                key={key}
                {...mergedProps}
                intensity={intensity}
                color={mergedProps.color as string}
                spread={mergedProps.spread as number}
              />
            );
          case "point-light":
            return <PointLightLayer key={key} {...mergedProps} intensity={intensity} />;
          case "light-preset":
            return <LightPreset key={key} intensity={intensity} preset={(mergedProps.preset || mergedProps.variant) as any} />;
          default:
            warnings.push(`Element "${id}" has no render path — skipping.`);
            return null;
        }
      };

      const elNode = renderElement();
      if (!elNode) return null;

      if (effects && effects.length > 0) {
        return (
          <div key={key} style={{ position: "relative" }}>
            <ModifierWrapper effects={effects}>{elNode}</ModifierWrapper>
          </div>
        );
      }

      return elNode;
    });

  if (warnings.length > 0) {
    console.warn(WARN_PREFIX, warnings.join(" "));
  }

  return <>{nodes}</>;
};
