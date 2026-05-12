"""
Video template modules for Clipped.

Each template is a self-contained VideoTemplate subclass.
Import via the registry: from .registry import REGISTRY, get_template
"""
from .registry import REGISTRY, get_template, list_templates

__all__ = ["REGISTRY", "get_template", "list_templates"]
