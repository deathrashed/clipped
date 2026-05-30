import { useCurrentFrame } from "remotion";
import type { CSSProperties } from "react";

type TimeDisplay3DProps = {
  startTime?: number;
  endTime?: number;
  format?: "mm:ss" | "ss" | "mm:ss.dd";
  position?: "top-left" | "top-right" | "bottom-left" | "bottom-right" | "center";
  intensity?: number;
  opacity?: number;
};

export const TimeDisplay3D = ({
  startTime = 0,
  endTime = 60,
  format = "mm:ss",
  position = "bottom-right",
  intensity = 0.5,
  opacity = 1,
}: TimeDisplay3DProps) => {
  const frame = useCurrentFrame();
  const fps = 30;
  const currentSec = frame / fps;
  const progress = Math.min(1, currentSec / endTime);

  const fmt = (s: number) => {
    if (format === "ss") return `${Math.floor(s)}`;
    const m = Math.floor(s / 60);
    const sec = Math.floor(s % 60);
    if (format === "mm:ss.dd") {
      const cent = Math.floor((s % 1) * 100);
      return `${String(m).padStart(2, "0")}:${String(sec).padStart(2, "0")}.${String(cent).padStart(2, "0")}`;
    }
    return `${String(m).padStart(2, "0")}:${String(sec).padStart(2, "0")}`;
  };

  const posMap: Record<string, CSSProperties> = {
    "top-left": { top: 24, left: 24 },
    "top-right": { top: 24, right: 24 },
    "bottom-left": { bottom: 24, left: 24 },
    "bottom-right": { bottom: 24, right: 24 },
    center: { top: "50%", left: "50%", transform: "translate(-50%, -50%)" },
  };

  const style: CSSProperties = {
    position: "absolute",
    ...posMap[position],
    fontFamily: "'SpaceMono', 'SF Mono', monospace",
    fontSize: 18,
    fontWeight: 400,
    color: `rgba(255,255,255,${0.5 + progress * 0.5})`,
    opacity,
    textShadow: "0 0 10px rgba(0,0,0,0.5)",
    letterSpacing: "0.08em",
  };

  return <div style={style}>{fmt(currentSec)}</div>;
};
