import type { ReactNode } from "react";
import { AbsoluteFill, interpolate, random, useCurrentFrame, useVideoConfig } from "remotion";
import type { Palette } from "../lib/palette";
import type { ClippedRenderProps } from "../types";
import { motionFactor } from "../lib/palette";
import { useAudioReactive } from "../hooks/useAudioReactive";

export const Vignette = ({ opacity = 0.72 }: { opacity?: number }) => (
  <AbsoluteFill
    style={{
      pointerEvents: "none",
      background: `radial-gradient(circle at center, transparent 42%, rgba(0,0,0,${opacity}) 100%)`,
    }}
  />
);

export const FilmGrain = ({ opacity = 0.09, cells = 150 }: { opacity?: number; cells?: number }) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ pointerEvents: "none", opacity, mixBlendMode: "screen" }}>
      {Array.from({ length: cells }).map((_, idx) => {
        const x = random(`grain-x-${idx}-${frame % 3}`) * 100;
        const y = random(`grain-y-${idx}-${frame % 5}`) * 100;
        const alpha = 0.18 + random(`grain-a-${idx}-${frame % 7}`) * 0.38;
        return (
          <div
            key={idx}
            style={{
              position: "absolute",
              left: `${x}%`,
              top: `${y}%`,
              width: 1 + random(`grain-w-${idx}`) * 2,
              height: 1 + random(`grain-h-${idx}`) * 2,
              background: `rgba(255,255,255,${alpha})`,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

export const Scanlines = ({ opacity = 0.13 }: { opacity?: number }) => (
  <AbsoluteFill
    style={{
      pointerEvents: "none",
      opacity,
      backgroundImage: "linear-gradient(rgba(255,255,255,0.22) 1px, transparent 1px)",
      backgroundSize: "100% 5px",
      mixBlendMode: "screen",
    }}
  />
);

import { LightSweep } from "./LightSweep";
export { LightSweep };

export const ReactiveHalo = ({
  props,
  palette,
  size,
  y = 0,
  opacity = 0.38,
}: {
  props: ClippedRenderProps;
  palette: Palette;
  size: number;
  y?: number;
  opacity?: number;
}) => {
  const audio = useAudioReactive(props.assets.audioSrc, 96, props.options.seed);
  const motion = motionFactor(props.options.motion);
  const scale = 1 + audio.bass * 0.14 * motion;
  return (
    <div
      style={{
        position: "absolute",
        left: "50%",
        top: "50%",
        width: size,
        height: size,
        borderRadius: "50%",
        transform: `translate(-50%, calc(-50% + ${y}px)) scale(${scale})`,
        background: `radial-gradient(circle, ${palette.accent}34 0%, ${palette.accent2}18 32%, transparent 70%)`,
        filter: `blur(${22 + audio.full * 34}px)`,
        opacity,
        mixBlendMode: "screen",
      }}
    />
  );
};

export const BeatFlash = ({
  props,
  palette,
  intensity = 0.16,
}: {
  props: ClippedRenderProps;
  palette: Palette;
  intensity?: number;
}) => {
  const audio = useAudioReactive(props.assets.audioSrc, 64, props.options.seed);
  const opacity = Math.max(0, audio.bass - 0.42) * intensity;
  return (
    <AbsoluteFill
      style={{
        pointerEvents: "none",
        opacity,
        background: `radial-gradient(circle at center, ${palette.accent2}, transparent 62%)`,
        mixBlendMode: "screen",
      }}
    />
  );
};

export const CameraShake = ({
  props,
  strength = 10,
  children,
}: {
  props: ClippedRenderProps;
  strength?: number;
  children: ReactNode;
}) => {
  const frame = useCurrentFrame();
  const audio = useAudioReactive(props.assets.audioSrc, 64, props.options.seed);
  const amount = audio.bass * strength * motionFactor(props.options.motion);
  const x = Math.sin(frame * 0.61) * amount;
  const y = Math.cos(frame * 0.49) * amount * 0.75;
  return <div style={{ position: "absolute", inset: 0, transform: `translate(${x}px, ${y}px)` }}>{children}</div>;
};

export const PostFxStack = ({
  props,
  palette,
  grainOpacity = 0.08,
}: {
  props: ClippedRenderProps;
  palette: Palette;
  grainOpacity?: number;
}) => {
  const effects = String(props.options.effects || "texture");
  const wantsCrt = ["crt", "vhs", "metal_vhs"].includes(effects);
  const wantsHeavy = ["vhs", "metal_vhs", "doom"].includes(effects);
  return (
    <>
      {wantsCrt ? <Scanlines opacity={wantsHeavy ? 0.18 : 0.11} /> : null}
      {wantsHeavy ? <VHSTears opacity={0.7} palette={palette} /> : null}
      <Vignette opacity={wantsHeavy ? 0.9 : 0.66} />
      {effects !== "clean" ? <FilmGrain opacity={effects === "grain" ? 0.16 : grainOpacity} cells={wantsHeavy ? 230 : 150} /> : null}
      {wantsHeavy ? <BeatFlash props={props} palette={palette} intensity={0.22} /> : null}
    </>
  );
};

/** VHSTears — horizontal tracking glitch tears */
export const VHSTears = ({
  opacity = 0.6,
  palette,
  tearCount = 3,
}: {
  opacity?: number;
  palette: Palette;
  tearCount?: number;
}) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ pointerEvents: "none", opacity, mixBlendMode: "screen" }}>
      {Array.from({ length: tearCount }).map((_, i) => {
        const seed = (i + 1) * 137;
        const y = ((frame * seed * 0.023 + i * 33) % 100);
        const height = 1 + ((frame * seed * 0.011 + i * 17) % 5);
        const shift = ((frame * seed * 0.031 + i * 11) % 40) - 20;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: 0,
              right: 0,
              top: `${y}%`,
              height,
              background: palette.accent + "44",
              transform: `translateX(${shift}px)`,
              filter: "blur(1px)",
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

/** ChromaticAberration — RGB channel split for psychedelic/glitch look */
export const ChromaticAberration = ({
  strength = 6,
  opacity = 0.55,
}: {
  strength?: number;
  opacity?: number;
}) => {
  const frame = useCurrentFrame();
  const shift = Math.sin(frame / 8) * strength;
  return (
    <AbsoluteFill style={{ pointerEvents: "none", opacity, mixBlendMode: "screen" }}>
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: "linear-gradient(90deg, rgba(255,0,0,0.08), transparent 40%, rgba(0,0,255,0.08))",
          transform: `translateX(${shift}px)`,
        }}
      />
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: "linear-gradient(90deg, rgba(0,255,0,0.06), transparent 50%, rgba(255,0,0,0.06))",
          transform: `translateX(${-shift * 0.5}px)`,
        }}
      />
    </AbsoluteFill>
  );
};

/** StarField — particle/star field background scene */
export const StarField = ({
  starCount = 200,
  speed = 0.4,
  opacity = 0.92,
}: {
  starCount?: number;
  speed?: number;
  opacity?: number;
}) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ pointerEvents: "none", opacity, backgroundColor: "black" }}>
      {Array.from({ length: starCount }).map((_, i) => {
        const seed = i * 137.508 + 0.618;
        const x = (seed * 73.1) % 100;
        const baseY = (seed * 41.7) % 100;
        const size = 0.8 + (seed % 2.4);
        const yMoved = (baseY + frame * speed * (0.3 + (i % 5) * 0.12)) % 100;
        const twinkle = 0.4 + 0.6 * Math.abs(Math.sin(frame / 18 + i));
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: `${x}%`,
              top: `${yMoved}%`,
              width: size,
              height: size,
              borderRadius: "50%",
              background: "white",
              opacity: twinkle,
              boxShadow: size > 2 ? `0 0 ${size * 2}px white` : undefined,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

/** NeonTunnel — animated concentric neon rectangles giving depth/tunnel feel */
export const NeonTunnel = ({
  palette,
  rings = 8,
  speed = 0.7,
  opacity = 0.55,
}: {
  palette: Palette;
  rings?: number;
  speed?: number;
  opacity?: number;
}) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ pointerEvents: "none", opacity }}>
      {Array.from({ length: rings }).map((_, i) => {
        const phase = ((frame * speed * 0.018) + (i / rings)) % 1;
        const scale = 0.12 + phase * 1.6;
        const ringOpacity = (1 - phase) * 0.55;
        const color = i % 2 === 0 ? palette.accent : palette.accent2;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              inset: "50%",
              width: `${scale * 100}%`,
              height: `${scale * 100}%`,
              transform: "translate(-50%, -50%)",
              border: `2px solid ${color}`,
              borderRadius: 12,
              opacity: ringOpacity,
              boxShadow: `0 0 18px ${color}66, inset 0 0 18px ${color}22`,
              mixBlendMode: "screen",
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

/** FilmBurn — hot orange/white vignette flash, great for transitions */
export const FilmBurn = ({
  progress = 0,
  color = "rgba(255, 140, 30, 0.9)",
}: {
  progress?: number;
  color?: string;
}) => {
  if (progress <= 0 || progress >= 1) return null;
  const peak = 1 - Math.abs(progress - 0.5) * 2;
  return (
    <AbsoluteFill
      style={{
        pointerEvents: "none",
        opacity: peak * 0.88,
        background: `radial-gradient(ellipse at center, ${color} 0%, transparent 72%)`,
        mixBlendMode: "screen",
      }}
    />
  );
};
