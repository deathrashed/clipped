import type { ClippedRenderProps } from "../types";
import type { Palette } from "../lib/palette";

export const Stage3DHint = ({ props, palette }: { props: ClippedRenderProps; palette: Palette }) => {
  if (props.options.style !== "cinematic") {
    return null;
  }
  return (
    <div
      style={{
        position: "absolute",
        inset: "16% 9%",
        border: `1px solid ${palette.accent}44`,
        transform: "perspective(900px) rotateX(8deg)",
        boxShadow: `0 0 90px ${palette.accent}22`,
        pointerEvents: "none",
      }}
    />
  );
};
