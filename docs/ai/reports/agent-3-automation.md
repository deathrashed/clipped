# Automation & Infrastructure Domain Analysis

This document provides a comprehensive, recursive analysis of the Automation & Infrastructure Domain (`macros/`, `scripts/`, and `tests/` directories) within the Clipped repository. It highlights functionality gaps, usability issues, and opportunities for improvement.

## 1. Technology & Dependencies

*   **Hardcoded Environmental Dependencies**: The test scripts (`tests/generate_test_vids.py`, `tests/test_all_templates.py`) and macros (`macros/clipped.kmmacros`, `macros/clipped-swinsian.kmmacros`) are heavily tightly-coupled to a specific user's local environment. They rely on absolute paths like `/Volumes/Eksternal/Audio/...` for test source files, `~/Scripts/Riley/clipped/bin/clipped` for the executable, and even `~/Scripts/.config/python/run.sh` to execute modules.
*   **Remotion/Node Runtime**: `scripts/render-fixtures.sh` assumes `npx` and a fully installed `node_modules` directory in `remotion/` are present, but lacks a pre-flight check to ensure dependencies are installed before attempting to render.
*   **Keyboard Maestro (macOS)**: Macros rely on `osascript` to bridge between Keyboard Maestro, Swinsian, Finder, and Terminal.app.

## 2. Feature Gaps

*   **Missing Remotion Templates in Macros**: The interactive prompt in `macros/clipped.kmmacros` ("3. Choose Video Template") only lists older FFmpeg templates (`reel`, `vertical`, `spinner`, etc.). None of the newer, flagship Remotion templates (`pulse_reel`, `gallery_square`, `record_square`, `fluid_scene`, `metal_vhs`, `premium_card`) are available in the interactive KM workflow.
*   **Outdated Default Templates**: The "Generate Instagram Reel (Last Clip)" macro (HotKey ⌘⇧34) hardcodes the template to the old FFmpeg `reel` template, rather than the newer, superior `pulse_reel` Remotion template.
*   **Missing Remotion Tests in E2E Suite**: `tests/test_all_templates.py` only validates FFmpeg templates. It completely omits all Remotion templates from its test matrix, meaning core product features lack automated CLI testing in this script.
*   **No Standardized Test Audio**: The test scripts fail immediately if the user doesn't have the specific heavy-metal MP3s located at `/Volumes/Eksternal/...`. There is no fallback to an included `assets/` or `remotion/public/` sample audio file, making the test suite unusable for CI or new contributors out-of-the-box.

## 3. Architecture & Structure

*   **Fragmented Testing Strategy**: The repository splits testing concerns without a unified entry point. `tests/test_all_templates.py` tests 2-second FFmpeg renders, `tests/generate_test_vids.py` does 5-second E2E previews for all templates, and `scripts/render-fixtures.sh` performs isolated still-renders of Remotion compositions. A unified task runner (e.g., Makefile, Justfile, or top-level python script) would improve QA ergonomics.
*   **Fragile AST Parsing**: `scripts/generate_finetune_data.py` uses brittle regular expressions to parse Python code (extracting `get_filter_graph` bodies and `TemplateInfo`). This will easily break with formatting changes or new python language features. Using the native `ast` module would provide a much more robust architecture for static code analysis.
*   **Inconsistent Execution Contexts**: Macros launch visible instances of `Terminal.app` to run shell scripts. This interrupts the user's workflow by stealing focus and littering the terminal with history, rather than running seamlessly in the background and dispatching native macOS notifications upon success/failure.

## 4. Code Quality Issues

*   **Duplication of Test Logic**: `generate_test_vids.py` and `test_all_templates.py` both invoke the CLI to render short video segments, but they define their own overlapping template arrays and use completely different invocation methods (`./bin/clipped` vs an external `run.sh` script).
*   **Silent Failures in Data Generation**: `generate_finetune_data.py` catches generic exceptions (`except Exception as e: print(...)`) and continues. A failure in regex parsing could result in a silently generated dataset that is missing critical examples.
*   **Variable/Naming Drift**: The `clipped-swinsian.kmmacros` script has a hardcoded template default of `reel` instead of `pulse_reel`, again reflecting a drift between the Python/React implementation and the automation layer.

## 5. Performance Opportunities

*   **Sequential Test Execution**: Both Python test scripts (`generate_test_vids.py`, `test_all_templates.py`) iterate through templates sequentially. Since video rendering is heavily CPU-bound but independent per-template, these could be parallelized using `concurrent.futures.ThreadPoolExecutor` or `asyncio` to significantly reduce the E2E test suite runtime.
*   **Sequential Fixture Rendering**: `scripts/render-fixtures.sh` calls `npx remotion still` sequentially. Remotion supports parallelized rendering, or at minimum, the bash script could launch jobs in the background (`&`) and `wait` for them to finish, speeding up visual QA.
*   **Terminal Boot Overhead**: The KM macros wait for Terminal.app to launch and initialize a full `zsh` interactive environment before running the `clipped` command. Invoking the binary directly via a background shell script inside KM (with output piped to a temporary log file) would remove the GUI overhead and start the FFmpeg/Remotion processes milliseconds faster.
