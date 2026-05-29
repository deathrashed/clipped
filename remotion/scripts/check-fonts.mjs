#!/usr/bin/env node
import { existsSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const publicDir = resolve(__dirname, "..", "public");

const expectedFonts = [
  ["Inter", "Inter-Regular.woff2", "400"],
  ["Inter", "Inter-Medium.woff2", "500"],
  ["Inter", "Inter-SemiBold.woff2", "600"],
  ["Inter", "Inter-Bold.woff2", "700"],
  ["Oswald", "Oswald-Regular.woff2", "400"],
  ["Oswald", "Oswald-Medium.woff2", "500"],
  ["Oswald", "Oswald-Bold.woff2", "700"],
  ["BebasNeue", "BebasNeue-Regular.woff2", "400"],
  ["SpaceMono", "SpaceMono-Regular.woff2", "400"],
  ["SpaceMono", "SpaceMono-Bold.woff2", "700"],
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
