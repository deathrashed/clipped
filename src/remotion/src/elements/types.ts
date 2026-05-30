import type { AudioAnalysis } from "../audio/audio-utils";
import type { Palette } from "../lib/palette";

export type ElementCategory =
  | "text"
  | "visualizers"
  | "effects"
  | "depth"
  | "shapes3d"
  | "backgrounds"
  | "lights"
  | "scene";

export type ElementTier = "core" | "premium" | "experimental" | "disabled";

export type TransformControls = {
  position?: { x: number; y: number; z?: number };
  rotation?: { x?: number; y?: number; z: number };
  scale?: number;
};

export type AppearanceControls = {
  opacity?: number;
  blendMode?: React.CSSProperties["mixBlendMode"];
};

export type KeyframeControl<T> = {
  value: T;
  keyframes?: Array<{
    frame: number;
    value: T;
    easing?: "linear" | "ease" | "easeIn" | "easeOut" | "spring";
  }>;
};

export type InspectorControl =
  | { type: "number"; key: string; label: string; min?: number; max?: number; step?: number; defaultValue: number; keyframeable?: boolean }
  | { type: "slider"; key: string; label: string; min: number; max: number; step?: number; defaultValue: number; keyframeable?: boolean }
  | { type: "color"; key: string; label: string; defaultValue: string; keyframeable?: boolean }
  | { type: "select"; key: string; label: string; options: string[]; defaultValue: string; keyframeable?: boolean }
  | { type: "boolean"; key: string; label: string; defaultValue: boolean; keyframeable?: boolean };

export type InspectorSection = {
  title: string;
  controls: InspectorControl[];
};

export type ElementDefinition = {
  id: string;
  label: string;
  category: ElementCategory;
  group?: string;
  tier: ElementTier;
  implemented: boolean;
  component?: string;
  description: string;
  inspector: InspectorSection[];
  defaultProps: Record<string, unknown>;
  recommendedFor: string[];
  avoidFor?: string[];
  safeByDefault: boolean;
  audioReactive?: boolean;
  requires3D?: boolean;
  requiresPostprocessing?: boolean;
};

export type EffectModifierId =
  | "glow"
  | "blur"
  | "shadow"
  | "stroke"
  | "adjust"
  | "dither"
  | "pixelate"
  | "wobble";

export type EffectModifierInstance = {
  id: EffectModifierId;
  enabled?: boolean;
  props?: Record<string, unknown>;
};

export type ModifierDefinition = {
  id: EffectModifierId;
  label: string;
  description: string;
  inspector: InspectorSection[];
  safeByDefault: boolean;
  recommendedFor: string[];
  avoidFor?: string[];
};

export type BaseElementInstance = {
  id: string;
  enabled?: boolean;
  transform?: TransformControls;
  appearance?: AppearanceControls;
  effects?: EffectModifierInstance[];
  props?: Record<string, unknown>;
};

export type ElementInstance = BaseElementInstance;

export type ElementStackProps = {
  elements: ElementInstance[];
  audio?: AudioAnalysis;
  palette?: Palette;
  allowExperimental?: boolean;
  enable3D?: boolean;
};

export type VisualizerElementProps = {
  audio: AudioAnalysis;
  palette: Palette;
  transform?: TransformControls;
  appearance?: AppearanceControls;
  color?: string;
  primaryColor?: string;
  secondaryColor?: string;
  intensity?: number;
  density?: number;
  pattern?: number;
  volume?: number;
  opacity?: number;
  width?: number;
  height?: number;
};
