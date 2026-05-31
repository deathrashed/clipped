import React from "react";
import {
  AbsoluteFill,
  Img,
  interpolate,
  random,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import {
  CoverImage,
  MusicTemplateProps,
  fitText,
  getMeta,
  readableShadow,
  smallCaps,
  useIntro,
} from "./proShared";

export const ProMetalVHS: React.FC<MusicTemplateProps> = (props) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const meta = getMeta(props);

  const coverIn = useIntro(22, 120);
  const titleIn = useIntro(48, 110);
  const jitter = (random(frame) - 0.5) * 10;
  const scan = (frame * 9) % 1920;

  return (
    <AbsoluteFill
      style={{
        background: "#020202",
        overflow: "hidden",
        color: "white",
        fontFamily:
          "Impact, Haettenschweiler, Arial Black, Helvetica, sans-serif",
      }}
    >
      <CoverImage
        src={meta.cover}
        style={{
          position: "absolute",
          inset: 0,
          width: "100%",
          height: "100%",
          filter:
            "blur(28px) brightness(0.28) contrast(1.45) saturate(0.7)",
          transform: `scale(${interpolate(frame, [0, durationInFrames], [1.08, 1.22])})`,
        }}
      />

      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "linear-gradient(to bottom, rgba(0,0,0,0.2), rgba(0,0,0,0.7)), repeating-linear-gradient(to bottom, rgba(255,255,255,0.045) 0px, rgba(255,255,255,0.045) 1px, transparent 3px, transparent 7px)",
          mixBlendMode: "screen",
          opacity: 0.28,
        }}
      />

      <div
        style={{
          position: "absolute",
          top: scan - 160,
          left: 0,
          right: 0,
          height: 130,
          background:
            "linear-gradient(to bottom, transparent, rgba(255,255,255,0.14), transparent)",
          opacity: 0.22,
        }}
      />

      {meta.logo && (
        <Img
          src={meta.logo}
          style={{
            position: "absolute",
            top: 115,
            left: 120 + jitter,
            width: 840,
            height: 260,
            objectFit: "contain",
            opacity: 0.92,
            filter:
              "drop-shadow(4px 0 #ff003c) drop-shadow(-4px 0 #00e5ff) drop-shadow(0 12px 30px black)",
          }}
        />
      )}

      <div
        style={{
          position: "absolute",
          top: 450,
          left: 115 + jitter,
          width: 850,
          height: 850,
          overflow: "hidden",
          border: "3px solid rgba(255,255,255,0.88)",
          boxShadow:
            "0 30px 90px rgba(0,0,0,0.8), 10px 0 rgba(255,0,55,0.4), -10px 0 rgba(0,229,255,0.35)",
          opacity: interpolate(coverIn, [0, 1], [0, 1]),
          transform: `scale(${interpolate(coverIn, [0, 1], [0.86, 1])}) rotate(${interpolate(coverIn, [0, 1], [-2, 0])}deg)`,
        }}
      >
        <CoverImage src={meta.cover} style={{ width: "100%", height: "100%" }} />
      </div>

      <div
        style={{
          position: "absolute",
          left: 70,
          right: 70,
          bottom: 145,
          opacity: interpolate(titleIn, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(titleIn, [0, 1], [45, 0])}px)`,
          textAlign: "center",
          ...readableShadow,
        }}
      >
        <div
          style={{
            fontSize: 92,
            lineHeight: 0.92,
            letterSpacing: 1,
            textTransform: "uppercase",
          }}
        >
          {fitText(meta.title, 30)}
        </div>

        <div
          style={{
            marginTop: 28,
            fontFamily: "Inter, Helvetica, Arial, sans-serif",
            fontSize: 34,
            ...smallCaps,
            color: "rgba(255,255,255,0.72)",
          }}
        >
          {[meta.artist, meta.year, meta.genre].filter(Boolean).join("  /  ")}
        </div>
      </div>
    </AbsoluteFill>
  );
};

export default ProMetalVHS;
