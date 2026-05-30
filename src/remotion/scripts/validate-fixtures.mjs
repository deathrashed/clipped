import { readFileSync } from "node:fs";
import { globSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const dir = dirname(fileURLToPath(import.meta.url));
const fixturesDir = resolve(dir, "../../../data/fixtures");

const files = globSync("qa-*.json", { cwd: fixturesDir });

if (files.length === 0) {
  console.error("No qa-*.json fixture files found in data/fixtures/");
  process.exit(1);
}

let exitCode = 0;

for (const file of files) {
  const path = resolve(fixturesDir, file);
  let data;
  try {
    const raw = readFileSync(path, "utf-8");
    data = JSON.parse(raw);
  } catch (err) {
    console.error(`✗ ${file} — invalid JSON: ${err.message}`);
    exitCode = 1;
    continue;
  }

  const qaEditor = ["qa-inspector.json", "qa-transform.json", "qa-visibility.json", "qa-ordering.json", "qa-keyframes.json"];

  if (!qaEditor.includes(file)) {
    console.log(`  ${file} — skipped (unknown fixture type)`);
    continue;
  }

  if (file === "qa-inspector.json") {
    if (!Array.isArray(data.elements)) {
      console.error(`✗ ${file} — missing "elements" array`);
      exitCode = 1;
    } else {
      console.log(`✓ ${file} — ${data.elements.length} element(s)`);
    }
  } else if (file === "qa-transform.json") {
    if (!data.initialState || !Array.isArray(data.edits)) {
      console.error(`✗ ${file} — missing "initialState" or "edits"`);
      exitCode = 1;
    } else {
      console.log(`✓ ${file} — ${data.edits.length} edit(s)`);
    }
  } else if (file === "qa-visibility.json") {
    if (!Array.isArray(data.initialElements) || !Array.isArray(data.sequence)) {
      console.error(`✗ ${file} — missing "initialElements" or "sequence"`);
      exitCode = 1;
    } else {
      const allHaveInstance = data.initialElements.every(
        (el) => el.id && el.hasOwnProperty("visible") && el.hasOwnProperty("locked") && el.instance
      );
      if (!allHaveInstance) {
        console.error(`✗ ${file} — elements missing id, visible, locked, or instance`);
        exitCode = 1;
      } else {
        console.log(`✓ ${file} — ${data.initialElements.length} element(s), ${data.sequence.length} step(s)`);
      }
    }
  } else if (file === "qa-ordering.json") {
    if (!Array.isArray(data.initialElementIds) || !Array.isArray(data.sequence)) {
      console.error(`✗ ${file} — missing "initialElementIds" or "sequence"`);
      exitCode = 1;
    } else {
      console.log(`✓ ${file} — ${data.initialElementIds.length} element(s), ${data.sequence.length} step(s)`);
    }
  } else if (file === "qa-keyframes.json") {
    if (!data.inputState || !data.exportedJson) {
      console.error(`✗ ${file} — missing "inputState" or "exportedJson"`);
      exitCode = 1;
    } else {
      console.log(`✓ ${file} — ${data.exportedJson.keyframes?.length ?? 0} keyframe group(s)`);
    }
  }
}

if (exitCode === 0) {
  console.log(`\nAll ${files.length} fixture(s) valid.`);
}
process.exit(exitCode);
