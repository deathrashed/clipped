from __future__ import annotations

from pathlib import Path
from typing import Iterable

import typer
from rich.console import Console

from .config import load_config
from .platforms import list_platforms
from .templates import list_templates

docs_app = typer.Typer(help="Generate Clipped documentation from live config and templates.")
console = Console()


def _md_table(headers: list[str], rows: Iterable[list[str]]) -> str:
    header_row = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join(["---"] * len(headers)) + " |"
    lines = [header_row, sep]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


@docs_app.command("generate")
def generate(
    output: Path = typer.Option(Path("docs/CLI.md"), help="Output markdown path."),
) -> None:
    """Generate a CLI documentation markdown file."""
    config = load_config()
    presets = config.get("preset", {})
    template_rows = [
        [t.info.name, t.info.label, f"{t.info.aspect[0]}×{t.info.aspect[1]}", ", ".join(t.info.ideal_for)]
        for t in list_templates()
    ]
    platform_rows = [
        [p.name, p.label, f"{p.width or '-'}×{p.height or '-'}", p.output_format]
        for p in list_platforms()
    ]
    preset_rows = [[name, ", ".join(f"{k}={v}" for k, v in data.items())] for name, data in presets.items()]

    content = f"""# Clipped CLI Reference

## Templates

{_md_table(['Name', 'Label', 'Size', 'Ideal For'], template_rows)}

## Platforms

{_md_table(['Name', 'Label', 'Size', 'Format'], platform_rows)}

## Presets

{_md_table(['Preset', 'Overrides'], preset_rows or [['none', '']])}

## Examples

```bash
clipped --help
clipped audio track.mp3 30 45
clipped video myaudio.mp3 --template spinner --platform default
clipped video vertical myaudio.mp3 --preset instagram
clipped config show
clipped doctor
clipped test templates sample.mp3 --dry-run
clipped batch video --input-dir ./audio --template spinner --platform default --dry-run
clipped watch --input-dir ./audio --type video --dry-run
```
"""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content)
    console.print(f"[green]Generated docs at {output}[/green]")
