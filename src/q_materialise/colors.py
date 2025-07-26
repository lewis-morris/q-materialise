"""
Base Material Design colours.

This module defines a small collection of base colours that can be combined
with the palette generation functions to produce coherent tints and shades.
Each entry corresponds to the `500` shade from the official Material Design
palette.

These colour names can be used when calling `q_materialise.generate_style` or
when defining your own style JSON files.

The values are taken from the Material Design 2014 specification and are
widely published on the web. See https://material.io/design/color for the full
reference.
"""

BASE_COLORS = {
    # Reds
    "red": "#f44336",
    "pink": "#e91e63",
    "purple": "#9c27b0",
    "deep_purple": "#673ab7",
    # Blues
    "indigo": "#3f51b5",
    "blue": "#2196f3",
    "light_blue": "#03a9f4",
    "cyan": "#00bcd4",
    # Greens
    "teal": "#009688",
    "green": "#4caf50",
    "light_green": "#8bc34a",
    "lime": "#cddc39",
    # Yellows and oranges
    "yellow": "#ffeb3b",
    "amber": "#ffc107",
    "orange": "#ff9800",
    "deep_orange": "#ff5722",
    # Neutrals
    "brown": "#795548",
    "grey": "#9e9e9e",
    "blue_grey": "#607d8b",
}

__all__ = ["BASE_COLORS"]
