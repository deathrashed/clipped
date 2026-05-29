import type { ReactNode } from "react";
import { MatteBorder } from "./MatteBorder";
import { ChromeBorder } from "./ChromeBorder";

export type FramePreset = "none" | "matte" | "chrome" | "vinyl-sleeve";

/**
 * ArtworkFrame — wraps children in the selected frame material.
 * size: frame outer dimension in px.
 * preset: frame style.
 */
export const ArtworkFrame = ({
  size,
  preset = "matte",
  children,
}: {
  size: number;
  preset?: FramePreset;
  children: ReactNode;
}) => {
  if (preset === "matte") {
    return <MatteBorder size={size}>{children}</MatteBorder>;
  }
  if (preset === "chrome") {
    return <ChromeBorder size={size}>{children}</ChromeBorder>;
  }
  // "none" or "vinyl-sleeve" — bare (sleeve is rendered separately)
  return (
    <div
      style={{
        width: size,
        height: size,
        overflow: "hidden",
        borderRadius: 6,
        boxShadow: "0 36px 90px rgba(0,0,0,0.72)",
      }}
    >
      {children}
    </div>
  );
};
