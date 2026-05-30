/**
 * VinylReflection — subtle floor reflection below the disc.
 * Renders a gradient oval shadow/reflection below the record.
 * opacity: 0.10–0.20 recommended.
 */
export const VinylReflection = ({
  size,
  y = 0,
  opacity = 0.14,
}: {
  size: number;
  y?: number;
  opacity?: number;
}) => {
  const reflectionH = size * 0.18;
  const reflectionW = size * 0.80;

  return (
    <div
      style={{
        position: "absolute",
        left: "50%",
        top: "50%",
        width: reflectionW,
        height: reflectionH,
        transform: `translate(-50%, calc(${size * 0.5 + y}px))`,
        background: "radial-gradient(ellipse at center, rgba(255,255,255,0.18) 0%, transparent 70%)",
        filter: "blur(10px)",
        opacity,
        pointerEvents: "none",
      }}
    />
  );
};
