"""Utility functions for colour manipulation.

This module exposes helpers to convert between hex strings and RGB
tuples, adjust brightness and compute appropriate contrast colours.
All functions in this module are pure and independent of any Qt
classes, making them easy to unit test and reuse.
"""

from __future__ import annotations

from typing import Tuple


def hex_to_rgb(hex_colour: str) -> Tuple[int, int, int]:
    """Convert a hex colour string to an RGB tuple.

    The leading ``#`` is optional.  Three‑digit shorthand notation
    (for example ``"#abc"``) is expanded to six digits before
    parsing.

    Args:
        hex_colour: A colour string in ``#rrggbb`` or ``#rgb`` form.

    Returns:
        Tuple[int, int, int]: A tuple ``(r, g, b)`` representing the
            RGB values.

    Raises:
        ValueError: If the input is not a valid hex colour.
    """
    s = hex_colour.strip().lstrip("#")
    if len(s) == 3:
        s = "".join(ch * 2 for ch in s)
    if len(s) != 6:
        raise ValueError(f"Invalid hex colour: {hex_colour}")
    try:
        r = int(s[0:2], 16)
        g = int(s[2:4], 16)
        b = int(s[4:6], 16)
    except ValueError as e:
        raise ValueError(f"Invalid hex colour: {hex_colour}") from e
    return (r, g, b)


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """Convert an RGB tuple into a hex colour string.

    Values outside the range ``0–255`` are clamped.  The returned
    string always starts with ``#`` and uses lowercase hex digits.

    Args:
        rgb: A tuple ``(r, g, b)`` containing the red, green and blue
            components.

    Returns:
        str: A hex colour string like ``"#00ff00"``.
    """
    r, g, b = (max(0, min(255, int(v))) for v in rgb)
    return f"#{r:02x}{g:02x}{b:02x}"


def lighten(hex_colour: str, factor: float) -> str:
    """Return a colour that is a lighter version of the input.

    Lightening is achieved by interpolating towards white.  A
    ``factor`` of ``0`` returns the original colour and ``1`` returns
    pure white.

    Args:
        hex_colour: The input colour as a hex string.
        factor: Interpolation factor in the inclusive range ``[0, 1]``.

    Returns:
        str: A new hex colour string representing a lighter colour.
    """
    r, g, b = hex_to_rgb(hex_colour)
    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)
    return rgb_to_hex((r, g, b))


def darken(hex_colour: str, factor: float) -> str:
    """Return a colour that is a darker version of the input.

    Darkening is achieved by interpolating towards black.  A
    ``factor`` of ``0`` returns the original colour and ``1`` returns
    pure black.

    Args:
        hex_colour: The input colour as a hex string.
        factor: Interpolation factor in the inclusive range ``[0, 1]``.

    Returns:
        str: A new hex colour string representing a darker colour.
    """
    r, g, b = hex_to_rgb(hex_colour)
    r = int(r * (1 - factor))
    g = int(g * (1 - factor))
    b = int(b * (1 - factor))
    return rgb_to_hex((r, g, b))


def perceived_brightness(hex_colour: str) -> float:
    """Return the perceived brightness of a colour.

    The brightness is computed using the formula defined by the W3C
    ``0.299 × R + 0.587 × G + 0.114 × B``.

    Args:
        hex_colour: The input colour as a hex string.

    Returns:
        float: Perceived brightness in the range ``0–255``.
    """
    r, g, b = hex_to_rgb(hex_colour)
    return 0.299 * r + 0.587 * g + 0.114 * b


def is_light_color(hex_colour: str) -> bool:
    """Return ``True`` if the colour is considered light.

    A colour is classified as light if its perceived brightness is
    greater than or equal to ``186`` (empirically chosen).  This
    threshold is commonly used to decide whether to draw black or
    white text over a background colour.

    Args:
        hex_colour: The input colour as a hex string.

    Returns:
        bool: ``True`` if the colour is light, otherwise ``False``.
    """
    return perceived_brightness(hex_colour) >= 186


def contrast_color(hex_colour: str) -> str:
    """Return black or white depending on the input colour's brightness.

    This helper determines whether a colour is light or dark using
    :func:`is_light_color` and returns ``"#000000"`` for light
    backgrounds and ``"#ffffff"`` for dark backgrounds.  The returned
    value can be used as a foreground colour to ensure sufficient
    contrast.

    Args:
        hex_colour: The input colour as a hex string.

    Returns:
        str: Either ``"#000000"`` (black) or ``"#ffffff"`` (white).
    """
    return "#000000" if is_light_color(hex_colour) else "#ffffff"
