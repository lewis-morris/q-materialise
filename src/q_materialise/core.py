"""High‑level API functions for QMaterialise.

This module exposes functions to apply styles, list and load built‑in
styles, generate new styles programmatically and export the resulting
stylesheet to a QSS file.  It also contains the built‑in QSS
template used for skinning Qt widgets.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .binding import QtGui, QtWidgets  # type: ignore
from .style import Style
from .utils import contrast_color

THEMES_DIR = Path(__file__).resolve().parent / "styles"


def list_styles() -> List[str]:
    """Returns a list of built-in style names.

    The names correspond to JSON files in the `q_materialise` package's
    `styles` directory without the `.json` extension.

    Returns:
        List[str]: A list of style names.
    """
    styles = []
    if THEMES_DIR.exists():
        for file in THEMES_DIR.iterdir():
            if file.suffix == ".json" and file.is_file():
                styles.append(file.stem)
    return sorted(styles)


def get_style(name: str) -> Style:
    """Loads a built-in style by name.

    Args:
        name (str): Name of the style (without `.json`).

    Returns:
        Style: A `Style` instance.

    Raises:
        FileNotFoundError: If the style file does not exist.
        json.JSONDecodeError: If the style file is invalid.
    """
    path = THEMES_DIR / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"Style '{name}' not found in {THEMES_DIR}")
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    return Style.from_dict(data)


def generate_style(
    name: str, primary: str, secondary: str, is_dark: bool = False, **kwargs: Any
) -> Style:
    """Generates a new style from a few colours.

    This convenience function instantiates a `Style` with the provided
    colours and delegates to its constructor to compute derived values
    (tints, shades and contrast colours). Additional keyword arguments
    are passed through to `Style` and can be used to override derived
    values or supply extras.

    Args:
        name (str): Name of the new style.
        primary (str): The primary colour (hex string).
        secondary (str): The secondary colour (hex string).
        is_dark (bool, optional): Whether the style should be dark. Defaults to False.
        **kwargs: Additional arguments forwarded to `Style`.

    Returns:
        Style: A new `Style` instance.
    """
    return Style(
        name=name, primary=primary, secondary=secondary, is_dark=is_dark, **kwargs
    )


def _build_qss(style: Style, extra: Optional[Dict[str, Any]] = None) -> str:
    """Internal helper to construct the QSS string for a style.

    The `extra` dictionary can define colours for custom button
    classes (`danger`, `warning`, `success`, `info`), the global font
    family and size, and the density scale. Unknown keys are ignored.

    Args:
        style (Style): The style to render.
        extra (Optional[Dict[str, Any]], optional): Optional overrides.

    Returns:
        str: The formatted QSS string.
    """
    extra = extra or {}
    # Font settings
    font_family = extra.get("font_family", "Roboto, sans-serif")
    font_size = extra.get("font_size", "14px")
    density_scale = float(extra.get("density_scale", 0))

    # Compute padding based on density scale.  A positive scale reduces
    # padding to create denser UIs; a negative scale increases it.  Use
    # slightly larger defaults than qt-material to differentiate the
    # appearance and improve touch targets.
    base_padding = 8.0
    base_padding_h = 16.0
    padding_v = max(0.0, base_padding + density_scale)
    padding_h = max(0.0, base_padding_h + 2 * density_scale)

    # Colours for special buttons
    danger = extra.get("danger", "#dc3545")
    warning = extra.get("warning", "#ffc107")
    success = extra.get("success", "#17a2b8")
    info = extra.get("info", "#0d6efd")
    # Compute contrast colours for these if not provided
    on_danger = contrast_color(danger)
    on_warning = contrast_color(warning)
    on_success = contrast_color(success)
    on_info = contrast_color(info)

    variables = {
        "PRIMARY": style.primary,
        "PRIMARY_LIGHT": style.primary_light,
        "PRIMARY_DARK": style.primary_dark,
        "SECONDARY": style.secondary,
        "SECONDARY_LIGHT": style.secondary_light,
        "SECONDARY_DARK": style.secondary_dark,
        "BACKGROUND": style.background,
        "SURFACE": style.surface,
        "TEXT": style.on_background if style.is_dark else style.on_surface,
        "ON_PRIMARY": style.on_primary,
        "ON_SECONDARY": style.on_secondary,
        "ON_BACKGROUND": style.on_background,
        "ON_SURFACE": style.on_surface,
        "ERROR": style.error,
        "ON_ERROR": style.on_error,
        "FONT_FAMILY": font_family,
        "FONT_SIZE": font_size,
        "PADDING_V": f"{padding_v:.0f}",
        "PADDING_H": f"{padding_h:.0f}",
        "DANGER": danger,
        "ON_DANGER": on_danger,
        "WARNING": warning,
        "ON_WARNING": on_warning,
        "SUCCESS": success,
        "ON_SUCCESS": on_success,
        "INFO": info,
        "ON_INFO": on_info,
    }

    # The QSS template.  Curly braces for CSS blocks are escaped with
    # double braces so that ``str.format`` treats them literally.  Only
    # placeholders in uppercase are substituted.  If you add new
    # rules here be careful to escape literal braces by doubling them
    # (``{{`` and ``}}``) because we rely on ``str.format`` for
    # interpolation.
    #
    # The template below defines styles for a broad range of Qt
    # widgets.  In addition to the basics (buttons, labels and text
    # fields) it now includes guidelines for combo boxes, spin boxes,
    # tab widgets, group boxes, item views (list/tree/table), scroll
    # bars, status bars and toolbars.  These additions ensure that
    # applications built with QMaterialise look consistent across
    # commonly used controls in the QtWidgets module of Qt6【904435161404075†L86-L105】.
    qss = """
/* Base settings */
QWidget {{
    background-color: {BACKGROUND};
    color: {ON_BACKGROUND};
    font-family: {FONT_FAMILY};
    font-size: {FONT_SIZE};
}}

/* Text selection */
* {{
    selection-background-color: {PRIMARY_LIGHT};
    selection-color: {ON_PRIMARY};
}}

/* Push buttons */
QPushButton {{
    background-color: {PRIMARY};
    color: {ON_PRIMARY};
    border: none;
    /* Increase the corner radius slightly to soften the look */
    border-radius: 6px;
    padding: {PADDING_V}px {PADDING_H}px;
}}
QPushButton:hover {{
    background-color: {PRIMARY_LIGHT};
}}
QPushButton:pressed {{
    background-color: {PRIMARY_DARK};
}}

/* Custom button classes */
QPushButton[class="danger"] {{
    background-color: {DANGER};
    color: {ON_DANGER};
}}
QPushButton[class="warning"] {{
    background-color: {WARNING};
    color: {ON_WARNING};
}}
QPushButton[class="success"] {{
    background-color: {SUCCESS};
    color: {ON_SUCCESS};
}}
QPushButton[class="info"] {{
    background-color: {INFO};
    color: {ON_INFO};
}}

/* Line edits and text fields */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {SURFACE};
    color: {ON_SURFACE};
    border: 1px solid {PRIMARY_LIGHT};
    /* Match button corner radius for visual consistency */
    border-radius: 6px;
    padding: {PADDING_V}px {PADDING_H}px;
}}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border: 1px solid {PRIMARY};
}}

/* Labels */
QLabel {{
    color: {ON_SURFACE};
}}

/* Check boxes and radio buttons */
QCheckBox, QRadioButton {{
    /* Increase spacing to improve readability */
    spacing: 6px;
}}
QCheckBox::indicator, QRadioButton::indicator {{
    /* Larger indicators with gentle rounding */
    width: 18px;
    height: 18px;
    border: 1px solid {PRIMARY_LIGHT};
    border-radius: 5px;
    background: {SURFACE};
}}
QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
    background-color: {PRIMARY};
    border: 2px solid {PRIMARY};
}}

/* Sliders */
QSlider::groove:horizontal {{
    /* Make the groove slightly thicker for better visibility */
    height: 6px;
    background: {PRIMARY_LIGHT};
}}
QSlider::handle:horizontal {{
    background: {PRIMARY};
    border: none;
    width: 18px;
    /* Centre the handle on the groove */
    margin: -7px 0;
    border-radius: 9px;
}}
QSlider::groove:vertical {{
    width: 6px;
    background: {PRIMARY_LIGHT};
}}
QSlider::handle:vertical {{
    background: {PRIMARY};
    border: none;
    height: 18px;
    margin: 0 -7px;
    border-radius: 9px;
}}

/* Progress bars */
QProgressBar {{
    border: 1px solid {PRIMARY_DARK};
    /* Slightly larger corner radius for a softer look */
    border-radius: 6px;
    background-color: {SURFACE};
    text-align: center;
    color: {ON_SURFACE};
}}
QProgressBar::chunk {{
    background-color: {PRIMARY};
}}

/* Menu bar */
QMenuBar {{
    background-color: {SURFACE};
    color: {ON_SURFACE};
}}
QMenuBar::item:selected {{
    background-color: {PRIMARY_LIGHT};
    color: {ON_PRIMARY};
}}

/* Menus */
QMenu {{
    background-color: {SURFACE};
    color: {ON_SURFACE};
    border: 1px solid {PRIMARY_LIGHT};
}}
QMenu::item:selected {{
    background-color: {PRIMARY_LIGHT};
    color: {ON_PRIMARY};
}}

/* Combo boxes */
QComboBox {{
    background-color: {SURFACE};
    color: {ON_SURFACE};
    border: 1px solid {PRIMARY_LIGHT};
    border-radius: 6px;
    padding: {PADDING_V}px {PADDING_H}px;
}}
QComboBox:hover {{
    border-color: {PRIMARY};
}}
/* Sub‑control for the arrow button on a combo box */
QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 28px;
    border-left: 1px solid {PRIMARY_LIGHT};
    border-top-right-radius: 6px;
    border-bottom-right-radius: 6px;
}}
/* Draw a simple triangle for the arrow using borders */
QComboBox::down-arrow {{
    width: 0;
    height: 0;
    border-left: 6px solid transparent;
    border-right: 6px solid transparent;
    border-top: 8px solid {ON_SURFACE};
}}

/* Spin boxes (integer and floating point) */
QSpinBox, QDoubleSpinBox {{
    background-color: {SURFACE};
    color: {ON_SURFACE};
    border: 1px solid {PRIMARY_LIGHT};
    border-radius: 6px;
    padding-right: 32px; /* leave space for the up/down buttons */
    padding-left: {PADDING_H}px;
    padding-top: {PADDING_V}px;
    padding-bottom: {PADDING_V}px;
}}
/* Buttons for increasing/decreasing values */
QSpinBox::up-button, QDoubleSpinBox::up-button {{
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 16px;
    background: {PRIMARY};
    border-left: 1px solid {PRIMARY_LIGHT};
    border-top-right-radius: 6px;
}}
QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {{
    background: {PRIMARY_LIGHT};
}}
QSpinBox::down-button, QDoubleSpinBox::down-button {{
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 16px;
    background: {PRIMARY};
    border-left: 1px solid {PRIMARY_LIGHT};
    border-bottom-right-radius: 6px;
}}
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
    background: {PRIMARY_LIGHT};
}}
/* Triangle arrows for spin boxes */
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
    width: 0;
    height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 6px solid {ON_PRIMARY};
}}
QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
    width: 0;
    height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid {ON_PRIMARY};
}}

/* Tab widgets */
QTabWidget::pane {{
    border: 1px solid {PRIMARY_LIGHT};
    border-radius: 6px;
    padding: 4px;
}}
QTabBar::tab {{
    background: {SURFACE};
    color: {ON_SURFACE};
    border: 1px solid {PRIMARY_LIGHT};
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: {PADDING_V}px {PADDING_H}px;
    margin-right: 2px;
}}
QTabBar::tab:selected {{
    background: {PRIMARY};
    color: {ON_PRIMARY};
    border-bottom-color: {PRIMARY};
}}
QTabBar::tab:hover {{
    background: {PRIMARY_LIGHT};
}}

/* Group boxes */
QGroupBox {{
    border: 1px solid {PRIMARY_LIGHT};
    border-radius: 6px;
    margin-top: 1.0em;
    color: {ON_SURFACE};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 6px;
}}

/* Abstract item views (list, tree, table) */
QAbstractItemView {{
    background-color: {SURFACE};
    color: {ON_SURFACE};
    border: 1px solid {PRIMARY_LIGHT};
    border-radius: 6px;
    selection-background-color: {PRIMARY_LIGHT};
    selection-color: {ON_PRIMARY};
    alternate-background-color: {BACKGROUND};
}}
/* Headers for tables and trees */
QHeaderView::section {{
    background-color: {PRIMARY};
    color: {ON_PRIMARY};
    padding: 4px;
    border: 1px solid {PRIMARY_LIGHT};
}}

/* Scroll bars */
QScrollBar:vertical {{
    background: {SURFACE};
    width: 12px;
    margin: 0px;
    border-radius: 6px;
}}
QScrollBar::handle:vertical {{
    background: {PRIMARY};
    min-height: 20px;
    border-radius: 6px;
}}
QScrollBar::handle:vertical:hover {{
    background: {PRIMARY_LIGHT};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    background: none;
    height: 0px;
}}
QScrollBar:horizontal {{
    background: {SURFACE};
    height: 12px;
    margin: 0px;
    border-radius: 6px;
}}
QScrollBar::handle:horizontal {{
    background: {PRIMARY};
    min-width: 20px;
    border-radius: 6px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {PRIMARY_LIGHT};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    background: none;
    width: 0px;
}}

/* Status bar */
QStatusBar {{
    background: {SURFACE};
    color: {ON_SURFACE};
    border-top: 1px solid {PRIMARY_LIGHT};
}}

/* Tool bars */
QToolBar {{
    background: {SURFACE};
    border-bottom: 1px solid {PRIMARY_LIGHT};
}}
QToolButton {{
    background-color: {PRIMARY};
    color: {ON_PRIMARY};
    border: none;
    border-radius: 4px;
    padding: 4px 8px;
}}
QToolButton:hover {{
    background-color: {PRIMARY_LIGHT};
}}
QToolButton:pressed {{
    background-color: {PRIMARY_DARK};
}}
"""

    return qss.format(**variables)


def inject_style(
    app: QtWidgets.QApplication,
    style: Union[str, Style, Dict[str, Any]],
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    """Applies a style to a running QApplication.

    This high‑level helper sets both the Qt palette and the
    application‑wide style sheet.  It may be called at any time, even
    after widgets have been created, and the changes take effect
    immediately.  You can pass a built‑in style name, an existing
    :class:`~q_materialise.style.Style` instance or a plain mapping of
    attributes; the latter two options allow you to construct and
    customise styles programmatically.

    The optional ``extra`` dictionary provides fine‑grained
    customisation without having to subclass or manually edit the
    generated QSS.  Recognised keys include:

    ``danger``, ``warning``, ``success``, ``info``
        Define the colours for special button classes.  When a
        :class:`~PySide6.QtWidgets.QPushButton` has its ``class``
        property set to one of these names the corresponding colour
        will be used for its background and the text colour will be
        chosen automatically for contrast.

    ``font_family``, ``font_size``
        Specify the global font family and size used throughout the
        style.  Any valid CSS font family and size expressions are
        accepted.  By default QMaterialise uses ``"Roboto, sans-serif"``
        at ``14px``.  Changing the font can dramatically alter the
        personality of your application; for example, you might set
        ``font_family" : "Fira Code, monospace"`` to give a code editor
        a distinct look.

    ``density_scale``
        Adjusts how much internal padding widgets have.  A positive
        value reduces padding to create denser UIs, whilst a negative
        value increases padding and makes controls easier to click on
        touch devices.  The default is ``0``.  Padding is calculated
        relative to the baseline values defined in the QSS template and
        cannot result in negative sizes.

    Any other keys in ``extra`` are ignored, which makes it safe to
    merge arbitrary dictionaries of settings.  See
    :func:`~q_materialise.export_style` if you want to write the
    resulting stylesheet to a file for use outside of Python.

    Args:
        app: The :class:`~PySide6.QtWidgets.QApplication` instance to style.
        style: A built‑in style name, :class:`~q_materialise.style.Style` or
            mapping.  See :func:`~q_materialise.get_style` and
            :func:`~q_materialise.generate_style` for ways to obtain styles.
        extra: Optional overrides for colours, fonts and density.

    Raises:
        TypeError: If ``style`` is not a recognised type.
    """
    # Convert style argument to Style instance
    if isinstance(style, str):
        the_style = get_style(style)
    elif isinstance(style, Style):
        the_style = style
    elif isinstance(style, dict):
        the_style = Style.from_dict(style)
    else:
        raise TypeError("style must be a string, Style instance or mapping")

    # Build and apply QPalette
    palette = QtGui.QPalette()
    # Background / window colours
    palette.setColor(
        QtGui.QPalette.ColorRole.Window, QtGui.QColor(the_style.background)
    )
    palette.setColor(
        QtGui.QPalette.ColorRole.WindowText, QtGui.QColor(the_style.on_background)
    )
    palette.setColor(QtGui.QPalette.ColorRole.Base, QtGui.QColor(the_style.surface))
    palette.setColor(
        QtGui.QPalette.ColorRole.AlternateBase, QtGui.QColor(the_style.surface)
    )
    palette.setColor(QtGui.QPalette.ColorRole.Text, QtGui.QColor(the_style.on_surface))
    palette.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor(the_style.primary))
    palette.setColor(
        QtGui.QPalette.ColorRole.ButtonText, QtGui.QColor(the_style.on_primary)
    )
    palette.setColor(
        QtGui.QPalette.ColorRole.BrightText, QtGui.QColor(the_style.on_primary)
    )
    palette.setColor(
        QtGui.QPalette.ColorRole.Highlight, QtGui.QColor(the_style.primary)
    )
    palette.setColor(
        QtGui.QPalette.ColorRole.HighlightedText, QtGui.QColor(the_style.on_primary)
    )

    app.setPalette(palette)

    # Build QSS and apply it
    qss = _build_qss(the_style, extra=extra)
    app.setStyleSheet(qss)


def export_style(
    style: Union[str, Style, Dict[str, Any]],
    qss_path: str,
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    """Writes the stylesheet for a style to a QSS file.

    This function does not require a running QApplication. It simply
    loads or constructs the given style, renders the QSS template
    using any overrides provided in `extra` and writes the result to
    `qss_path`. Parent directories are created if necessary.

    Args:
        style (Union[str, Style, Dict[str, Any]]): A style name, dict or Style instance.
        qss_path (str): File path to write the stylesheet to.
        extra (Optional[Dict[str, Any]], optional): Optional overrides for button colours and font settings.

    Raises:
        TypeError: If style is not a string, Style instance, or mapping.
    """
    if isinstance(style, str):
        the_style = get_style(style)
    elif isinstance(style, Style):
        the_style = style
    elif isinstance(style, dict):
        the_style = Style.from_dict(style)
    else:
        raise TypeError("style must be a string, Style instance or mapping")
    qss = _build_qss(the_style, extra=extra)
    dest = Path(qss_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8") as f:
        f.write(qss)
