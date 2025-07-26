"""
Public API for the QMaterialise library.

This module re-exports the most commonly used functions and classes so they
can be imported directly from `q_materialise`. The library is organized into
several submodules:

- `q_materialise.style` contains the `Style` data class representing a complete
  colour scheme. Styles can be created programmatically or loaded from JSON files.
- `q_materialise.utils` provides helper functions for working with colours,
  including RGB/hex conversion, lightening/darkening colours, and calculating
  contrast colours.
- `q_materialise.colors` defines a small set of base colours used by the palette
  generator.
- `q_materialise.binding` exposes the Qt classes from whichever binding
  (PySide6, PyQt6, PySide2, or PyQt5) is available.

The high-level functions imported here form the core API:

- `inject_style` — apply a style to a running QApplication.
- `list_styles` — list the names of the built-in styles.
- `get_style` — load a built-in style from the package.
- `generate_style` — create a style from a small set of inputs.
- `export_style` — write the stylesheet for a style to a QSS file.

Example:
    ```python
    from q_materialise import inject_style
    from PySide6 import QtWidgets

    app = QtWidgets.QApplication([])
    # Apply one of the built-in styles (see `list_styles()` for the full list)
    inject_style(app, style="sapphire_day")
    ...
    ```
"""

from importlib.metadata import version, PackageNotFoundError

try:
    # use the *distribution* name from pyproject.toml
    __version__ = version("q-materialise")
except PackageNotFoundError:
    # fallback if running from source (not yet installed)
    __version__ = "0.1.1"

from .binding import QtCore, QtGui, QtWidgets  # re‑export common Qt classes
from .style import Style
from .core import (
    inject_style,
    export_style,
    list_styles,
    get_style,
    generate_style,
    invert_toolbutton_icons,
)
from .demo import show_demo
__all__ = [
    "QtCore",
    "QtGui",
    "QtWidgets",
    "Style",
    "inject_style",
    "export_style",
    "list_styles",
    "get_style",
    "generate_style",
    "invert_toolbutton_icons",
    "show_demo"
]
