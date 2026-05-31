import React from "react";
import {
  AbsoluteFill,
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

const Field: React.FC<{ label: string; value?: string; delay: number }> = ({
  label,
  value,
  delay,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = useIntro(delay, 90);

  if (!value) return null;

  return (
    <div
      style={{
        opacity: interpolate(p, [0, 1], [0, 1]),
        transform: `translateX(${interpolate(p, [0, 1], [34, 0])}px)`,
        marginBottom: 34,
      }}
    >
      <div
        style={{
          fontSize: 22,
          color: "rgba(255,255,255,0.45)",
          ...smallCaps,
        }}
      >
        {label}
      </div>
      <div
        style={{
          marginTop: 8,
          fontSize: 42,
          lineHeight: 1.05,
          color: "rgba(255,255,255,0.9)",
          fontWeight: 650,
        }}
      >
        {value}
      </div>
    </div>
  );
};

export const ProArchiveCard: React.FC<MusicTemplateProps> = (props) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const meta = getMeta(props);
  const coverIn = useIntro(18, 100);

  return (
    <AbsoluteFill
      style={{
        background: "#06070a",
        overflow: "hidden",
        color: "white",
        fontFamily:
          "Inter, SF Pro Display, Helvetica Neue, Arial, sans-serif",
      }}
    >
      <CoverImage
        src={meta.cover}
        style={{
          position: "absolute",
          inset: 0,
          width: "100%",
          height: "100%",
          filter: "blur(55px) brightness(0.32) saturate(1.15)",
          transform: `scale(${interpolate(frame, [0, durationInFrames], [1.05, 1.13])})`,
        }}
      />

      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "linear-gradient(135deg, rgba(0,0,0,0.2), rgba(0,0,0,0.86) 58%, rgba(0,0,0,0.94))",
        }}
      />

      <div
        style={{
          position: "absolute",
          top: 180,
          left: 80,
          width: 610,
          height: 610,
          borderRadius: 28,
          overflow: "hidden",
          boxShadow:
            "0 40px 100px rgba(0,0,0,0.65), 0 0 0 1px rgba(255,255,255,0.14)",
          opacity: interpolate(coverIn, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(coverIn, [0, 1], [60, 0])}px)`,
        }}
      >
        <CoverImage src={meta.cover} style={{ width: "100%", height: "100%" }} />
      </div>

      <div
        style={{
          position: "absolute",
          left: 80,
          right: 80,
          top: 870,
          ...readableShadow,
        }}
      >
        <div style={{ fontSize: 24, ...smallCaps, color: "#9ca3af" }}>
          Track
        </div>
        <div
          style={{
            marginTop: 10,
            fontSize: 72,
            lineHeight: 0.98,
            fontWeight: 800,
          }}
        >
          {fitText(meta.title, 32)}
        </div>
      </div>

      <div
        style={{
          position: "absolute",
          left: 80,
          right: 80,
          top: 1135,
        }}
      >
        <Field label="Artist" value={meta.artist} delay={42} />
        <Field label="Album" value={meta.album} delay={52} />
        <div style={{ display: "flex", gap: 80 }}>
          <Field label="Year" value={meta.year} delay={62} />
          <Field label="Genre" value={meta.genre} delay={70} />
        </div>
        <Field label="Label" value={meta.label} delay={78} />
      </div>
    </AbsoluteFill>
  );
};

export default ProArchiveCard;
