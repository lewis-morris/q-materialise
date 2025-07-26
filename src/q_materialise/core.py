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
    # placeholders in uppercase are substituted.
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
"""

    return qss.format(**variables)


def inject_style(
    app: QtWidgets.QApplication,
    style: Union[str, Style, Dict[str, Any]],
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    """Applies a style to a running QApplication.

    This function sets the application palette and stylesheet based on
    the provided style. It may be called at any time, even after the
    application has created its widgets. Passing a style name causes
    the corresponding built-in style to be loaded; passing a mapping
    results in a `Style` being constructed; passing a `Style` instance
    uses it directly.

    The optional `extra` dictionary can be used to override button
    colours (`danger`, `warning`, `success`, `info`), specify font
    settings (`font_family`, `font_size`) and adjust the density scale
    (`density_scale`). Unknown keys are ignored.

    Args:
        app (QtWidgets.QApplication): The QApplication to style.
        style (Union[str, Style, Dict[str, Any]]): A style name, dict or Style instance.
        extra (Optional[Dict[str, Any]], optional): Optional overrides for colours and fonts.

    Raises:
        TypeError: If style is not a string, Style instance or mapping.
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
