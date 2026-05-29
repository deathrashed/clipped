import type { InspectorSection } from "./types";

export const transformSection: InspectorSection = {
  title: "Transform",
  controls: [
    { type: "number", key: "transform.position.x", label: "X", defaultValue: 0, keyframeable: true },
    { type: "number", key: "transform.position.y", label: "Y", defaultValue: 0, keyframeable: true },
    { type: "number", key: "transform.rotation.z", label: "Z", defaultValue: 0, keyframeable: true },
    { type: "slider", key: "transform.scale", label: "Scale", min: 0, max: 10, step: 0.01, defaultValue: 1, keyframeable: true },
  ],
};

export const appearanceSection: InspectorSection = {
  title: "Appearance",
  controls: [
    { type: "slider", key: "appearance.opacity", label: "Opacity", min: 0, max: 1, step: 0.01, defaultValue: 1, keyframeable: true },
  ],
};

export const defaultSections: InspectorSection[] = [transformSection, appearanceSection];

export const glowModifierInspector: InspectorSection[] = [
  {
    title: "Glow",
    controls: [
      { type: "slider", key: "intensity", label: "Intensity", min: 0, max: 2, step: 0.01, defaultValue: 0.3, keyframeable: true },
      { type: "slider", key: "radius", label: "Radius", min: 0, max: 100, step: 1, defaultValue: 20, keyframeable: true },
      { type: "color", key: "color", label: "Color", defaultValue: "#FFFFFF", keyframeable: true },
    ],
  },
];

export const blurModifierInspector: InspectorSection[] = [
  {
    title: "Blur",
    controls: [
      { type: "slider", key: "amount", label: "Amount", min: 0, max: 20, step: 0.1, defaultValue: 2, keyframeable: true },
    ],
  },
];

export const shadowModifierInspector: InspectorSection[] = [
  {
    title: "Shadow",
    controls: [
      { type: "slider", key: "x", label: "X", min: -50, max: 50, step: 1, defaultValue: 4, keyframeable: true },
      { type: "slider", key: "y", label: "Y", min: -50, max: 50, step: 1, defaultValue: 4, keyframeable: true },
      { type: "slider", key: "blur", label: "Blur", min: 0, max: 50, step: 1, defaultValue: 10, keyframeable: true },
      { type: "color", key: "color", label: "Color", defaultValue: "#000000", keyframeable: true },
      { type: "slider", key: "opacity", label: "Opacity", min: 0, max: 1, step: 0.01, defaultValue: 0.3, keyframeable: true },
    ],
  },
];

export const strokeModifierInspector: InspectorSection[] = [
  {
    title: "Stroke",
    controls: [
      { type: "slider", key: "width", label: "Width", min: 0, max: 20, step: 0.5, defaultValue: 2, keyframeable: true },
      { type: "color", key: "color", label: "Color", defaultValue: "#FFFFFF", keyframeable: true },
      { type: "slider", key: "opacity", label: "Opacity", min: 0, max: 1, step: 0.01, defaultValue: 1, keyframeable: true },
    ],
  },
];

export const adjustModifierInspector: InspectorSection[] = [
  {
    title: "Adjust",
    controls: [
      { type: "slider", key: "brightness", label: "Brightness", min: -1, max: 1, step: 0.01, defaultValue: 0, keyframeable: true },
      { type: "slider", key: "contrast", label: "Contrast", min: -1, max: 1, step: 0.01, defaultValue: 0, keyframeable: true },
      { type: "slider", key: "saturation", label: "Saturation", min: -1, max: 1, step: 0.01, defaultValue: 0, keyframeable: true },
      { type: "slider", key: "hue", label: "Hue", min: -180, max: 180, step: 1, defaultValue: 0, keyframeable: true },
    ],
  },
];

export const ditherModifierInspector: InspectorSection[] = [
  {
    title: "Dither",
    controls: [
      { type: "slider", key: "amount", label: "Amount", min: 0, max: 1, step: 0.01, defaultValue: 0.5, keyframeable: true },
      { type: "select", key: "pattern", label: "Pattern", options: ["bayer", "random", "blue-noise"], defaultValue: "bayer", keyframeable: false },
      { type: "slider", key: "colors", label: "Colors", min: 2, max: 64, step: 1, defaultValue: 16, keyframeable: true },
    ],
  },
];

export const pixelateModifierInspector: InspectorSection[] = [
  {
    title: "Pixelate",
    controls: [
      { type: "slider", key: "size", label: "Size", min: 1, max: 50, step: 1, defaultValue: 8, keyframeable: true },
    ],
  },
];

export const wobbleModifierInspector: InspectorSection[] = [
  {
    title: "Wobble",
    controls: [
      { type: "slider", key: "amplitude", label: "Amplitude", min: 0, max: 20, step: 0.1, defaultValue: 2, keyframeable: true },
      { type: "slider", key: "speed", label: "Speed", min: 0, max: 10, step: 0.1, defaultValue: 3, keyframeable: true },
    ],
  },
];

export function resolveInspectorValue(
  key: string,
  props: Record<string, unknown>,
): unknown {
  const parts = key.split(".");
  let current: unknown = props;
  for (const part of parts) {
    if (current && typeof current === "object" && part in (current as Record<string, unknown>)) {
      current = (current as Record<string, unknown>)[part];
    } else {
      return undefined;
    }
  }
  return current;
}

export function applyInspectorDefaults(
  props: Record<string, unknown>,
  sections: InspectorSection[],
): Record<string, unknown> {
  const result = { ...props };
  for (const section of sections) {
    for (const control of section.controls) {
      const parts = control.key.split(".");
      let current = result;
      for (let i = 0; i < parts.length - 1; i++) {
        const part = parts[i];
        if (!(part in current) || typeof current[part] !== "object") {
          current[part] = {};
        }
        current = current[part] as Record<string, unknown>;
      }
      const last = parts[parts.length - 1];
      if (!(last in current)) {
        current[last] = control.defaultValue;
      }
    }
  }
  return result;
}
