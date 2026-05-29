from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from rich.console import Console

from .config import get_config, load_config, validate_output_dirs
from .platforms import list_platforms
from .templates import REGISTRY
from .remotion_engine import REMOTION_DIR

console = Console()


def _check_tool(name: str) -> bool:
    path = shutil.which(name)
    console.print(f"- {name}: [green]found[/green]" if path else f"- {name}: [red]missing[/red]")
    return bool(path)


def _check_python_package(name: str) -> bool:
    try:
        __import__(name)
        console.print(f"- Python package {name}: [green]import OK[/green]")
        return True
    except ImportError:
        console.print(f"- Python package {name}: [red]missing[/red]")
        return False


def _check_templates() -> bool:
    success = True
    console.print("\nTemplate registry:")
    for name, cls in REGISTRY.items():
        try:
            instance = cls()
            size = instance.get_output_size()
            console.print(f"- {name}: [green]OK[/green] ({size[0]}x{size[1]})")
        except Exception as exc:
            console.print(f"- {name}: [red]ERROR[/red] {exc}")
            success = False
    return success


def _check_remotion() -> bool:
    success = True
    console.print("\nRemotion renderer:")
    if not (REMOTION_DIR / "package.json").exists():
        console.print(f"- app: [red]missing[/red] ({REMOTION_DIR})")
        return False
    console.print(f"- app: [green]found[/green] ({REMOTION_DIR})")

    for tool in ("node", "npm", "npx"):
        success = _check_tool(tool) and success

    expected = None
    try:
        import json
        data = json.loads((REMOTION_DIR / "package.json").read_text(encoding="utf-8"))
        expected = data.get("dependencies", {}).get("remotion")
    except Exception:
        pass

    remotion_pkg = REMOTION_DIR / "node_modules" / "remotion" / "package.json"
    if not remotion_pkg.exists():
        console.print("- npm install: [yellow]not installed[/yellow] (run: cd remotion && npm install)")
        return False

    try:
        import json
        installed = json.loads(remotion_pkg.read_text(encoding="utf-8")).get("version")
        status = "green" if not expected or installed == expected else "yellow"
        console.print(f"- remotion package: [{status}]{installed}[/{status}] expected {expected or 'unknown'}")
        if expected and installed != expected:
            success = False
    except Exception as exc:
        console.print(f"- remotion package: [red]error[/red] {exc}")
        success = False

    try:
        res = subprocess.run(
            ["npm", "run", "still:smoke"],
            cwd=REMOTION_DIR,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if res.returncode == 0:
            console.print("- still render: [green]OK[/green]")
        else:
            console.print("- still render: [red]failed[/red]")
            console.print(f"  [dim]{(res.stderr or res.stdout).strip()[-500:]}[/dim]")
            success = False
    except Exception as exc:
        console.print(f"- still render: [red]error[/red] {exc}")
        success = False
    return success


def _check_platforms() -> bool:
    success = True
    console.print("\nPlatform profiles:")
    for profile in list_platforms():
        try:
            assert profile.name
            console.print(f"- {profile.name}: [green]OK[/green] ({profile.label})")
        except AssertionError:
            console.print(f"- {profile.name}: [red]invalid[/red]")
            success = False
    return success


def run_diagnostics() -> None:
    console.print("[bold cyan]Clipped diagnostics[/bold cyan]\n")

    config = load_config()
    general = config.get("general", {})

    console.print("[bold]Config file[/bold]")
    console.print(f"- Path: {Path.home() / '.config' / 'clipped' / 'config.toml'}")
    console.print(f"- Presets: {', '.join(sorted(config.get('preset', {}).keys())) or 'none'}")
    console.print("\n[bold]Required tools[/bold]")

    tools = ["python3", "ffmpeg", "ffprobe", "yt-dlp", "osascript", "magick"]
    tool_results = [_check_tool(tool) for tool in tools]

    rmbg_path = general.get("rmbg_path", "/Users/rd/Scripts/Riley/rmbg/bin/rmbg")
    if rmbg_path and Path(rmbg_path).expanduser().exists():
        console.print(f"- rmbg (logo cleaning): [green]found[/green] ({rmbg_path})")
    else:
        console.print(f"- rmbg (logo cleaning): [yellow]missing[/yellow] (Not fatal, logo cleaning disabled)")

    console.print("\n[bold]Python dependencies[/bold]")
    pkg_results = [_check_python_package(name) for name in ["mutagen"]]

    console.print("\n[bold]Output directories[/bold]")
    validate_output_dirs(get_config())

    template_ok = _check_templates()
    platforms_ok = _check_platforms()
    remotion_ok = _check_remotion()

    console.print("\n[bold]Summary[/bold]")
    overall = all(tool_results + pkg_results + [template_ok, platforms_ok, remotion_ok])
    console.print(
        "[green]All checks passed[/green]" if overall else "[red]Some checks failed[/red]"
    )

    if not overall:
        raise SystemExit(1)
