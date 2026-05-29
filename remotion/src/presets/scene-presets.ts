import type { TypographyPreset } from "../tokens/typography";
import type { ColorGradePreset } from "../effects/ColorGrade";
import type { AtmosphereMode } from "../effects/AtmosphereLayer";

export type ScenePresetId =
  | "clean"
  | "cinematic"
  | "neo-noir"
  | "vhs-death"
  | "black-metal"
  | "boom-bap"
  | "luxury-vinyl"
  | "brutalist"
  | "spotify-canvas";

export type ScenePreset = {
  id: ScenePresetId;
  typographyPreset: TypographyPreset;
  colorGrade: ColorGradePreset;
  atmosphere: AtmosphereMode;
  halation: {
    enabled: boolean;
    opacity: number;
    blur: number;
    warmth: number;
  };
  ambientLight: {
    enabled: boolean;
    color: string;
    opacity: number;
  };
  rimLight: {
    enabled: boolean;
    color: string;
    opacity: number;
  };
  visualizer: {
    glow: boolean;
    intensity: number;
  };
  halo: {
    enabled: boolean;
    opacity: number;
  };
};

const presets: Record<ScenePresetId, ScenePreset> = {
  clean: {
    id: "clean",
    typographyPreset: "minimal",
    colorGrade: "neutral",
    atmosphere: "none",
    halation: { enabled: false, opacity: 0, blur: 0, warmth: 0 },
    ambientLight: { enabled: false, color: "transparent", opacity: 0 },
    rimLight: { enabled: false, color: "transparent", opacity: 0 },
    visualizer: { glow: false, intensity: 0.3 },
    halo: { enabled: false, opacity: 0 },
  },
  cinematic: {
    id: "cinematic",
    typographyPreset: "cinematic",
    colorGrade: "cinematic",
    atmosphere: "dust",
    halation: { enabled: true, opacity: 0.25, blur: 6, warmth: 0.15 },
    ambientLight: { enabled: true, color: "rgba(255, 180, 100, 0.12)", opacity: 0.3 },
    rimLight: { enabled: false, color: "transparent", opacity: 0 },
    visualizer: { glow: false, intensity: 0.4 },
    halo: { enabled: false, opacity: 0 },
  },
  "neo-noir": {
    id: "neo-noir",
    typographyPreset: "editorial",
    colorGrade: "cold",
    atmosphere: "fog",
    halation: { enabled: true, opacity: 0.35, blur: 8, warmth: 0.2 },
    ambientLight: { enabled: true, color: "rgba(0, 120, 255, 0.15)", opacity: 0.4 },
    rimLight: { enabled: true, color: "rgba(0, 150, 255, 0.3)", opacity: 0.5 },
    visualizer: { glow: true, intensity: 0.6 },
    halo: { enabled: true, opacity: 0.15 },
  },
  "vhs-death": {
    id: "vhs-death",
    typographyPreset: "vhs",
    colorGrade: "vhs",
    atmosphere: "smoke",
    halation: { enabled: true, opacity: 0.4, blur: 10, warmth: 0.25 },
    ambientLight: { enabled: true, color: "rgba(255, 50, 50, 0.1)", opacity: 0.3 },
    rimLight: { enabled: true, color: "rgba(255, 100, 100, 0.25)", opacity: 0.4 },
    visualizer: { glow: true, intensity: 0.7 },
    halo: { enabled: true, opacity: 0.25 },
  },
  "black-metal": {
    id: "black-metal",
    typographyPreset: "brutal",
    colorGrade: "black-metal",
    atmosphere: "ash",
    halation: { enabled: true, opacity: 0.3, blur: 8, warmth: 0.1 },
    ambientLight: { enabled: true, color: "rgba(50, 50, 50, 0.2)", opacity: 0.5 },
    rimLight: { enabled: true, color: "rgba(100, 100, 100, 0.3)", opacity: 0.4 },
    visualizer: { glow: false, intensity: 0.8 },
    halo: { enabled: false, opacity: 0 },
  },
  "boom-bap": {
    id: "boom-bap",
    typographyPreset: "editorial",
    colorGrade: "boom-bap",
    atmosphere: "dust",
    halation: { enabled: true, opacity: 0.25, blur: 6, warmth: 0.15 },
    ambientLight: { enabled: true, color: "rgba(200, 160, 100, 0.1)", opacity: 0.3 },
    rimLight: { enabled: false, color: "transparent", opacity: 0 },
    visualizer: { glow: false, intensity: 0.5 },
    halo: { enabled: false, opacity: 0 },
  },
  "luxury-vinyl": {
    id: "luxury-vinyl",
    typographyPreset: "cinematic",
    colorGrade: "luxury-vinyl",
    atmosphere: "none",
    halation: { enabled: true, opacity: 0.2, blur: 6, warmth: 0.12 },
    ambientLight: { enabled: true, color: "rgba(255, 215, 0, 0.08)", opacity: 0.35 },
    rimLight: { enabled: true, color: "rgba(255, 215, 0, 0.4)", opacity: 0.6 },
    visualizer: { glow: false, intensity: 0.4 },
    halo: { enabled: false, opacity: 0 },
  },
  brutalist: {
    id: "brutalist",
    typographyPreset: "brutal",
    colorGrade: "neutral",
    atmosphere: "none",
    halation: { enabled: false, opacity: 0, blur: 0, warmth: 0 },
    ambientLight: { enabled: false, color: "transparent", opacity: 0 },
    rimLight: { enabled: false, color: "transparent", opacity: 0 },
    visualizer: { glow: false, intensity: 0.6 },
    halo: { enabled: false, opacity: 0 },
  },
  "spotify-canvas": {
    id: "spotify-canvas",
    typographyPreset: "minimal",
    colorGrade: "neutral",
    atmosphere: "dust",
    halation: { enabled: false, opacity: 0, blur: 0, warmth: 0 },
    ambientLight: { enabled: false, color: "transparent", opacity: 0 },
    rimLight: { enabled: false, color: "transparent", opacity: 0 },
    visualizer: { glow: false, intensity: 0.3 },
    halo: { enabled: false, opacity: 0 },
  },
};

/**
 * Maps a style string to a ScenePreset. Matches partial and hyphenated strings.
 */
export const resolveScenePreset = (style?: string): ScenePreset => {
  if (!style) return presets.cinematic;

  const normalized = style.toLowerCase().replace(/_/g, "-");

  // Exact mappings
  if (normalized === "clean") return presets.clean;
  if (normalized === "cinematic" || normalized === "premium") return presets.cinematic;
  if (normalized === "neo-noir") return presets["neo-noir"];
  if (normalized === "vhs" || normalized === "vhs-death" || normalized === "metal-vhs" || normalized === "metal_vhs") return presets["vhs-death"];
  if (normalized === "black-metal") return presets["black-metal"];
  if (normalized === "boom-bap") return presets["boom-bap"];
  if (normalized === "luxury" || normalized === "luxury-vinyl") return presets["luxury-vinyl"];
  if (normalized === "brutal" || normalized === "brutalist") return presets.brutalist;
  if (normalized === "spotify" || normalized === "spotify-canvas") return presets["spotify-canvas"];

  // Default fallback
  return presets.cinematic;
};
