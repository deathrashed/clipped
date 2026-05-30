"""
Template registry — maps string keys to VideoTemplate classes.

# Templates are discovered automatically from the `src/clipped/templates/`
# package. Add a new template file and subclass `VideoTemplate` to expose it.
"""
from __future__ import annotations

import importlib
import json
import pkgutil
from pathlib import Path
from typing import Any, Type

from .base import TemplateInfo, VideoTemplate

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


class RemotionTemplate(VideoTemplate):
    """Metadata-only template adapter for Remotion compositions."""

    info: TemplateInfo

    def get_inputs(self, assets) -> list[str]:
        return [str(assets.audio_path)]

    def get_filter_graph(self, assets, duration: float) -> str:
        raise RuntimeError("Remotion templates do not expose FFmpeg filter graphs.")


def _manifest_path() -> Path:
    return Path(__file__).resolve().parents[3] / "data" / "templates.manifest.json"


def _load_remotion_templates() -> dict[str, Type[VideoTemplate]]:
    path = _manifest_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    registry: dict[str, Type[VideoTemplate]] = {}
    for item in data.get("templates", []):
        try:
            aspect = tuple(item.get("aspect", (1080, 1080)))
            if len(aspect) != 2:
                continue
            name = str(item["name"])
            info = TemplateInfo(
                name=name,
                label=str(item.get("label", name)),
                description=str(item.get("description", "")),
                aspect=(int(aspect[0]), int(aspect[1])),
                ideal_for=list(item.get("ideal_for", [])),
                engine=str(item.get("engine", "remotion")),
                category=str(item.get("category", "Remotion")),
                composition_id=str(item.get("composition_id", name)),
                capabilities=list(item.get("capabilities", [])),
                options=dict(item.get("options", {})),
                defaults=dict(item.get("defaults", {})),
            )
        except Exception:
            continue

        registry[name] = type(
            f"{''.join(part.capitalize() for part in name.split('_'))}RemotionTemplate",
            (RemotionTemplate,),
            {"info": info},
        )
    return registry


REGISTRY: dict[str, Type[VideoTemplate]] = {
    **_load_remotion_templates(),
    **_discover_templates(),
}


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


def template_engine(name: str) -> str:
    cls = REGISTRY.get(name)
    if cls is None:
        return "ffmpeg"
    return getattr(cls.info, "engine", "ffmpeg")


def default_platform_for_template(name: str) -> str:
    cls = REGISTRY.get(name)
    if cls is None:
        return "default"
    info = cls.info
    if info.engine == "remotion":
        w, h = info.aspect
        if h > w:
            return "vertical_full"
        if w > h:
            return "youtube"
        return "default"
    if name in {"vertical", "vertical_wave", "reel"}:
        return "vertical_full"
    if name == "cinematic":
        return "youtube"
    return "default"


def remotion_template_options(name: str) -> tuple[dict[str, Any], dict[str, Any]]:
    cls = REGISTRY.get(name)
    if cls is None:
        return {}, {}
    info = cls.info
    if info.engine != "remotion":
        return {}, {}
    return dict(info.options), dict(info.defaults)
