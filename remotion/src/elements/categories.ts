import type { ElementCategory } from "./types";

export const categoryLabels: Record<ElementCategory, string> = {
  text: "Text",
  visualizers: "Visualizers",
  effects: "Effects",
  depth: "Depth Effects",
  shapes3d: "Shapes & 3D",
  backgrounds: "Backgrounds",
  lights: "Lights",
  scene: "Scene",
};

export const categoryOrder: ElementCategory[] = [
  "text",
  "visualizers",
  "effects",
  "depth",
  "shapes3d",
  "backgrounds",
  "lights",
  "scene",
];
