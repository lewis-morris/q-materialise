"""Dynamic import of Qt bindings.

This module attempts to import one of the supported Qt Python bindings
in a well‑defined order: PySide6, PyQt6, PySide2, then PyQt5.  If
none of these are installed an informative :class:`ImportError` is
raised.

The imported modules are re‑exported as ``QtCore``, ``QtGui`` and
``QtWidgets`` so that client code and the rest of this package can
remain agnostic of the underlying binding.  Where there are API
differences between bindings (such as the change from ``exec_`` to
``exec`` in Qt6) the library attempts to cater for them in its own
code.
"""

from __future__ import annotations

from typing import Any

# Determine which binding to use.
_binding = None
_error_messages = []

try:
    from PySide6 import QtCore, QtGui, QtWidgets  # type: ignore[attr-defined]

    _binding = "pyside6"
except ImportError as exc:
    _error_messages.append(f"PySide6: {exc}")

if _binding is None:
    try:
        from PyQt6 import QtCore, QtGui, QtWidgets  # type: ignore[attr-defined]

        _binding = "pyqt6"
    except ImportError as exc:
        _error_messages.append(f"PyQt6: {exc}")

if _binding is None:
    try:
        from PySide2 import QtCore, QtGui, QtWidgets  # type: ignore[attr-defined]

        _binding = "pyside2"
    except ImportError as exc:
        _error_messages.append(f"PySide2: {exc}")

if _binding is None:
    try:
        from PyQt5 import QtCore, QtGui, QtWidgets  # type: ignore[attr-defined]

        _binding = "pyqt5"
    except ImportError as exc:
        _error_messages.append(f"PyQt5: {exc}")

if _binding is None:
    # If no binding could be imported, raise a single ImportError with
    # messages for each attempted binding to aid debugging.
    raise ImportError(
        "No supported Qt binding could be imported. Please install "
        "PySide6, PyQt6, PySide2 or PyQt5. Errors encountered:\n"
        + "\n".join(_error_messages)
    )

# Public API: re‑export the imported modules as if they were part of
# this package.  Downstream code can `from q_materialise.binding import
# QtWidgets` and remain agnostic as to which binding is in use.
__all__ = ["QtCore", "QtGui", "QtWidgets", "binding"]

binding: str = _binding


def exec_(app: Any) -> int:
    """Execute a Qt application instance and return its exit code.

    This convenience wrapper dispatches to the correct method name
    depending on the Qt binding in use.  Recent versions of PySide and
    PyQt expose an ``exec()`` method on QApplication, while older
    versions used ``exec_()``.  Calling this function hides that
    difference.  Typical usage::

        from q_materialise.binding import exec_  # not required if using inject_style
        app = QtWidgets.QApplication(sys.argv)
        return exec_(app)

    Args:
        app: A running QApplication instance.

    Returns:
        int: The exit code returned by the application's event loop.

    Raises:
        RuntimeError: If the given ``app`` does not provide a
            recognised ``exec`` or ``exec_`` method.
    """
    if hasattr(app, "exec"):
        return app.exec()
    elif hasattr(app, "exec_"):
        return app.exec_()
    else:
        raise RuntimeError(
            "Unrecognised QApplication object; cannot find exec() method"
        )
