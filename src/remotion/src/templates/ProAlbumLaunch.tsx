import React from "react";
import {
  AbsoluteFill,
  Img,
  interpolate,
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

export const ProAlbumLaunch: React.FC<MusicTemplateProps> = (props) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const meta = getMeta(props);

  const intro = useIntro(8);
  const card = useIntro(32);
  const details = useIntro(58);

  const bgScale = interpolate(frame, [0, durationInFrames], [1.06, 1.16]);
  const coverY = interpolate(card, [0, 1], [80, 0]);
  const coverOpacity = interpolate(card, [0, 1], [0, 1]);
  const detailY = interpolate(details, [0, 1], [40, 0]);

  return (
    <AbsoluteFill
      style={{
        background: "#050505",
        overflow: "hidden",
        fontFamily:
          "Inter, SF Pro Display, Helvetica Neue, Arial, sans-serif",
        color: "white",
      }}
    >
      <CoverImage
        src={meta.cover}
        style={{
          position: "absolute",
          inset: 0,
          width: "100%",
          height: "100%",
          filter: "blur(42px) brightness(0.42) saturate(1.2)",
          transform: `scale(${bgScale})`,
        }}
      />

      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "radial-gradient(circle at 50% 32%, rgba(255,255,255,0.13), transparent 34%), linear-gradient(to bottom, rgba(0,0,0,0.2), rgba(0,0,0,0.88))",
        }}
      />

      {meta.logo ? (
        <Img
          src={meta.logo}
          style={{
            position: "absolute",
            top: 130,
            left: 190,
            width: 700,
            height: 220,
            objectFit: "contain",
            opacity: interpolate(intro, [0, 1], [0, 0.92]),
            transform: `translateY(${interpolate(intro, [0, 1], [-35, 0])}px)`,
            filter: "drop-shadow(0 10px 35px rgba(0,0,0,0.85))",
          }}
        />
      ) : (
        <div
          style={{
            position: "absolute",
            top: 165,
            width: "100%",
            textAlign: "center",
            fontSize: 36,
            ...smallCaps,
            ...readableShadow,
            opacity: interpolate(intro, [0, 1], [0, 1]),
          }}
        >
          {meta.artist}
        </div>
      )}

      <div
        style={{
          position: "absolute",
          top: 430 + coverY,
          left: 145,
          width: 790,
          height: 790,
          borderRadius: 34,
          overflow: "hidden",
          boxShadow:
            "0 45px 110px rgba(0,0,0,0.65), 0 0 0 1px rgba(255,255,255,0.14)",
          opacity: coverOpacity,
        }}
      >
        <CoverImage src={meta.cover} style={{ width: "100%", height: "100%" }} />
      </div>

      <div
        style={{
          position: "absolute",
          left: 90,
          right: 90,
          top: 1320 + detailY,
          opacity: interpolate(details, [0, 1], [0, 1]),
          textAlign: "center",
        }}
      >
        <div
          style={{
            fontSize: 72,
            lineHeight: 1.02,
            fontWeight: 800,
            ...readableShadow,
          }}
        >
          {fitText(meta.title, 34)}
        </div>

        <div
          style={{
            marginTop: 30,
            fontSize: 44,
            color: "rgba(255,255,255,0.78)",
            ...readableShadow,
          }}
        >
          {meta.artist}
        </div>

        <div
          style={{
            marginTop: 42,
            display: "flex",
            justifyContent: "center",
            gap: 18,
            flexWrap: "wrap",
            color: "rgba(255,255,255,0.66)",
            fontSize: 28,
          }}
        >
          {meta.album && <span>{meta.album}</span>}
          {meta.year && <span>• {meta.year}</span>}
          {meta.genre && <span>• {meta.genre}</span>}
        </div>
      </div>
    </AbsoluteFill>
  );
};

export default ProAlbumLaunch;
