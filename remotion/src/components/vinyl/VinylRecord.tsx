import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import type { ClippedRenderProps } from "../../types";
import type { Palette } from "../../lib/palette";
import { VinylDisc } from "../../vinyl/VinylDisc";
import { VinylSpecular } from "../../vinyl/VinylSpecular";
import { VinylLabel } from "../../vinyl/VinylLabel";
import { VinylReflection } from "../../vinyl/VinylReflection";

export const VinylRecord = ({
  props,
  palette,
  size,
  y = 0,
  labelScale = 0.34,
  revealFrame = 0,
}: {
  props: ClippedRenderProps;
  palette: Palette;
  size: number;
  y?: number;
  labelScale?: number;
  revealFrame?: number;
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const reveal = spring({ frame: frame - revealFrame, fps, config: { damping: 20, stiffness: 85 } });

  return (
    <div
      style={{
        position: "absolute",
        left: "50%",
        top: "50%",
        width: size,
        height: size,
        transform: `translate(-50%, calc(-50% + ${y}px)) scale(${reveal})`,
      }}
    >
      <VinylReflection size={size} y={0} opacity={0.14} />
      <VinylDisc size={size} motion={props.options.motion}>
        <VinylLabel discSize={size} imageSrc={props.assets.coverSrc} labelScale={labelScale} />
      </VinylDisc>
      <VinylSpecular size={size} motion={props.options.motion} />
    </div>
  );
};
