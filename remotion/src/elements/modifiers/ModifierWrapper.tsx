import type { ReactNode } from "react";
import type { EffectModifierInstance } from "../types";
import { modifierDefaultProps } from "./modifier-types";
import { GlowModifier } from "./GlowModifier";
import { BlurModifier } from "./BlurModifier";
import { ShadowModifier } from "./ShadowModifier";
import { StrokeModifier } from "./StrokeModifier";
import { AdjustModifier } from "./AdjustModifier";
import { DitherModifier } from "./DitherModifier";
import { PixelateModifier } from "./PixelateModifier";
import { WobbleModifier } from "./WobbleModifier";

type ModifierWrapperProps = {
  effects?: EffectModifierInstance[];
  children: ReactNode;
};

const WARN_PREFIX = "[ModifierWrapper]";

export const ModifierWrapper = ({ effects, children }: ModifierWrapperProps) => {
  if (!effects || effects.length === 0) return <>{children}</>;

  const activeEffects = effects.filter((e) => e.enabled !== false);

  if (activeEffects.length === 0) return <>{children}</>;

  return (
    <>
      {activeEffects.reduce<ReactNode>((acc, effect) => {
        const defaults = modifierDefaultProps[effect.id] || {};
        const merged = { ...defaults, ...effect.props };

        switch (effect.id) {
          case "glow":
            return <GlowModifier key={`mod-${effect.id}`} {...merged}>{acc}</GlowModifier>;
          case "blur":
            return <BlurModifier key={`mod-${effect.id}`} {...merged}>{acc}</BlurModifier>;
          case "shadow":
            return <ShadowModifier key={`mod-${effect.id}`} {...merged}>{acc}</ShadowModifier>;
          case "stroke":
            return <StrokeModifier key={`mod-${effect.id}`} {...merged}>{acc}</StrokeModifier>;
          case "adjust":
            return <AdjustModifier key={`mod-${effect.id}`} {...merged}>{acc}</AdjustModifier>;
          case "dither":
            return <DitherModifier key={`mod-${effect.id}`} {...merged}>{acc}</DitherModifier>;
          case "pixelate":
            return <PixelateModifier key={`mod-${effect.id}`} {...merged}>{acc}</PixelateModifier>;
          case "wobble":
            return <WobbleModifier key={`mod-${effect.id}`} {...merged}>{acc}</WobbleModifier>;
          default:
            console.warn(WARN_PREFIX, `Unknown modifier "${effect.id}" — skipping.`);
            return acc;
        }
      }, children)}
    </>
  );
};
