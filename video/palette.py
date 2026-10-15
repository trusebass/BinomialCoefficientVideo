"""Colors, fonts, timing constants and global config (script Part A).

Every scene does `from palette import *`, so anything defined here is shared.
"""

from manim import *

# ---------------------------------------------------------------- colors (A.1)
BG = ManimColor("#101318")            # frame background
PANEL = ManimColor("#171B22")         # rare backing panel
INK = ManimColor("#EEF0F4")           # main text, numbers, operators
INK2 = ManimColor("#B7BCC8")          # secondary text, tree edges
MUTED = ManimColor("#8A90A0")         # labels, axes, dimmed context
RULE = ManimColor("#2A2F39")          # lines at rest, outlines
A_BLUE = ManimColor("#3987E5")        # every letter a, every ×a edge
B_ORANGE = ManimColor("#D95926")      # every letter b, every ×b edge
PATH_AQUA = ManimColor("#199E70")     # traced paths only
FOCUS_YELLOW = ManimColor("#C98500")  # the one thing in focus
CELL_LO = ManimColor("#1B2433")       # Pascal cell fill at t = 0
CELL_HI = ManimColor("#6DA7EC")       # Pascal cell fill at t = 1

# ---------------------------------------------------------------- fonts (A.2)
# Pango (Manim's text engine) silently falls back to a default face when a
# name doesn't match, so these must be the exact family names that
# `manimpango.list_fonts()` reports.
DISPLAY_FONT = "IBM Plex Sans Condensed"
MONO_FONT = "Bale Mono"               # fallback: "IBM Plex Mono"
SERIF_FONT = "Source Serif 4"

# ---------------------------------------------------------------- timing (A.3, A.5)
BEAT = 0.5          # the only pause length ever used after an animation
T_WRITE = 1.2       # upper bound for Write
T_FADE = 0.5        # FadeIn / FadeOut
T_MORPH = 1.0       # Transform / TransformMatchingTex
LAG = 0.15          # default lag_ratio for LaggedStart

DIM = 0.35          # opacity for context that is out of focus

# ---------------------------------------------------------------- layout (A.4)
SAFE = 0.6                          # margin on every side
HEADER_Y = 3.25                     # centre of the header band [2.9, 3.6]
LEFT_X, RIGHT_X = -3.6, 3.6         # split-screen centres

# ---------------------------------------------------------------- config
# Only the background is set here. Resolution and frame rate come from the
# quality flag (-ql = 480p15 for drafts, -qh = 1080p60 for the final), because
# code that sets config.pixel_width would silently override -ql.
config.background_color = BG


# ---------------------------------------------------------------- color mixing
def _srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _linear_to_srgb(c):
    c = min(max(c, 0.0), 1.0)
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def _to_oklab(rgb):
    r, g, b = (_srgb_to_linear(c) for c in rgb)
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    return (
        0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
        1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
        0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s,
    )


def _from_oklab(lab):
    L, a, b = lab
    l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    return tuple(_linear_to_srgb(c) for c in (
        4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
    ))


def mix_oklab(c0, c1, t):
    """Mix two colors like CSS `color-mix(in oklab, ...)`.

    The reference page shades its Pascal cells this way. Manim's own
    interpolate_color mixes in sRGB, which gives greyer, darker midtones.
    """
    p = _to_oklab(ManimColor(c0).to_rgb())
    q = _to_oklab(ManimColor(c1).to_rgb())
    return ManimColor(_from_oklab(tuple(a + (b - a) * t for a, b in zip(p, q))))


def cell_colors(value, row_max):
    """(fill, text color) of a Pascal cell, the rule from A.1."""
    t = 0.0 if row_max == 0 else value / row_max
    t = round(t * 100) / 100            # the page rounds to whole percent
    fill = mix_oklab(CELL_LO, CELL_HI, t)
    return fill, (BG if t > 0.55 else INK)
