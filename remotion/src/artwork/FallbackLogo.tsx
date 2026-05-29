import type { CSSProperties } from "react";

type FallbackLogoProps = {
  text: string;
  maxWidth: number;
  style?: CSSProperties;
};

export const FallbackLogo = ({ text, maxWidth, style }: FallbackLogoProps) => {
  const initials = text
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 3)
    .map((w) => w[0])
    .join("")
    .toUpperCase();

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        width: Math.min(maxWidth, 320),
        ...style,
      }}
    >
      <span
        style={{
          fontFamily: "'Oswald', -apple-system, BlinkMacSystemFont, sans-serif",
          fontSize: initials.length <= 2 ? 72 : 52,
          fontWeight: 500,
          letterSpacing: "0.2em",
          color: "rgba(255,255,255,0.9)",
          textShadow: "0 2px 20px rgba(0,0,0,0.5)",
          lineHeight: 1,
          textAlign: "center",
        }}
      >
        {initials}
      </span>
    </div>
  );
};
