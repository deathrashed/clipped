"""
Configuration management for Clipped.

Config file: ~/.config/clipped/config.toml
State files: ~/.config/clipped/{state.json, history.txt, library.jsonl}

Supports [general] settings and named [preset.*] profiles.
"""
import sys
import textwrap
from pathlib import Path

try:
    import tomllib
except ImportError:
    print("Python 3.11+ is required. Please update.", file=sys.stderr)
    sys.exit(1)

CONFIG_FILE   = Path("~/.config/clipped/config.toml").expanduser()
STATE_FILE    = CONFIG_FILE.parent / "state.json"
HISTORY_FILE  = CONFIG_FILE.parent / "history.txt"
LIBRARY_FILE  = CONFIG_FILE.parent / "library.jsonl"

DEFAULT_CONFIG: dict = {
    "general": {
        "audio_dir":           "~/Music/clipped/_audio",
        "video_dir":           "~/Music/clipped/_video",
        "copy_to_clipboard":   True,
        "interactive_preview": True,
        "smart_clipping":      False,
        "auto_fade":           True,
        "fade_duration":       0.5,
        "spinner_speed":       0.5,   # revolutions / second
        "waveform_mode":        "line",  # line | cline | p2p | point
        "waveform_color":       "0x00E5FF",  # vivid cyan
        "default_template":    "spinner",
        "default_platform":    "default",
    }
}

_DEFAULT_TOML = textwrap.dedent("""\
    [general]
    audio_dir           = "~/Music/clipped/_audio"
    video_dir           = "~/Music/clipped/_video"
    copy_to_clipboard   = true
    interactive_preview = true
    smart_clipping      = false
    auto_fade           = true
    fade_duration       = 0.5
    spinner_speed        = 0.5       # revolutions / second
    waveform_mode       = "line"    # line | cline | p2p | point  (for waveformbar template)
    waveform_color      = "0x00E5FF" # hex colour for the waveform bar
    default_template    = "spinner"
    default_platform    = "default"

    # ── Named presets ─────────────────────────────────────────────────────────
    # Run with: clipped --preset instagram
    # Each key overrides the matching [general] key.

    [preset.instagram]
    default_template = "vertical"
    default_platform = "instagram"

    [preset.tiktok]
    default_template = "vertical"
    default_platform = "tiktok"

    [preset.archive]
    default_template = "static"
    default_platform = "default"

    [preset.cinematic]
    default_template = "cinematic"
    default_platform = "youtube"

    [preset.discord]
    default_platform = "discord"

    [preset.waveformbar]
    default_template = "waveformbar"
    default_platform = "default"
""")


def load_config() -> dict:
    config_dir = CONFIG_FILE.parent
    config_dir.mkdir(parents=True, exist_ok=True)

    import copy
    config = copy.deepcopy(DEFAULT_CONFIG)

    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "rb") as f:
            try:
                user = tomllib.load(f)
            except Exception as e:
                print(f"Error parsing config.toml: {e}", file=sys.stderr)
                return config

        # Migrate legacy output_dir key
        gen = user.get("general", {})
        if "output_dir" in gen:
            if "audio_dir" not in gen:
                gen["audio_dir"] = f"{gen['output_dir']}/_audio"
            if "video_dir" not in gen:
                gen["video_dir"] = f"{gen['output_dir']}/_video"

        config["general"].update(gen)

        # Load presets
        for key, val in user.items():
            if key.startswith("preset.") or (key == "preset" and isinstance(val, dict)):
                # tomllib gives us nested: user["preset"]["instagram"] = {...}
                pass
        if "preset" in user and isinstance(user["preset"], dict):
            config["preset"] = user["preset"]

    else:
        CONFIG_FILE.write_text(_DEFAULT_TOML)

    return config


def get_config() -> dict:
    return load_config()["general"]


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
                f"[bold yellow]⚠  Output dir parent does not exist:[/bold yellow] {parent}\n"
                f"   ({key} = {p})\n"
                f"   Is an external drive unmounted? Clips will be saved there anyway."
            )
