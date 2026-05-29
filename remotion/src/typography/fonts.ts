// Font loading for Clipped typography system.
// loadFont() must be called at module top level — Remotion injects the CSS.
// Import { fonts } in any component that uses text.

import { loadFont as loadInter } from "@remotion/google-fonts/Inter";
import { loadFont as loadOswald } from "@remotion/google-fonts/Oswald";
import { loadFont as loadBebasNeue } from "@remotion/google-fonts/BebasNeue";
import { loadFont as loadSpaceMono } from "@remotion/google-fonts/SpaceMono";

const inter = loadInter("normal", {
  weights: ["400", "500", "600", "700"],
  subsets: ["latin"],
});
const oswald = loadOswald("normal", {
  weights: ["400", "500", "700"],
  subsets: ["latin"],
});
const bebas = loadBebasNeue("normal", {
  weights: ["400"],
  subsets: ["latin"],
});
const spaceMono = loadSpaceMono("normal", {
  weights: ["400", "700"],
  subsets: ["latin"],
});

/**
 * Font family strings keyed by role.
 * "display" → Oswald (editorial/cinematic) or Bebas Neue (brutal)
 * "body"    → Inter
 * "mono"    → Space Mono (VHS/CRT)
 *
 * Usage: style={{ fontFamily: fonts.display }}
 */
export const fonts = {
  display:  oswald.fontFamily,
  brutal:   bebas.fontFamily,
  body:     inter.fontFamily,
  mono:     spaceMono.fontFamily,
} as const;

/**
 * Resolve fontFamily string from the token role + typography preset context.
 * "display" uses brutal face for brutal preset, oswald otherwise.
 */
export const resolveFont = (
  role: "display" | "body" | "mono",
  isBrutal = false,
): string => {
  if (role === "display") return isBrutal ? fonts.brutal : fonts.display;
  if (role === "mono") return fonts.mono;
  return fonts.body;
};
