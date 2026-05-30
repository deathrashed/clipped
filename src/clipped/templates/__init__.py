"""
Video template modules for Clipped.

Each template is a self-contained VideoTemplate subclass.
Import via the registry: from .registry import REGISTRY, get_template
"""
from .registry import (
    REGISTRY,
    default_platform_for_template,
    get_template,
    list_templates,
    remotion_template_options,
    template_engine,
)

__all__ = [
    "REGISTRY",
    "default_platform_for_template",
    "get_template",
    "list_templates",
    "remotion_template_options",
    "template_engine",
]
