import type { ElementStackProps } from "./types";
import registry from "./registry";
import { Vignette, ChromaticAberration, Fisheye } from "./effects/lens";
import { Noise, Scanline, VHS } from "./effects/texture";
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
      const { id, intensity = 0.5, opacity = 1, props: extraProps } = el;

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

      switch (id) {
        case "vignette":
          return <Vignette key={key} intensity={intensity} opacity={opacity} />;
        case "chromatic-aberration":
          return <ChromaticAberration key={key} intensity={intensity} opacity={opacity} />;
        case "fisheye":
          return <Fisheye key={key} intensity={intensity} />;
        case "noise":
          return <Noise key={key} intensity={intensity} opacity={opacity} />;
        case "scanline":
          return <Scanline key={key} intensity={intensity} opacity={opacity} />;
        case "vhs":
          return <VHS key={key} intensity={intensity} opacity={opacity} />;
        case "bloom":
          return <Bloom key={key} intensity={intensity} opacity={opacity} />;
        case "strobe":
          return <Strobe key={key} intensity={intensity} />;
        case "brightness-contrast":
          return <BrightnessContrast key={key} intensity={intensity} />;
        case "hue-saturation":
          return <HueSaturation key={key} intensity={intensity} />;
        case "color-grading":
          return <ColorGrading key={key} intensity={intensity} preset={extraProps?.preset as any} />;
        case "filter-effect":
          return <FilterEffect key={key} intensity={intensity} />;
        case "tone-mapping":
          return <ToneMapping key={key} intensity={intensity} />;
        case "black-white":
          return <BlackWhite key={key} intensity={intensity} />;
        case "inversion":
          return <Inversion key={key} intensity={intensity} />;
        case "fog":
          return <DepthFog key={key} intensity={intensity} />;
        case "depth-blur":
          return <DepthBlur key={key} intensity={intensity} />;
        case "shader-bg":
          return <ShaderBackground key={key} intensity={intensity} />;
        case "gradient-bg":
          return <GradientBackground key={key} intensity={intensity} />;
        case "noise-bg":
          return <NoiseBackground key={key} intensity={intensity} />;
        case "ambient-light":
          return (
            <AmbientLightLayer
              key={key}
              intensity={intensity}
              color={extraProps?.color as string}
              spread={extraProps?.spread as number}
            />
          );
        case "point-light":
          return <PointLightLayer key={key} intensity={intensity} />;
        case "light-preset":
          return <LightPreset key={key} intensity={intensity} preset={(extraProps?.variant || extraProps?.preset) as any} />;
        default:
          warnings.push(`Element "${id}" has no render path — skipping.`);
          return null;
      }
    });

  if (warnings.length > 0) {
    console.warn(WARN_PREFIX, warnings.join(" "));
  }

  return <>{nodes}</>;
};
