#!/usr/bin/env node
import { existsSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const publicDir = resolve(__dirname, "..", "public");

const expectedFonts = [
  ["Anton", "Anton-Regular.woff2", "400"],
  ["Barlow", "Barlow-Regular.woff2", "400"],
  ["Barlow", "Barlow-SemiBold.woff2", "600"],
  ["Barlow", "Barlow-Bold.woff2", "700"],
  ["BebasNeue", "BebasNeue-Regular.woff2", "400"],
  ["BebasNeue", "BebasNeue-Bold.woff2", "700"],
  ["Exo2", "Exo2-Regular.woff2", "400"],
  ["Exo2", "Exo2-Medium.woff2", "500"],
  ["Exo2", "Exo2-Bold.woff2", "700"],
  ["Impact", "Impact.woff2", "400"],
  ["Inter", "Inter-Thin.woff2", "100"],
  ["Inter", "Inter-ExtraLight.woff2", "200"],
  ["Inter", "Inter-Light.woff2", "300"],
  ["Inter", "Inter-Regular.woff2", "400"],
  ["Inter", "Inter-Medium.woff2", "500"],
  ["Inter", "Inter-SemiBold.woff2", "600"],
  ["Inter", "Inter-Bold.woff2", "700"],
  ["Inter", "Inter-ExtraBold.woff2", "800"],
  ["Inter", "Inter-Black.woff2", "900"],
  ["Molot", "Molot.woff2", "400"],
  ["Montserrat", "Montserrat-Regular.woff2", "400"],
  ["Montserrat", "Montserrat-Medium.woff2", "500"],
  ["Montserrat", "Montserrat-SemiBold.woff2", "600"],
  ["Montserrat", "Montserrat-Bold.woff2", "700"],
  ["Oswald", "Oswald-ExtraLight.woff2", "200"],
  ["Oswald", "Oswald-Light.woff2", "300"],
  ["Oswald", "Oswald-Regular.woff2", "400"],
  ["Oswald", "Oswald-Medium.woff2", "500"],
  ["Oswald", "Oswald-SemiBold.woff2", "600"],
  ["Oswald", "Oswald-Bold.woff2", "700"],
  ["Oswald", "Oswald-Heavy.woff2", "800"],
  ["PeaceSans", "PeaceSans.woff2", "400"],
  ["Poppins", "Poppins-Regular.woff2", "400"],
  ["Poppins", "Poppins-Medium.woff2", "500"],
  ["Poppins", "Poppins-SemiBold.woff2", "600"],
  ["Poppins", "Poppins-Bold.woff2", "700"],
  ["Roboto", "Roboto-Regular.woff2", "400"],
  ["Roboto", "Roboto-Medium.woff2", "500"],
  ["Roboto", "Roboto-Bold.woff2", "700"],
  ["Russo", "RussoOne-Regular.woff2", "400"],
  ["SF", "SF-Compact-Text-Black.woff2", "900"],
  ["SF", "SF-Pro-Text-Semibold.woff2", "600"],
  ["SpaceMono", "SpaceMono-Regular.woff2", "400"],
  ["SpaceMono", "SpaceMono-Italic.woff2", "400"],
  ["SpaceMono", "SpaceMono-Bold.woff2", "700"],
  ["SpaceMono", "SpaceMono-BoldItalic.woff2", "700"],
];

const strict = process.argv.includes("--strict");
let missingCount = 0;

console.log("Checking local font files...\n");

for (const [family, file, weight] of expectedFonts) {
  const fontPath = resolve(publicDir, "fonts", family, file);
  const relPath = `public/fonts/${family}/${file}`;
  if (existsSync(fontPath)) {
    console.log(`  ✓ ${relPath} (weight ${weight})`);
  } else {
    console.log(`  ✗ ${relPath} (weight ${weight}) — MISSING`);
    missingCount++;
  }
}

const total = expectedFonts.length;
const found = total - missingCount;

console.log(`\n${found}/${total} font files found.`);

if (missingCount > 0) {
  console.log("\nMissing fonts will fall back to system font stacks.");
  console.log("See public/fonts/README.md for expected file layout.");
  if (strict) {
    process.exit(1);
  }
} else {
  console.log("All local fonts are available for offline rendering.");
}
