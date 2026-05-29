# Architecture Decision Records - Clipped

## ADR-0001: Modular Template System

### Status
Accepted

### Context
Clipped needs to generate videos from audio clips using different visual styles (spinners, fades, static art, etc.). The system must be extensible for new templates while maintaining consistent interfaces.

### Decision
Implement a modular template system with:
- Abstract base class `VideoTemplate` in `templates/base.py`
- Each template as a separate module in `templates/`
- Registry system in `templates/registry.py` for discovery
- Template selection via CLI and platform profiles

### Consequences
**Positive:**
- Easy to add new templates without modifying core code
- Consistent interface across all templates
- Platform profiles can suggest appropriate templates
- Templates can be developed and tested independently

**Negative:**
- Additional complexity in template coordination
- Need to maintain registry and base class

**Risks:**
- Template interface drift if not carefully maintained

## ADR-0002: Platform-Aware Export Profiles

### Status
Accepted

### Context
Different social platforms have varying requirements for video dimensions, duration limits, file size limits, and codec preferences. Clipped needs to optimize exports for each platform.

### Decision
Create `PlatformProfile` classes in `platforms.py` with:
- Dimensions (width, height)
- Maximum duration
- Maximum file size
- Codec settings (video codec, audio codec, bitrate)
- Suggested template mappings
- Auto-scaling when template dimensions differ from platform requirements

### Consequences
**Positive:**
- One-command exports optimized for each platform
- Consistent quality across platforms
- Easy to add new platform support
- Template suggestions improve user experience

**Negative:**
- Platform requirements change frequently (need maintenance)
- Additional complexity in export pipeline

## ADR-0003: FFmpeg Integration with Progress Tracking

### Status
Accepted

### Context
Video generation requires FFmpeg for encoding, but FFmpeg commands can take significant time (minutes) with no progress indication, leading to poor user experience.

### Decision
Implement `run_ffmpeg_with_progress()` in `progress.py` that:
- Parses FFmpeg stderr for time/duration information
- Displays real-time progress bar using Rich
- Handles both audio and video encoding
- Provides cancellation support

### Consequences
**Positive:**
- Users see progress during long operations
- Better perceived performance
- Ability to cancel stuck operations
- Consistent progress reporting across all FFmpeg operations

**Negative:**
- Additional complexity in subprocess management
- FFmpeg stderr parsing can be fragile
- Progress calculation depends on accurate duration metadata

## ADR-0004: Configuration Management

### Status
Accepted

### Context
Clipped needs user-configurable settings for FFmpeg paths, default platforms, output directories, and other preferences. Settings should persist across sessions.

### Decision
Use TOML configuration in `~/.config/clipped/config.toml` with:
- Default settings from `config.example.toml`
- Runtime loading via `get_config()` in `config.py`
- Validation of required directories and executables
- Preset system for common configurations

### Consequences
**Positive:**
- User preferences persist across sessions
- Easy to share configurations
- Validation prevents runtime errors
- Presets simplify common use cases

**Negative:**
- Need to handle config file creation and migration
- TOML parsing adds dependency

## ADR-0005: macOS Integration

### Status
Accepted

### Context
Clipped targets macOS users who expect native integration with system features like notifications, file pickers, and media applications.

### Decision
Integrate with macOS-specific features:
- AppleScript for file picker dialogs
- `osascript` for system notifications
- Swinsian integration for current track detection
- `afplay` for audio preview
- Keyboard Maestro macros for hotkeys

### Consequences
**Positive:**
- Native macOS user experience
- Seamless integration with existing workflows
- Powerful automation capabilities
- Familiar interface patterns

**Negative:**
- macOS-specific, not cross-platform
- AppleScript maintenance burden
- Dependency on external applications (Swinsian, KM)

## ADR-0006: YouTube URL Support

### Status
Accepted

### Context
Users want to clip audio directly from YouTube URLs without manual downloading, enabling quick sharing of online content.

### Decision
Integrate `yt-dlp` for YouTube downloading with:
- URL validation and metadata extraction
- Temporary file management
- Timeout handling (300s default)
- Error recovery for failed downloads

### Consequences
**Positive:**
- Direct URL support improves workflow
- No intermediate download step required
- Access to vast online audio library
- Metadata preservation from source

**Negative:**
- Dependency on yt-dlp (frequently updated)
- Network dependency for operations
- Copyright and terms of service considerations
- Additional complexity in error handling

## ADR-0007: Rich TUI Interface

### Status
Accepted

### Context
Clipped needs an interactive command-line interface for template/platform selection, with good usability for non-technical users.

### Decision
Use Rich + Questionary for TUI with:
- Interactive menus for template/platform selection
- Progress bars for long operations
- Colored output and formatting
- Keyboard navigation support

### Consequences
**Positive:**
- Professional, polished interface
- Good usability for all users
- Consistent with modern CLI tools
- Rich progress indication

**Negative:**
- Additional dependencies
- Terminal compatibility considerations
- More complex than simple argparse

## ADR-0008: Preset System

### Status
Accepted

### Context
Common workflows (Instagram Reels, TikTok videos, etc.) require specific template + platform combinations. Users shouldn't need to select these manually every time.

### Decision
Implement `--preset` flag that:
- Loads predefined template + platform combinations
- Skips interactive menus
- Supports custom user-defined presets in config
- Provides shortcuts for common use cases

### Consequences
**Positive:**
- Streamlined workflows for common tasks
- Reduced user friction
- Configurable for team preferences
- Batch processing friendly

**Negative:**
- Preset maintenance as platforms evolve
- Additional configuration complexity

## ADR-0009: Developer Tooling and Docs Generation

### Status
Accepted

### Context
Clipped benefits from clearer diagnostics, easier configuration management, and generated command reference documentation for users and maintainers.

### Decision
Add CLI tooling for:
- `clipped doctor` diagnostics
- `clipped config show|edit|init|reset`
- `clipped test templates` smoke tests
- `clipped batch` and `clipped watch` workflows
- `clipped docs generate` documentation generation

### Consequences
**Positive:**
- Better onboarding for new users
- Easier environment validation and troubleshooting
- Safer batch and watch workflows
- Generated docs stay in sync with config and templates

**Negative:**
- More CLI surface area to maintain
- Slightly higher help/UX complexity

## ADR-0010: Source Package Layout

### Status
Proposed

### Context
The active Python package currently lives in `clipped_src/`. That name is explicit, but it is less standard than modern Python's `src/<package>/` layout.

### Decision
Keep `clipped_src/` stable for the current cleanup pass. If the package is renamed later, prefer `src/clipped/` and update `bin/clipped`, `install.sh`, docs, tests, and all `python -m clipped_src.main` references in one migration.

Do not rename the package itself to `src`; `src` should be a container directory, not the importable application package.

### Consequences
**Positive:**
- Avoids breaking the CLI wrapper and Keyboard Maestro workflows during taxonomy cleanup.
- Leaves a clear migration path to a conventional Python layout.

**Negative:**
- The package name remains slightly nonstandard until a dedicated packaging pass.

## ADR-0011: Remotion-First Video Rendering

### Status
Accepted

### Context
The FFmpeg template system is reliable for utility renders, but richer motion graphics, typography, audio-reactive visuals, and reusable visual components are difficult to maintain as filter graphs.

### Decision
Add a top-level `remotion/` React/TypeScript app as Clipped's primary video renderer for new templates. Python remains the CLI/TUI, metadata resolver, platform/profile coordinator, and macOS automation layer. Remotion templates are declared in `remotion/templates.manifest.json`; `clipped_src/remotion_engine.py` prepares render props/assets and invokes the local Remotion CLI. Existing FFmpeg templates remain available as legacy templates and FFmpeg remains the audio-only/export utility path.

### Consequences
**Positive:**
- New templates can share higher-level visual components.
- Template options can be driven by a manifest and props JSON instead of Python filter graph code.
- Remotion Studio gives a better design workflow for future templates.

**Negative:**
- Adds Node/npm and pinned Remotion package dependencies.
- Render diagnostics must cover both Python/FFmpeg and Remotion/Node.
