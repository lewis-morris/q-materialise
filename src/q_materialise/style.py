"""
Style representation for QMaterialise.

The `Style` class encapsulates all colours and settings required to skin a
Qt application according to Material Design principles. A style can be created
programmatically via `q_materialise.generate_style`, loaded from a JSON file,
or constructed directly from keyword arguments.

In addition to the basic colours (primary, secondary, background, surface, and
error), a style stores precomputed tints and shades (e.g., `primary_light`,
`primary_dark`) and contrast colours (e.g., `on_primary`). These derived values
are generated automatically when the style is initialised but can be overridden
explicitly for full control.

Styles are serialisable to and from JSON to facilitate easy editing and storage.
See the `Style.to_json` and `Style.from_json` methods for details.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional

from . import utils


@dataclass
class Style:
    """A Material Design style for Qt applications.

    All colour attributes must be supplied as hex strings with a leading `#`.
    The `is_dark` flag controls whether text and surface colours default to dark or light values.
    If derived colours (e.g. `primary_light`) are not provided, they will be computed automatically
    from their base colours using sensible defaults.
    """

    name: str
    primary: str
    secondary: str
    is_dark: bool = False
    background: Optional[str] = None
    surface: Optional[str] = None
    error: str = "#f44336"
    primary_light: Optional[str] = None
    primary_dark: Optional[str] = None
    secondary_light: Optional[str] = None
    secondary_dark: Optional[str] = None
    on_primary: Optional[str] = None
    on_secondary: Optional[str] = None
    on_background: Optional[str] = None
    on_surface: Optional[str] = None
    on_error: Optional[str] = None
    extras: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Normalise hex codes to lower case and ensure they start with '#'
        for attr in [
            "primary",
            "secondary",
            "background",
            "surface",
            "error",
            "primary_light",
            "primary_dark",
            "secondary_light",
            "secondary_dark",
            "on_primary",
            "on_secondary",
            "on_background",
            "on_surface",
            "on_error",
        ]:
            value = getattr(self, attr)
            if value is not None:
                norm = self._normalise_hex(value)
                setattr(self, attr, norm)

        # Set default background and surface colours if not provided
        if self.background is None:
            self.background = "#303030" if self.is_dark else "#fafafa"
        if self.surface is None:
            self.surface = "#424242" if self.is_dark else "#ffffff"

        # Compute tints and shades if not supplied
        self.primary_light = self.primary_light or utils.lighten(self.primary, 0.25)
        self.primary_dark = self.primary_dark or utils.darken(self.primary, 0.2)
        self.secondary_light = self.secondary_light or utils.lighten(
            self.secondary, 0.25
        )
        self.secondary_dark = self.secondary_dark or utils.darken(self.secondary, 0.2)

        # Compute contrast colours
        self.on_primary = self.on_primary or utils.contrast_color(self.primary)
        self.on_secondary = self.on_secondary or utils.contrast_color(self.secondary)
        self.on_background = self.on_background or utils.contrast_color(self.background)
        self.on_surface = self.on_surface or utils.contrast_color(self.surface)
        self.on_error = self.on_error or utils.contrast_color(self.error)

    @staticmethod
    def _normalise_hex(value: str) -> str:
        """Ensures a colour string starts with '#' and is lower case.

        Args:
            value (str): The colour string.

        Returns:
            str: Normalised hex colour string.
        """
        s = value.strip().lower()
        if not s.startswith("#"):
            s = "#" + s
        return s

    def to_dict(self) -> Dict[str, Any]:
        """Returns a dictionary representation of the style.

        This includes derived colours and extras. The resulting
        dictionary can be serialised to JSON or passed back into
        `Style` as keyword arguments.

        Returns:
            Dict[str, Any]: Dictionary of style attributes.
        """
        return {
            "name": self.name,
            "primary": self.primary,
            "primary_light": self.primary_light,
            "primary_dark": self.primary_dark,
            "secondary": self.secondary,
            "secondary_light": self.secondary_light,
            "secondary_dark": self.secondary_dark,
            "background": self.background,
            "surface": self.surface,
            "error": self.error,
            "on_primary": self.on_primary,
            "on_secondary": self.on_secondary,
            "on_background": self.on_background,
            "on_surface": self.on_surface,
            "on_error": self.on_error,
            "is_dark": self.is_dark,
            "extras": self.extras,
        }

    def to_json(self, **json_kwargs: Any) -> str:
        """Serialises the style to a JSON string.

        Additional keyword arguments are passed through to `json.dumps`.

        Args:
            **json_kwargs: Additional keyword arguments for `json.dumps`.

        Returns:
            str: JSON string representation of the style.
        """
        return json.dumps(self.to_dict(), **json_kwargs)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Style":
        """Constructs a `Style` from a mapping.

        Unknown keys are ignored. Missing keys will result in
        sensible defaults being calculated.

        Args:
            data (Mapping[str, Any]): Mapping of style attributes.

        Returns:
            Style: A new `Style` instance.
        """
        # Separate known fields from extras. Any unknown keys are collected into
        # the extras dictionary rather than causing a ``TypeError`` when passed
        # directly to the dataclass constructor. This allows style JSON files
        # to include arbitrary extra keys (e.g. ``danger``, ``warning``, etc.)
        # which will be available via ``style.extras``.
        from dataclasses import fields

        known = {f.name for f in fields(cls)}
        kwargs: Dict[str, Any] = {}
        extras: Dict[str, Any] = {}
        for key, value in data.items():
            if key in known:
                kwargs[key] = value
            else:
                extras[key] = value
        # If the style definition already contains an "extras" mapping, merge
        # its contents with any additional unknown keys, giving precedence to
        # the values explicitly defined under "extras".
        if "extras" in kwargs and isinstance(kwargs["extras"], Mapping):
            base_extras = dict(kwargs["extras"])
            base_extras.update(extras)
            extras = base_extras
        kwargs["extras"] = extras
        return cls(**kwargs)  # type: ignore[arg-type]

    @classmethod
    def from_json(cls, json_string: str) -> "Style":
        """Constructs a `Style` from a JSON string.

        Args:
            json_string (str): JSON encoded style data.

        Returns:
            Style: A new `Style` instance.
        """
        data = json.loads(json_string)
        return cls.from_dict(data)
