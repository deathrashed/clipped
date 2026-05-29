import type { ReactNode, CSSProperties } from "react";

/**
 * ChromeBorder — razor-thin metallic gradient border.
 * thickness: border px. Default 2.
 * radius: corner radius. Default 6.
 */
export const ChromeBorder = ({
  size,
  thickness = 2,
  radius = 6,
  children,
  style,
}: {
  size: number;
  thickness?: number;
  radius?: number;
  children?: ReactNode;
  style?: CSSProperties;
}) => (
  <div
    style={{
      width: size,
      height: size,
      padding: thickness,
      background: "conic-gradient(from 135deg, #888 0%, #fff 25%, #aaa 50%, #fff 75%, #888 100%)",
      borderRadius: radius + thickness,
      boxShadow: "0 30px 70px rgba(0,0,0,0.72)",
      ...style,
    }}
  >
    <div
      style={{
        width: "100%",
        height: "100%",
        overflow: "hidden",
        borderRadius: radius,
      }}
    >
      {children}
    </div>
  </div>
);
