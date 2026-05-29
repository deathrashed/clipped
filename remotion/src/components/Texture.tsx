import { random, useCurrentFrame } from "remotion";
import type { ClippedRenderProps } from "../types";

export const TextureOverlay = ({ props, opacity = 0.14 }: { props: ClippedRenderProps; opacity?: number }) => {
  const frame = useCurrentFrame();
  if (props.options.effects === "clean") {
    return null;
  }

  const dots = Array.from({ length: props.options.effects === "grain" ? 90 : 34 }, (_, idx) => {
    const seed = `${props.options.seed || props.metadata.title}-${idx}`;
    return {
      left: random(`${seed}-x`) * 100,
      top: random(`${seed}-y`) * 100,
      size: 1 + random(`${seed}-s`) * 3,
      alpha: 0.08 + random(`${seed}-a`) * 0.26,
    };
  });

  return (
    <div style={{ position: "absolute", inset: 0, pointerEvents: "none", opacity }}>
      {dots.map((dot, idx) => (
        <div
          key={idx}
          style={{
            position: "absolute",
            left: `${dot.left}%`,
            top: `${dot.top}%`,
            width: dot.size,
            height: dot.size,
            background: "white",
            opacity: dot.alpha * (0.75 + Math.sin(frame / 15 + idx) * 0.25),
          }}
        />
      ))}
      <div
        style={{
          position: "absolute",
          inset: 0,
          boxShadow: "inset 0 0 180px rgba(0,0,0,0.72)",
        }}
      />
    </div>
  );
};
