import type { Palette } from "../lib/palette";

type FallbackArtworkProps = {
  size: number;
  palette: Palette;
  seed?: string;
};

export const FallbackArtwork = ({ size, palette, seed = "" }: FallbackArtworkProps) => {
  const hue = seed.split("").reduce((a, c) => a + c.charCodeAt(0), 0) % 360;
  const lightColor = `hsl(${hue}, 40%, 18%)`;
  const darkColor = `hsl(${hue}, 50%, 8%)`;

  return (
    <div
      style={{
        width: size,
        height: size,
        background: `
          radial-gradient(ellipse at 30% 35%, ${lightColor} 0%, ${darkColor} 60%),
          repeating-linear-gradient(
            45deg,
            transparent 0px,
            transparent 8px,
            rgba(255,255,255,0.015) 8px,
            rgba(255,255,255,0.015) 9px
          )
        `,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        position: "relative",
        overflow: "hidden",
      }}
    >
      <div
        style={{
          width: size * 0.38,
          height: size * 0.38,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${palette.accent}22 0%, transparent 70%)`,
          position: "absolute",
          top: "18%",
          right: "15%",
        }}
      />
      <div
        style={{
          width: size * 0.55,
          height: size * 0.55,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${palette.accent2}18 0%, transparent 60%)`,
          position: "absolute",
          bottom: "12%",
          left: "10%",
        }}
      />
      <div
        style={{
          width: "100%",
          height: "100%",
          background: `
            linear-gradient(
              135deg,
              transparent 40%,
              rgba(255,255,255,0.04) 50%,
              transparent 60%
            )
          `,
        }}
      />
    </div>
  );
};
