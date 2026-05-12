"""
Template registry — maps string keys to VideoTemplate classes.

To register a new template, add it here. The TUI and CLI both query this registry.
"""
from __future__ import annotations
from typing import Type

from .base import VideoTemplate
from .spinner      import SpinnerTemplate
from .fade         import FadeTemplate
from .static       import StaticTemplate
from .vertical     import VerticalTemplate
from .minimal      import MinimalTemplate
from .cinematic    import CinematicTemplate
from .waveformbar  import WaveformBarTemplate
from .vertical_wave import VerticalWaveTemplate

# ── Registry ──────────────────────────────────────────────────────────────────
# Ordered dict — insertion order determines TUI display order.
REGISTRY: dict[str, Type[VideoTemplate]] = {
    "spinner":     SpinnerTemplate,
    "fade":        FadeTemplate,
    "static":      StaticTemplate,
    "vertical":    VerticalTemplate,
    "minimal":     MinimalTemplate,
    "cinematic":   CinematicTemplate,
    "waveformbar": WaveformBarTemplate,
    "vertical_wave": VerticalWaveTemplate,
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
            f"Unknown template '{name}'. Available: {list(REGISTRY.keys())}"
        )
    return cls(config=config, **kwargs)


def list_templates() -> list[VideoTemplate]:
    """Return one (TemplateInfo-only) instance of every registered template."""
    return [cls() for cls in REGISTRY.values()]
