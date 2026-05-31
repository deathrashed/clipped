from __future__ import annotations
from pathlib import Path

FONT_FILE = "/System/Library/Fonts/Supplemental/Arial.ttf"

def font(template):
    return f":fontfile='{template._escape_path(FONT_FILE)}'" if Path(FONT_FILE).exists() else ""

def meta(assets, name, default=""):
    return str(getattr(assets, name, "") or default)

def year(assets):
    return meta(assets, "year") or meta(getattr(assets, "metadata", object()), "year")

def genre(assets):
    return meta(assets, "genre") or meta(getattr(assets, "metadata", object()), "genre")

def bg_cover(idx, w, h, label="bg", blur=42, bright=-0.36, sat=0.65):
    return (
        f"[{idx}:v]scale={w}:{h}:force_original_aspect_ratio=increase,"
        f"crop={w}:{h},gblur=sigma={blur},eq=brightness={bright}:saturation={sat}[{label}]"
    )

def solid(w, h, label="bg", color="#07070a"):
    return f"color=s={w}x{h}:c={color}[{label}]"

def square(idx, size, label):
    return (
        f"[{idx}:v]scale={size}:{size}:force_original_aspect_ratio=decrease,"
        f"pad={size}:{size}:(ow-iw)/2:(oh-ih)/2:color=black@0,format=rgba[{label}]"
    )

def circle(idx, size, speed, label):
    return (
        f"[{idx}:v]scale={size}:{size}:force_original_aspect_ratio=decrease,"
        f"pad={size}:{size}:(ow-iw)/2:(oh-ih)/2:color=black@0,format=rgba,"
        f"geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':"
        f"a='if(lte(pow(X-W/2,2)+pow(Y-H/2,2),pow(W/2,2)),255,0)',"
        f"rotate=t*{speed}:c=none[{label}]"
    )

def readable(template, align="center"):
    return (
        f"{font(template)}:text_align={align}:expansion=none"
        ":shadowcolor=black@0.85:shadowx=0:shadowy=4"
        ":borderw=2:bordercolor=black@0.55"
    )

# ── Old API aliases (backward compat) ───────────────────────────────────
def bg(idx, w, h, label, blur, bright, sat):
    return bg_cover(idx, w, h, label, blur, bright, sat)

def fallback(w, h, label="bg", color="#08080b"):
    return solid(w, h, label, color)

font_clause = font

def blurred_bg(idx, w, h, blur=42, brightness=-0.35, saturation=0.7, label="bg"):
    return bg_cover(idx, w, h, label, blur, brightness, saturation)

def fallback_bg(w, h, label="bg", color="#08080b"):
    return solid(w, h, label, color)

square_art = square
circular_art = circle
readable_common = readable
