"""Public API for the QMaterialise library.

This module re‑exports the most commonly used functions and classes so
they can be imported directly from :mod:`q_materialise`.  The
library is organised into several submodules:

* :mod:`q_materialise.style` contains the :class:`~q_materialise.style.Style`
  data class which represents a complete colour scheme.  Styles can be
  created programmatically or loaded from JSON files.
* :mod:`q_materialise.utils` provides helper functions for working with
  colours (conversion between RGB and hex, lightening/darkening colours
  and calculating contrast colours).
* :mod:`q_materialise.colors` defines a small set of base colours used by
  the palette generator.
* :mod:`q_materialise.binding` exposes the Qt classes from whichever
  binding (PySide6, PyQt6, PySide2 or PyQt5) is available.

The high‑level functions imported here form the core API:

* :func:`inject_style` – apply a style to a running QApplication.
* :func:`list_styles` – list the names of the built‑in styles.
* :func:`get_style` – load a built‑in style from the package.
* :func:`generate_style` – create a style from a small set of inputs.
* :func:`export_style` – write the stylesheet for a style to a QSS file.

Example usage::

    from q_materialise import inject_style
    from PySide6 import QtWidgets

    app = QtWidgets.QApplication([])
    # apply one of the built‑in styles (see ``list_styles()`` for the full list)
    inject_style(app, style="sapphire_day")
    ...
"""

from .binding import QtCore, QtGui, QtWidgets  # re‑export common Qt classes
from .style import Style
from .core import inject_style, export_style, list_styles, get_style, generate_style

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
]

__version__ = "0.1.0"