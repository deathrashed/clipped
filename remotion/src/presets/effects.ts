import type { ClippedRenderProps } from "../types";

export type EffectPreset = {
  grainOpacity: number;
  haloOpacity: number;
  vignette: number;
  vignetteOpacity?: number; // alias for vignette, injected by effectPreset()
  scanlines: boolean;
  shake: number;
  lightSweep: boolean;
};

const presets: Record<string, EffectPreset> = {
  clean: { grainOpacity: 0, haloOpacity: 0.12, vignette: 0.58, scanlines: false, shake: 0, lightSweep: false },
  texture: { grainOpacity: 0.08, haloOpacity: 0.18, vignette: 0.68, scanlines: false, shake: 0, lightSweep: true },
  grain: { grainOpacity: 0.15, haloOpacity: 0.16, vignette: 0.7, scanlines: false, shake: 0, lightSweep: true },
  film: { grainOpacity: 0.13, haloOpacity: 0.15, vignette: 0.76, scanlines: false, shake: 1.5, lightSweep: true },
  crt: { grainOpacity: 0.1, haloOpacity: 0.12, vignette: 0.82, scanlines: true, shake: 1.2, lightSweep: false },
  vhs: { grainOpacity: 0.16, haloOpacity: 0.10, vignette: 0.86, scanlines: true, shake: 2.4, lightSweep: false },
  metal_vhs: { grainOpacity: 0.18, haloOpacity: 0.15, vignette: 0.9, scanlines: true, shake: 3.2, lightSweep: false },
  neon: { grainOpacity: 0.07, haloOpacity: 0.38, vignette: 0.66, scanlines: false, shake: 1, lightSweep: true },
};

export const effectPreset = (props: ClippedRenderProps): EffectPreset => {
  const name = String(props.options.effects || "texture");
  const p = presets[name] || presets.texture;
  return { ...p, vignetteOpacity: p.vignette };
};

