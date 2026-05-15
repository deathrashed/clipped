"""
Template registry — maps string keys to VideoTemplate classes.

Templates are discovered automatically from the `clipped_src/templates/`
package. Add a new template file and subclass `VideoTemplate` to expose it.
"""
from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path
from typing import Type

from .base import VideoTemplate

# ── Registry ──────────────────────────────────────────────────────────────────
# Template modules are discovered dynamically to reduce registry maintenance.


def _discover_templates() -> dict[str, Type[VideoTemplate]]:
    registry: dict[str, Type[VideoTemplate]] = {}
    package = __name__.rsplit(".", 1)[0]
    template_dir = Path(__file__).resolve().parent

    for module_info in sorted(pkgutil.iter_modules([str(template_dir)]), key=lambda m: m.name):
        if module_info.name in {"__init__", "base", Path(__file__).stem}:
            continue
        module = importlib.import_module(f"{package}.{module_info.name}")
        for obj in vars(module).values():
            if isinstance(obj, type) and issubclass(obj, VideoTemplate) and obj is not VideoTemplate:
                info = getattr(obj, "info", None)
                if info is None:
                    continue
                registry[info.name] = obj
    return registry


REGISTRY: dict[str, Type[VideoTemplate]] = _discover_templates()


def get_template(name: str, config: dict | None = None, **kwargs) -> VideoTemplate:
    """
    Instantiate a template by name.

    Extra kwargs (e.g. sequence=[...]) are forwarded to the constructor
    for templates that accept them (like FadeTemplate).
    """
    cls = REGISTRY.get(name)
    if cls is None:
        raise ValueError(
            f"Unknown template '{name}'. Available: {sorted(REGISTRY.keys())}"
        )
    return cls(config=config, **kwargs)


def list_templates() -> list[VideoTemplate]:
    """Return one (TemplateInfo-only) instance of every registered template."""
    return [cls() for cls in REGISTRY.values()]
