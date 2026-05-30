import { Img, staticFile } from "remotion";

/**
 * VinylLabel — centered label zone with artwork and spindle hole.
 * labelScale: fraction of disc size. Default 0.34.
 */
export const VinylLabel = ({
  discSize,
  imageSrc,
  labelScale = 0.34,
}: {
  discSize: number;
  imageSrc: string | null;
  labelScale?: number;
}) => {
  const labelSize = discSize * labelScale;
  const spindleSize = discSize * 0.048;
  const src = imageSrc ? staticFile(imageSrc) : null;

  return (
    <>
      {/* Label disk */}
      <div
        style={{
          position: "absolute",
          left: "50%",
          top: "50%",
          width: labelSize,
          height: labelSize,
          transform: "translate(-50%, -50%)",
          borderRadius: "50%",
          overflow: "hidden",
          background: "#111",
          boxShadow: "0 0 20px rgba(0,0,0,0.6)",
        }}
      >
        {src ? (
          <Img src={src} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
        ) : null}
      </div>
      {/* Spindle hole */}
      <div
        style={{
          position: "absolute",
          left: "50%",
          top: "50%",
          width: spindleSize,
          height: spindleSize,
          transform: "translate(-50%, -50%)",
          borderRadius: "50%",
          background: "#080808",
          boxShadow: "inset 0 0 8px rgba(255,255,255,0.18)",
          zIndex: 2,
        }}
      />
    </>
  );
};
