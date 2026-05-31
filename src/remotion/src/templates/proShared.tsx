import React from "react";
import {
  AbsoluteFill,
  Img,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export type MusicTemplateProps = {
  title?: string;
  trackTitle?: string;
  artist?: string;
  artistName?: string;
  album?: string;
  albumName?: string;
  year?: string;
  genre?: string;
  label?: string;
  cover?: string;
  coverUrl?: string;
  albumCover?: string;
  artwork?: string;
  artistImage?: string;
  logo?: string;
};

export const getMeta = (props: MusicTemplateProps) => {
  return {
    title: props.title || props.trackTitle || "Untitled Track",
    artist: props.artist || props.artistName || "Unknown Artist",
    album: props.album || props.albumName || "",
    year: props.year || "",
    genre: props.genre || "",
    label: props.label || "",
    cover:
      props.cover ||
      props.coverUrl ||
      props.albumCover ||
      props.artwork ||
      "",
    artistImage: props.artistImage || "",
    logo: props.logo || "",
  };
};

export const fitText = (text: string, long = 24) => {
  if (!text) return "";
  return text.length > long ? text.slice(0, long - 1) + "…" : text;
};

export const CoverImage: React.FC<{
  src?: string;
  style?: React.CSSProperties;
}> = ({ src, style }) => {
  if (!src) {
    return (
      <div
        style={{
          background:
            "linear-gradient(135deg, #111827, #020617 60%, #1e293b)",
          ...style,
        }}
      />
    );
  }
  return <Img src={src} style={{ objectFit: "cover", ...style }} />;
};

export const useIntro = (delay = 0, stiffness = 90) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return spring({
    frame: Math.max(0, frame - delay),
    fps,
    config: { damping: 18, stiffness },
  });
};

export const readableShadow = {
  textShadow:
    "0 4px 20px rgba(0,0,0,0.9), 0 1px 2px rgba(0,0,0,1)",
};

export const smallCaps: React.CSSProperties = {
  letterSpacing: 5,
  textTransform: "uppercase",
  fontWeight: 700,
};
