# Clipped - Media Automation Toolkit

### 1. Project Overview & Architecture
*   **Purpose:** A high-leverage media toolkit for automated audio clipping, multi-template video generation, platform-aware export, and metadata-aware workflows on macOS.
*   **Tech Stack:** Python 3, FFmpeg, yt-dlp, Typer, Rich, Mutagen.
*   **Architecture:** Command-Line Interface (CLI) pattern. The application uses a modular design routing commands from the CLI entrypoint (`main.py`) to domain-specific modules (`audio.py`, `video.py`, `platforms.py`). Video templates are implemented using a Strategy/Registry pattern inside the `templates/` directory, subclassing a `VideoTemplate` Abstract Base Class.
*   **Architecture Diagram:**
```mermaid
flowchart TD
    CLI[main.py (Typer CLI)]
    Audio[audio.py]
    Video[video.py]
    Config[config.py]
    Platforms[platforms.py]
    Templates[templates/registry.py]
    FFmpeg[(FFmpeg)]

    CLI --> Audio
    CLI --> Video
    CLI --> Config
    Video --> Platforms
    Video --> Templates
    Audio --> FFmpeg
    Video --> FFmpeg
```

### 2. Repository Map
*   **Directory Structure:**
    *   `bin/`: Contains the global executable wrapper (`clipped`).
    *   `clipped_src/`: Main Python package containing all source code.
        *   `templates/`: Video template implementations (e.g., `spinner.py`, `fade.py`) and the registry.
    *   `macros/`: Keyboard Maestro `.kmmacros` bundle and setup instructions.
    *   `docs/`: Documentation.
    *   `.venv/`: Python virtual environment (ignored in git).
*   **Key Entry Points:**
    *   `bin/clipped`: Executable shell wrapper setting up the path.
    *   `clipped_src/main.py`: The Typer CLI entrypoint.
    *   `clipped_src/templates/registry.py`: Where new templates must be registered.

### 3. Operational Workflows
*   **Setup & Environment:**
    *   Run `install.sh` or manually create a venv: `python -m venv .venv && source .venv/bin/activate`
    *   Install dependencies: `pip install -r requirements.txt`
    *   Configuration is stored at `~/.config/clipped/config.toml` (generated on first run from `config.example.toml`).
*   **Development Server:** Not applicable (CLI tool). Test interactively by running `clipped` or `bin/clipped`.
*   **Testing & Validation:**
    *   `test_all_templates.py` can be used to run/test templates.
    *   Use `--dry-run` flag with `clipped video` to preview FFmpeg commands without executing them.

### 4. Technical Conventions & Patterns
*   **Coding Standards:** Python type hints, modular structure. Uses `Rich` for terminal UI and progress bars.
*   **State & Data:** Configuration is loaded from XDG paths (`~/.config/clipped/config.toml`). Clip history is stored in an append-only JSONL file (`clipped_training_data.jsonl`).
*   **Error Handling:** Managed primarily through CLI exits and Typer. FFmpeg errors are captured and reported.
*   **Design Patterns:** Uses the Registry pattern for video templates to make them easily extensible.

### 5. AI Agent Operational Guidance (CRITICAL)
*   **Safe Modification Boundaries:** `clipped_src/` is fully safe to modify. Keyboard Maestro macros (`macros/`) should be modified via the `macro-creator` skill rather than editing XML blindly.
*   **Secrets Management & Security:** No explicit secrets are currently managed, but any API keys should be placed in `~/.config/clipped/config.toml` or `.env` and NEVER committed.
*   **Preservation Mandates:**
    *   Always use the `.venv` virtual environment for execution and dependency installation.
    *   Do not break the `VideoTemplate` ABC contract when creating new templates.
*   **Known Pitfalls:** FFmpeg string escaping in filter graphs can be complex; always verify FFmpeg command output using `--dry-run`.
*   **Required Verifications:** Always run `python test_all_templates.py` or manually test CLI commands after modifications. Use `plutil -lint` if you generate or modify KM macros.

### 6. Project Health Snapshot
*   **Current State:** Project is actively maintained (v2.0.0). Codebase is modular and template-extensible. Relies heavily on external binaries like `ffmpeg` and `yt-dlp`. Keyboard Maestro macros provide the primary fast path for users, meaning CLI changes must not break the `clipped` command signature expected by the macros.
