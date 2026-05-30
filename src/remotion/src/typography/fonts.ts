import { delayRender, continueRender, staticFile } from "remotion";

const localFonts = [
  // Inter
  { name: "Inter", src: "fonts/Inter/Inter-Regular.woff2", weight: "400" },
  { name: "Inter", src: "fonts/Inter/Inter-Medium.woff2", weight: "500" },
  { name: "Inter", src: "fonts/Inter/Inter-SemiBold.woff2", weight: "600" },
  { name: "Inter", src: "fonts/Inter/Inter-Bold.woff2", weight: "700" },
  // Oswald
  { name: "Oswald", src: "fonts/Oswald/Oswald-Regular.woff2", weight: "400" },
  { name: "Oswald", src: "fonts/Oswald/Oswald-Medium.woff2", weight: "500" },
  { name: "Oswald", src: "fonts/Oswald/Oswald-Bold.woff2", weight: "700" },
  // Bebas Neue
  { name: "Bebas Neue", src: "fonts/BebasNeue/BebasNeue-Regular.woff2", weight: "400" },
  // Space Mono
  { name: "Space Mono", src: "fonts/SpaceMono/SpaceMono-Regular.woff2", weight: "400" },
  { name: "Space Mono", src: "fonts/SpaceMono/SpaceMono-Bold.woff2", weight: "700" },
];

// Load local fonts programmatically in the browser environment
if (typeof window !== "undefined" && typeof window.FontFace !== "undefined") {
  localFonts.forEach((fontSpec) => {
    const font = new FontFace(
      fontSpec.name,
      `url(${staticFile(fontSpec.src)})`,
      { weight: fontSpec.weight }
    );
    font.load()
      .then((loadedFace) => {
        try {
          document.fonts.add(loadedFace);
        } catch (e) {}
      })
      .catch((err) => {
        console.warn(`Failed to load font ${fontSpec.name} (${fontSpec.src}) gracefully falling back.`, err);
      });
  });
}

/**
 * Font family strings keyed by role with robust local system fallbacks.
 */
export const fonts = {
  display: "'Oswald', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
  brutal: "'Bebas Neue', Impact, 'Arial Black', sans-serif",
  body: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
  mono: "'Space Mono', Monaco, Consolas, 'Courier New', monospace",
} as const;

/**
 * Resolve fontFamily string from the token role + typography preset context.
 */
export const resolveFont = (
  role: "display" | "body" | "mono",
  isBrutal = false,
): string => {
  if (role === "display") return isBrutal ? fonts.brutal : fonts.display;
  if (role === "mono") return fonts.mono;
  return fonts.body;
};
