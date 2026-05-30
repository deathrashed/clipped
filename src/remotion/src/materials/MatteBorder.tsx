import type { ReactNode, CSSProperties } from "react";

/**
 * MatteBorder — warm off-white matte frame around artwork.
 * thickness: border px. Default 10.
 * color: matte color. Default warm off-white.
 * radius: corner radius of inner content. Default 4.
 */
export const MatteBorder = ({
  size,
  thickness = 10,
  color = "#f2ede6",
  radius = 4,
  children,
  style,
}: {
  size: number;
  thickness?: number;
  color?: string;
  radius?: number;
  children?: ReactNode;
  style?: CSSProperties;
}) => (
  <div
    style={{
      width: size,
      height: size,
      padding: thickness,
      backgroundColor: color,
      borderRadius: radius + thickness,
      boxShadow: "0 40px 80px rgba(0,0,0,0.72)",
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
