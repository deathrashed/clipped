import type { CSSProperties } from "react";

type ShaderBackgroundProps = {
  pattern?: "grid" | "dots" | "waves" | "hex";
  color1?: string;
  color2?: string;
  intensity?: number;
};

export const ShaderBackground = ({
  pattern = "grid",
  color1 = "#1a1a2e",
  color2 = "#16213e",
  intensity = 1,
}: ShaderBackgroundProps) => {
  const patternFn = () => {
    switch (pattern) {
      case "dots":
        return `radial-gradient(circle at 25% 25%, ${color2} 0px, transparent 4px)`;
      case "waves":
        return `linear-gradient(45deg, ${color1} 0%, ${color2} 25%, ${color1} 50%, ${color2} 75%, ${color1} 100%)`;
      case "hex":
        return `repeating-linear-gradient(60deg, ${color1} 0px, ${color2} 2px, transparent 2px, transparent 20px)`;
      default:
        return `repeating-linear-gradient(0deg, transparent, transparent 19px, ${color2} 19px, ${color2} 20px), repeating-linear-gradient(90deg, transparent, transparent 19px, ${color2} 19px, ${color2} 20px)`;
    }
  };

  const style: CSSProperties = {
    position: "absolute",
    inset: 0,
    background: `${patternFn()}, ${color1}`,
    backgroundSize: pattern === "waves" ? "200% 200%" : "20px 20px",
    opacity: intensity,
  };

  return <div style={style} />;
};

type GradientBackgroundProps = {
  colors?: string[];
  direction?: "vertical" | "horizontal" | "diagonal" | "radial";
  intensity?: number;
};

export const GradientBackground = ({
  colors = ["#0f0c29", "#302b63", "#24243e"],
  direction = "vertical",
  intensity = 1,
}: GradientBackgroundProps) => {
  const dirMap: Record<string, string> = {
    vertical: "180deg",
    horizontal: "90deg",
    diagonal: "135deg",
    radial: "circle at center",
  };

  const style: CSSProperties = {
    position: "absolute",
    inset: 0,
    background: direction === "radial"
      ? `radial-gradient(${colors.join(", ")})`
      : `linear-gradient(${dirMap[direction]}, ${colors.join(", ")})`,
    opacity: intensity,
  };

  return <div style={style} />;
};

type NoiseBackgroundProps = {
  intensity?: number;
};

export const NoiseBackground = ({
  intensity = 0.05,
}: NoiseBackgroundProps) => {
  const style: CSSProperties = {
    position: "absolute",
    inset: 0,
    opacity: intensity,
    backgroundImage:
      "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\")",
    backgroundRepeat: "repeat",
    backgroundSize: "256px 256px",
  };
  return <div style={style} />;
};
