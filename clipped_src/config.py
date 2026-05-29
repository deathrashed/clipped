"""
Configuration management for Clipped.

Config file: ~/.config/clipped/config.toml
State files: ~/.config/clipped/{state.json, history.txt}

Supports [general] settings and named [preset.*] profiles.
"""
import sys
import textwrap
import re
import json
from pathlib import Path
from typing import Any

try:
    import tomllib
except ImportError:
    print("Python 3.11+ is required. Please update.", file=sys.stderr)
    sys.exit(1)

CONFIG_FILE   = Path("~/.config/clipped/config.toml").expanduser()
STATE_FILE    = CONFIG_FILE.parent / "state.json"
HISTORY_FILE   = CONFIG_FILE.parent / "history.txt"

DEFAULT_CONFIG: dict = {
    "general": {
        "audio_dir":           "~/Music/clipped/_audio",
        "video_dir":           "~/Music/clipped/_video",
        "copy_to_clipboard":   True,
        "interactive_preview": True,
        "auto_open_output":    False,
        "preview_duration":    3.0,
        "smart_clipping":      False,
        "auto_fade":           True,
        "fade_duration":       0.5,
        "spinner_speed":       0.5,   # revolutions / second
        "waveform_mode":        "line",  # line | cline | p2p | point
        "waveform_color":       "0x00E5FF",  # vivid cyan
        "remotion_style":       "classic",
        "remotion_motion":      "medium",
        "remotion_waveform":    "radial",
        "remotion_palette":     "auto",
        "remotion_scene_pack":  "story",
        "remotion_effects":     "texture",
        "remotion_captions":    "off",
        "remotion_clean_logos": True,
        "remotion_logo_bg":     "auto",
        "remotion_logo_fuzz":   15,
        "rmbg_path":            "/Users/rd/Scripts/Riley/rmbg/bin/rmbg",
        "default_captions":     "off",
        "remotion_fps":         30,
        "default_template":     "gallery_square",
        "default_platform":    "default",
        "use_videotoolbox":     True,
        
        # Vertical Template Settings
        "vertical_spinner_speed":        0.5,
        "vertical_text_in_percent":      0.25,
        "vertical_reveal_start_percent": 0.82,
        "vertical_transition_duration":  2.0,
        "vertical_text_fade_duration":   1.0,
        "vertical_text_reveal_overlap":  1.0,
    },
    "preset": {
        "instagram": {
            "default_template": "pulse_reel",
            "default_platform": "instagram",
        },
        "tiktok": {
            "default_template": "pulse_reel",
            "default_platform": "tiktok",
        },
        "youtube_shorts": {
            "default_template": "pulse_reel",
            "default_platform": "youtube_shorts",
        },
        "vertical_full": {
            "default_template": "pulse_reel",
            "default_platform": "vertical_full",
        },
        "archive": {
            "default_template": "gallery_square",
            "default_platform": "default",
        },
        "cinematic": {
            "default_template": "cinematic",
            "default_platform": "youtube",
        },
        "discord": {
            "default_platform": "discord",
        },
        "waveformbar": {
            "default_template": "record_square",
            "default_platform": "default",
        },
    },
}

_DEFAULT_TOML = textwrap.dedent("""\
    [general]
    audio_dir           = "~/Music/clipped/_audio"
    video_dir           = "~/Music/clipped/_video"
    copy_to_clipboard   = true
    interactive_preview = true
    auto_open_output    = false
    preview_duration    = 3.0
    smart_clipping      = false
    auto_fade           = true
    fade_duration       = 0.5
    spinner_speed        = 0.5       # revolutions / second
    waveform_mode       = "line"    # line | cline | p2p | point  (for waveformbar template)
    waveform_color      = "0x00E5FF" # hex colour for the waveform bar
    remotion_style      = "classic"
    remotion_motion     = "medium"
    remotion_waveform   = "radial"
    remotion_palette    = "auto"
    remotion_scene_pack = "story"
    remotion_effects    = "texture"
    remotion_captions   = "off"
    remotion_clean_logos = true
    remotion_logo_bg    = "auto"
    remotion_logo_fuzz  = 15
    rmbg_path           = "/Users/rd/Scripts/Riley/rmbg/bin/rmbg"
    default_captions    = "off"
    remotion_fps        = 30
    default_template    = "gallery_square"
    default_platform    = "default"
    use_videotoolbox    = true      # use Apple VideoToolbox GPU acceleration on macOS

    # ── Named presets ─────────────────────────────────────────────────────────
    # Run with: clipped --preset instagram
    # Each key overrides the matching [general] key.

    [preset.instagram]
    default_template = "pulse_reel"
    default_platform = "instagram"

    [preset.tiktok]
    default_template = "pulse_reel"
    default_platform = "tiktok"

    [preset.youtube_shorts]
    default_template = "pulse_reel"
    default_platform = "youtube_shorts"

    [preset.vertical_full]
    default_template = "pulse_reel"
    default_platform = "vertical_full"

    [preset.archive]
    default_template = "gallery_square"
    default_platform = "default"

    [preset.cinematic]
    default_template = "cinematic"
    default_platform = "youtube"

    [preset.discord]
    default_platform = "discord"

    [preset.waveformbar]
    default_template = "record_square"
    default_platform = "default"
""")


def load_config() -> dict:
    config_dir = CONFIG_FILE.parent
    config_dir.mkdir(parents=True, exist_ok=True)

    import copy
    config = copy.deepcopy(DEFAULT_CONFIG)

    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(_DEFAULT_TOML)
        return config

    with CONFIG_FILE.open("rb") as f:
        try:
            user = tomllib.load(f)
        except Exception as e:
            print(f"Error parsing config.toml: {e}", file=sys.stderr)
            return config

    # Merge general settings
    gen = user.get("general", {})
    
    # Migrate legacy output_dir key
    if "output_dir" in gen:
        od = gen.pop("output_dir")
        if "audio_dir" not in gen:
            gen["audio_dir"] = f"{od}/_audio"
        if "video_dir" not in gen:
            gen["video_dir"] = f"{od}/_video"

    config["general"].update(gen)

    # Load presets - tomllib gives us user["preset"]["instagram"] = {...}
    if "preset" in user and isinstance(user["preset"], dict):
        config["preset"].update(user["preset"])
    
    # Support top-level preset.NAME for backward compatibility if any
    for key, val in user.items():
        if key.startswith("preset.") and isinstance(val, dict):
            p_name = key.split(".", 1)[1]
            if "preset" not in config:
                config["preset"] = {}
            config["preset"][p_name] = val

    return config


def get_config() -> dict:
    return load_config()["general"]


def _format_toml_value(value: Any) -> str:
    """Format a simple scalar value for config.toml."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, Path):
        value = str(value)
    escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _find_section(lines: list[str], section: str) -> tuple[int | None, int | None]:
    header = f"[{section}]"
    start = None
    for idx, line in enumerate(lines):
        if line.strip() == header:
            start = idx
            break
    if start is None:
        return None, None

    end = len(lines)
    for idx in range(start + 1, len(lines)):
        stripped = lines[idx].strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            end = idx
            break
    return start, end


def update_config_key(key: str, value: Any, section: str = "general") -> None:
    """
    Persist one simple scalar config key.

    This intentionally avoids a new TOML writer dependency. Existing comments
    and sections are preserved for normal one-line scalar values, but complex
    TOML constructs such as arrays of tables are outside this helper's scope.
    """
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(_DEFAULT_TOML)

    original = CONFIG_FILE.read_text()
    lines = original.splitlines(keepends=True)
    start, end = _find_section(lines, section)

    if start is None or end is None:
        if lines and not lines[-1].endswith("\n"):
            lines[-1] = f"{lines[-1]}\n"
        if lines and lines[-1].strip():
            lines.append("\n")
        lines.append(f"[{section}]\n")
        start = len(lines) - 1
        end = len(lines)

    formatted = _format_toml_value(value)
    key_pattern = re.compile(
        rf"^(\s*{re.escape(key)}\s*=\s*)(.*?)(\s*(#.*)?)?$"
    )

    for idx in range(start + 1, end):
        line = lines[idx]
        newline = "\n" if line.endswith("\n") else ""
        body = line[:-1] if newline else line
        match = key_pattern.match(body)
        if match:
            suffix = match.group(3) or ""
            lines[idx] = f"{match.group(1)}{formatted}{suffix}{newline}"
            break
    else:
        insert_at = end
        while insert_at > start + 1 and not lines[insert_at - 1].strip():
            insert_at -= 1
        lines.insert(insert_at, f"{key} = {formatted}\n")

    CONFIG_FILE.write_text("".join(lines))
    try:
        with CONFIG_FILE.open("rb") as f:
            tomllib.load(f)
    except Exception:
        CONFIG_FILE.write_text(original)
        raise


def get_preset(name: str) -> dict:
    """
    Return merged config for a named preset.
    Preset keys override [general] keys.
    """
    full = load_config()
    base = dict(full["general"])
    presets = full.get("preset", {})
    overrides = presets.get(name, {})
    if not overrides:
        raise ValueError(
            f"Preset '{name}' not found in config.toml. "
            f"Available: {list(presets.keys())}"
        )
    base.update(overrides)
    return base


def validate_output_dirs(config: dict) -> None:
    """
    Warn if configured output directories have non-existent parents
    (e.g. an unmounted external drive). Does NOT abort — just warns.
    """
    from rich.console import Console
    c = Console()
    for key in ("audio_dir", "video_dir"):
        p = Path(config.get(key, "")).expanduser()
        parent = p.parent
        if not parent.exists():
            c.print(
                f"[bold yellow]WARN Output dir parent does not exist:[/bold yellow] {parent}\n"
                f"   ({key} = {p})\n"
                f"   Is an external drive unmounted? Clips will be saved there anyway."
            )


def load_state() -> dict:
    """Load session state (last choices, recents) from state.json."""
    if not STATE_FILE.exists():
        return {}
    try:
        with STATE_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(state: dict) -> None:
    """Save session state (last choices, recents) to state.json."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        with STATE_FILE.open("w", encoding="utf-8") as f:
            json.dump(state, f, indent=4)
    except Exception:
        pass


def update_state(key: str, value: Any) -> None:
    """Update one key in the session state."""
    state = load_state()
    state[key] = value
    save_state(state)
