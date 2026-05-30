import { Audio, staticFile } from "remotion";
import type { ClippedRenderProps } from "../types";

export const AudioLayer = ({ props }: { props: ClippedRenderProps }) => {
  if (!props.assets.audioSrc) {
    return null;
  }
  return <Audio src={staticFile(props.assets.audioSrc)} volume={props.audio.volume ?? 1} />;
};
