import type { CSSProperties } from "react";

type AmbientLightLayerProps = {
  color?: string;
  intensity?: number;
  spread?: number;
  position?: { x: number; y: number };
};

export const AmbientLightLayer = ({
  color = "#ffaa44",
  intensity = 0.15,
  spread = 50,
  position = { x: 50, y: 50 },
}: AmbientLightLayerProps) => {
  const style: CSSProperties = {
    position: "absolute",
    inset: 0,
    pointerEvents: "none",
    background: `radial-gradient(ellipse at ${position.x}% ${position.y}%, ${color} 0%, transparent ${spread}%)`,
    opacity: intensity,
    mixBlendMode: "overlay",
  };
  return <div style={style} />;
};

type PointLightLayerProps = {
  color?: string;
  intensity?: number;
  radius?: number;
  positions?: Array<{ x: number; y: number }>;
};

export const PointLightLayer = ({
  color = "#ffffff",
  intensity = 0.1,
  radius = 30,
  positions = [{ x: 50, y: 50 }],
}: PointLightLayerProps) => {
  const gradients = positions
    .map(
      (p, i) =>
        `radial-gradient(circle at ${p.x}% ${p.y}%, ${color} 0%, transparent ${radius}%)${i < positions.length - 1 ? ", " : ""}`
    )
    .join("");

  const style: CSSProperties = {
    position: "absolute",
    inset: 0,
    pointerEvents: "none",
    background: gradients,
    opacity: intensity,
    mixBlendMode: "screen",
  };
  return <div style={style} />;
};

type LightPresetProps = {
  preset?: "warm-glow" | "cool-rim" | "golden-hour" | "neon-tunnel" | "studio";
  intensity?: number;
};

export const LightPreset = ({
  preset = "warm-glow",
  intensity = 0.5,
}: LightPresetProps) => {
  const presets: Record<string, { ambient: AmbientLightLayerProps; points: PointLightLayerProps }> = {
    "warm-glow": {
      ambient: { color: "#ff8844", intensity: 0.12 * intensity, spread: 60 },
      points: {
        color: "#ffcc66",
        intensity: 0.08 * intensity,
        radius: 25,
        positions: [{ x: 50, y: 30 }],
      },
    },
    "cool-rim": {
      ambient: { color: "#4488ff", intensity: 0.1 * intensity, spread: 40, position: { x: 10, y: 10 } },
      points: {
        color: "#66aaff",
        intensity: 0.06 * intensity,
        radius: 20,
        positions: [
          { x: 10, y: 10 },
          { x: 90, y: 10 },
        ],
      },
    },
    "golden-hour": {
      ambient: { color: "#ff7744", intensity: 0.15 * intensity, spread: 45, position: { x: 30, y: 20 } },
      points: {
        color: "#ffaa44",
        intensity: 0.1 * intensity,
        radius: 35,
        positions: [{ x: 30, y: 20 }],
      },
    },
    "neon-tunnel": {
      ambient: { color: "#ff00ff", intensity: 0.08 * intensity, spread: 50 },
      points: {
        color: "#00ffff",
        intensity: 0.12 * intensity,
        radius: 30,
        positions: [
          { x: 20, y: 50 },
          { x: 80, y: 50 },
        ],
      },
    },
    studio: {
      ambient: { color: "#ffffff", intensity: 0.05 * intensity, spread: 30, position: { x: 50, y: 10 } },
      points: {
        color: "#ffffff",
        intensity: 0.15 * intensity,
        radius: 40,
        positions: [
          { x: 20, y: 30 },
          { x: 80, y: 30 },
        ],
      },
    },
  };

  const cfg = presets[preset];

  return (
    <>
      <AmbientLightLayer {...cfg.ambient} />
      <PointLightLayer {...cfg.points} />
    </>
  );
};
