import React from "react";

export type RimLightProps = {
  color?: string;
  opacity?: number;
  blur?: number;
  side?: "top" | "right" | "bottom" | "left" | "all";
};

export const RimLight: React.FC<RimLightProps> = ({
  color = "rgba(255, 255, 255, 0.4)",
  opacity = 0.5,
  blur = 6,
  side = "all",
}) => {
  const shadowValue = (() => {
    switch (side) {
      case "top":
        return `0 -${blur}px ${blur}px -1px ${color}`;
      case "bottom":
        return `0 ${blur}px ${blur}px -1px ${color}`;
      case "left":
        return `-${blur}px 0 ${blur}px -1px ${color}`;
      case "right":
        return `${blur}px 0 ${blur}px -1px ${color}`;
      case "all":
      default:
        return `0 0 ${blur}px 1px ${color}`;
    }
  })();

  const borderStyle = (() => {
    const defaultBorder = `1px solid ${color}`;
    switch (side) {
      case "top":
        return { borderTop: defaultBorder };
      case "bottom":
        return { borderBottom: defaultBorder };
      case "left":
        return { borderLeft: defaultBorder };
      case "right":
        return { borderRight: defaultBorder };
      case "all":
      default:
        return { border: defaultBorder };
    }
  })();

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        pointerEvents: "none",
        borderRadius: "inherit",
        opacity,
        boxShadow: shadowValue,
        mixBlendMode: "screen",
        zIndex: 5,
        ...borderStyle,
      }}
    />
  );
};
