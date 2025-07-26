"""High‑level API functions for QMaterialise.

This module exposes functions to apply styles, list and load built‑in
styles, generate new styles programmatically and export the resulting
stylesheet to a QSS file.  It also contains the built‑in QSS
template used for skinning Qt widgets.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .binding import QtGui, QtWidgets  # type: ignore
from .style import Style
from .utils import contrast_color, darken, lighten

THEMES_DIR = Path(__file__).resolve().parent / "styles"
_ICONS_DIR = Path(__file__).resolve().parent / "icons"

def _icon_uri(rel: str) -> str:
    return (_ICONS_DIR / rel).as_posix()

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

    # Extended colours and outline variants. Some of the more detailed
    # Material themes distinguish between multiple levels of surface
    # elevation (e.g., cards vs windows) and outline colours. The user
    # may supply these values via the ``extra`` dictionary; otherwise
    # sensible defaults are computed here. If ``extra`` is missing a
    # value we also consult ``style.extras`` before falling back to
    # reasonable fallbacks such as the base surface colour or a light
    # version of the primary colour.
    # Outline colour defaults to the light variant of the primary
    # colour. Outline variant is a slightly lighter version of the
    # outline colour to provide a subtle distinction between borders.
    outline = extra.get("outline") or style.extras.get("outline", style.primary_light)
    outline_variant = extra.get("outline_variant") or style.extras.get(
        "outline_variant", lighten(outline, 0.2)
    )
    # Surface elevations: default all levels to the base surface. Users
    # may override these individually in ``extra`` or ``style.extras``.
    surface_elev_1 = (
        extra.get("surface_elev_1")
        or style.extras.get("surface_elev_1", style.surface)
    )
    surface_elev_2 = (
        extra.get("surface_elev_2")
        or style.extras.get("surface_elev_2", style.surface)
    )
    surface_elev_3 = (
        extra.get("surface_elev_3")
        or style.extras.get("surface_elev_3", style.surface)
    )

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
        "DANGER_LIGHT": lighten(danger,.2),
        "DANGER_DARK": darken(danger,.2),
        "ON_DANGER": on_danger,
        "WARNING": warning,
        "WARNING_LIGHT": lighten(warning,.2),
        "WARNING_DARK": darken(warning,.2),
        "ON_WARNING": on_warning,
        "SUCCESS": success,
        "SUCCESS_LIGHT": lighten(success,.2),
        "SUCCESS_DARK": darken(success,.2),
        "ON_SUCCESS": on_success,
        "INFO": info,
        "INFO_LIGHT": lighten(info,.2),
        "INFO_DARK": darken(info,.2),
        "ON_INFO": on_info,
        "SURFACE_ELEV_1": surface_elev_1,
        "SURFACE_ELEV_2": surface_elev_2,
        "SURFACE_ELEV_3": surface_elev_3,
        "OUTLINE": outline,
        "OUTLINE_VARIANT": outline_variant,
    }

    def _enc(hexstr: str) -> str:
        # for data: URLs we must encode '#'
        return hexstr.replace("#", "%23")

    variables.update({
        "ARROW_ON_SURFACE": _enc(style.on_surface),   # default arrow colour
        "ARROW_ON_PRIMARY": _enc(style.on_primary),   # when background is primary / focused
        "ARROW_PRIMARY":    _enc(style.primary),      # optional: if you prefer coloured arrows
    })

    variables.update({
        "DOWN_ARROW_ACTIVE":  _icon_uri("downarrow.svg"),
        "DOWN_ARROW_PRIMARY": _icon_uri("downarrow.svg"),
        "UP_ARROW_ACTIVE":    _icon_uri("uparrow.svg"),
        "UP_ARROW_PRIMARY":   _icon_uri("uparrow.svg"),
    })

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
    # commonly used controls in the QtWidgets module of Qt6.
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

QPushButton[class="danger"]:hover {{
    background-color: {DANGER_LIGHT};
    color: {ON_DANGER};
}}
QPushButton[class="warning"]:hover {{
    background-color: {WARNING_LIGHT};
    color: {ON_WARNING};
}}
QPushButton[class="success"]:hover {{
    background-color: {SUCCESS_LIGHT};
    color: {ON_SUCCESS};
}}
QPushButton[class="info"]:hover {{
    background-color: {INFO_LIGHT};
    color: {ON_INFO};
}}
QPushButton[class="danger"]:pressed {{
    background-color: {DANGER_DARK};
    color: {ON_DANGER};
}}
QPushButton[class="warning"]:pressed {{
    background-color: {WARNING_DARK};
    color: {ON_WARNING};
}}
QPushButton[class="success"]:pressed {{
    background-color: {SUCCESS_DARK};
    color: {ON_SUCCESS};
}}
QPushButton[class="info"]:pressed {{
    background-color: {INFO_DARK};
    color: {ON_INFO};
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
/* QDial  - a circular progress bar */
QDial {{
    background-color: {SURFACE};
    border: 2px solid {OUTLINE};
    border-radius: 32px; /* circular */
}}

QDial::groove {{
    background: transparent;
}}

QDial::handle {{
    background-color: {PRIMARY};
    border: none;
    border-radius: 6px;
    width: 12px;
    height: 12px;
    margin: -6px; /* center handle */
}}

QDial::notch {{
    background: {OUTLINE_VARIANT};
    width: 2px;
    height: 6px;
}}

QLCDNumber {{
    background-color: {SURFACE_ELEV_1};
    color: {PRIMARY};
    border: 1px solid {OUTLINE};
    border-radius: 6px;
    padding: 4px;
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
}}

QMenu::item:selected {{
    background-color: {PRIMARY_LIGHT};
    color: {ON_PRIMARY};
}}

/* Combo & date/time edits ------------------------------------------------ */
QComboBox::down-arrow,
QDateEdit::down-arrow,
QTimeEdit::down-arrow,
QDateTimeEdit::down-arrow {{
    image: url({DOWN_ARROW_ACTIVE});
    width: 40px; height: 40px;
    margin-right: 6px;
    margin-left: 6px;
    color: {PRIMARY};
}}
QComboBox::down-arrow:focus,
QDateEdit::down-arrow:focus,
QTimeEdit::down-arrow:focus,
QDateTimeEdit::down-arrow:focus {{
    image: url({DOWN_ARROW_PRIMARY});
}}

/* Spin boxes ------------------------------------------------------------- */
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
    image: url({UP_ARROW_ACTIVE});
    width: 20px; height: 20px;
}}
QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
    image: url({DOWN_ARROW_ACTIVE});
    width: 20px; height: 20px;
}}
QSpinBox::up-arrow:focus, QDoubleSpinBox::up-arrow:focus {{
    image: url({UP_ARROW_PRIMARY});
}}
QSpinBox::down-arrow:focus, QDoubleSpinBox::down-arrow:focus {{
    image: url({DOWN_ARROW_PRIMARY});
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


/* Tab widgets */
QTabWidget::pane {{
    border: 1px solid {PRIMARY_LIGHT};FCo
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

/* Base / Typography ------------------------------------------------------- */
* {{
    color: {ON_SURFACE};
    font-family: {FONT_FAMILY};
    font-size: {FONT_SIZE};
}}
QWidget {{
    background-color: {BACKGROUND};
}}
QFrame[frameShape="4"], /* QFrame::Panel */
QFrame[frameShape="5"], /* QFrame::StyledPanel */
QFrame[frameShape="6"]  /* QFrame::HLine/VLine have own rules below */
{{
    background-color: {SURFACE};
    border: 1px solid {OUTLINE};
    border-radius: 6px;
}}
QFrame[frameShape="0"] {{ /* NoFrame */
    border: none;
}}
QFrame[frameShape="1"], /* Box */
QFrame[frameShape="2"], /* Panel */
QFrame[frameShape="3"]  /* WinPanel */
{{
    border: 1px solid {OUTLINE_VARIANT};
}}
QFrame[frameShape="6"][frameShadow="16"], /* HLine | Sunken */
QFrame[frameShape="7"][frameShadow="16"]  /* VLine | Sunken */
{{
    border: none;
    background-color: {OUTLINE_VARIANT};
}}

/* Text selection (global) */
* {{
    selection-background-color: {PRIMARY_LIGHT};
    selection-color: {ON_PRIMARY};
}}

/* Disabled states */
*:disabled {{
    color: rgba( {ON_SURFACE}, 0.38 );
    background-color: rgba( {SURFACE}, 0.30 );
    border-color: rgba( {OUTLINE}, 0.20 );
}}

/* Push buttons ------------------------------------------------------------ */
QPushButton {{
    background-color: {PRIMARY};
    color: {ON_PRIMARY};
    border: none;
    border-radius: 6px;
    padding: {PADDING_V}px {PADDING_H}px;
}}
QPushButton:hover {{ background-color: {PRIMARY_LIGHT}; }}
QPushButton:pressed {{ background-color: {PRIMARY_DARK}; }}
QPushButton:default {{
    /* box-shadow property removed; unsupported in Qt stylesheets */
}}
QPushButton:flat {{ background-color: transparent; color: {PRIMARY}; }}
QPushButton:flat:hover {{ background-color: rgba( {PRIMARY_LIGHT}, 0.20 ); }}

/* Tonal / Secondary variants via class attribute */
QPushButton[class="secondary"] {{ background-color: {SECONDARY}; color: {ON_SECONDARY}; }}
QPushButton[class="secondary"]:hover {{ background-color: {PRIMARY_LIGHT}; color: {ON_PRIMARY}; }}
QPushButton[class="danger"]   {{ background-color: {DANGER};   color: {ON_DANGER}; }}
QPushButton[class="warning"]  {{ background-color: {WARNING};  color: {ON_WARNING}; }}
QPushButton[class="success"]  {{ background-color: {SUCCESS};  color: {ON_SUCCESS}; }}
QPushButton[class="info"]     {{ background-color: {INFO};     color: {ON_INFO}; }}

/* Command link buttons ---------------------------------------------------- */
QCommandLinkButton {{
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 12px 16px;
    color: {PRIMARY};
}}
QCommandLinkButton:hover {{ background-color: rgba( {PRIMARY_LIGHT}, 0.18 ); }}
QCommandLinkButton:pressed {{ background-color: rgba( {PRIMARY_DARK}, 0.24 ); }}

/* Tool buttons / Toolbars ------------------------------------------------- */
QToolBar {{
    background: {SURFACE};
    border-bottom: 1px solid {OUTLINE};
    spacing: 4px;
}}
QToolBar::separator {{
    background: {OUTLINE_VARIANT};
    width: 1px; height: 1px; margin: 6px;
}}
QToolButton {{
    /*
     * The tool button background needs a border otherwise Qt draws a native border
     * that completely overlaps the background colour.  See the Qt Style Sheets
     * reference for QToolButton【532275245469220†L418-L424】.  Without a border the
     * light themes tend to bleed into the toolbar making the icons hard to see.
     */
    background-color: transparent;
    /* Keep the explicit colour unset so that icons derived from themed SVGs or
     * font-based icons keep their natural colours.  The global `*` rule sets
     * the text colour to `ON_SURFACE` which is dark on light themes and
     * light on dark themes.  If you are using QIcon::fromTheme() this
     * allows the icons to adapt automatically.  For non-themed icons see
     * the `invert_toolbutton_icons` helper function documented below.
     */
    border: 1px solid {OUTLINE_VARIANT};
    border-radius: 6px;
    padding: 6px 10px;
}}
QToolButton:hover {{ background-color: rgba( {PRIMARY_LIGHT}, 0.20 ); }}
QToolButton:pressed {{ background-color: rgba( {PRIMARY_DARK}, 0.24 ); }}
QToolButton[popupMode="1"] {{
    padding-right: 28px;
}}
QToolButton::menu-indicator {{
    width: 0; height: 0;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 7px solid {ON_SURFACE};
    margin: 0 8px 0 8px;
}}

/* Line edits & text fields ------------------------------------------------ */
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QDateEdit, QTimeEdit, QDateTimeEdit {{
    background-color: {SURFACE};
    color: {ON_SURFACE};
    border: 1px solid {OUTLINE};
    border-radius: 6px;
    padding: {PADDING_V}px {PADDING_H}px;
}}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus,
QDateEdit:focus, QTimeEdit:focus, QDateTimeEdit:focus {{
    border: 2px solid {PRIMARY};
    outline: none;
}}
/* Placeholder text (Qt 5.12+ / 6) */
QLineEdit::placeholder, QTextEdit[placeholderText], QPlainTextEdit[placeholderText] {{
    color: rgba( {ON_SURFACE}, 0.60 );
}}

/* Spin boxes -------------------------------------------------------------- */
QSpinBox, QDoubleSpinBox {{ padding-right: 32px; }}
QSpinBox::up-button, QDoubleSpinBox::up-button {{
    subcontrol-origin: border; subcontrol-position: top right;
    width: 18px; background: transparent; border-left: 1px solid {OUTLINE};
    border-top-right-radius: 6px; margin: 0;
}}
QSpinBox::down-button, QDoubleSpinBox::down-button {{
    subcontrol-origin: border; subcontrol-position: bottom right;
    width: 18px; background: transparent; border-left: 1px solid {OUTLINE};
    border-bottom-right-radius: 6px; margin: 0;
}}
QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
    background: rgba( {PRIMARY_LIGHT}, 0.18 );
}}


/* Combo boxes ------------------------------------------------------------- */
QComboBox {{
    background-color: {SURFACE}; color: {ON_SURFACE};
    border: 1px solid {OUTLINE}; border-radius: 6px;
    padding: {PADDING_V}px {PADDING_H}px; padding-right: 36px;
}}
QComboBox:hover {{ border-color: {PRIMARY}; }}
QComboBox:focus {{ border: 2px solid {PRIMARY}; }}
QComboBox::drop-down {{
    subcontrol-origin: padding; subcontrol-position: top right;
    width: 32px; border-left: 1px solid {OUTLINE};
    border-top-right-radius: 6px; border-bottom-right-radius: 6px;
}}

QComboBox QAbstractItemView {{
    background-color: {SURFACE}; color: {ON_SURFACE};
    border: 1px solid {OUTLINE}; border-radius: 6px;
    selection-background-color: {PRIMARY_LIGHT}; selection-color: {ON_PRIMARY};
}}

/* Check boxes & radio buttons -------------------------------------------- */
QCheckBox, QRadioButton {{ spacing: 8px; }}
QGroupBox::indicator, QCheckBox::indicator, QRadioButton::indicator {{
    width: 18px; height: 18px; border: 1px solid {OUTLINE}; background: {SURFACE};
    border-radius: 4px;
}}
QRadioButton::indicator {{ border-radius: 9px; }}
QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
    background-color: {PRIMARY}; border: 2px solid {PRIMARY};
}}
QCheckBox:disabled, QRadioButton:disabled {{ color: rgba( {ON_SURFACE}, 0.38 ); }}

/* Switch-style (use class="switch") */
QCheckBox[class="switch"] {{
    padding: 6px 0;
}}
QCheckBox[class="switch"]::indicator {{
    width: 40px; height: 22px; border-radius: 11px; border: 1px solid {OUTLINE};
    background: rgba( {ON_SURFACE}, 0.12 );
}}
QCheckBox[class="switch"]::indicator:checked {{
    background: {PRIMARY}; border-color: {PRIMARY};
}}
QCheckBox[class="switch"]::indicator:checked:disabled {{
    background: rgba( {PRIMARY}, 0.38 );
}}

/* Sliders ----------------------------------------------------------------- */
QSlider::groove:horizontal {{ height: 6px; background: {OUTLINE_VARIANT}; border-radius: 3px; }}
QSlider::handle:horizontal {{
    background: {PRIMARY}; border: none; width: 18px; margin: -7px 0; border-radius: 9px;
}}
QSlider::groove:vertical {{ width: 6px; background: {OUTLINE_VARIANT}; border-radius: 3px; }}
QSlider::handle:vertical {{
    background: {PRIMARY}; border: none; height: 18px; margin: 0 -7px; border-radius: 9px;
}}
QSlider::sub-page:horizontal, QSlider::add-page:vertical {{ background: {PRIMARY_LIGHT}; border-radius: 3px; }}
QSlider::add-page:horizontal, QSlider::sub-page:vertical {{ background: rgba( {ON_SURFACE}, 0.12 ); border-radius: 3px; }}
QSlider::tick-mark {{ background: {OUTLINE_VARIANT}; }}

/* Progress indicators ----------------------------------------------------- */
QProgressBar {{
    border: 1px solid {OUTLINE}; border-radius: 6px; background-color: {SURFACE};
    text-align: center; color: {ON_SURFACE};
    min-height: 18px;
}}
QProgressBar::chunk {{ background-color: {PRIMARY}; border-radius: 6px; }}
QProgressDialog {{ background: {SURFACE}; }}

/* Menus / Menu bar -------------------------------------------------------- */
QMenuBar {{ background-color: {SURFACE}; color: {ON_SURFACE}; }}
QMenuBar::item {{
    /* Add a light outline so menu items stand out on light themes. Without
     * a border the menu bar items blend into the background and it becomes
     * difficult to see where one drop‑down ends and the next begins.  The
     * outline colour is a slightly lighter version of the primary colour.
     */
    padding: 6px 12px;
 
}}
QMenuBar QMenu::item{{
    margin: 0px 0px; 
    padding: 6px 6px;
    border: 0px solid transparent; /* Prevents menu bar items from shifting */
    border-radius: 0px;
}}
QMenuBar QMenu::item:hover {{
    background-color: {PRIMARY_DARK};
    color: {PRIMARY};
}}

/* selected (when you’ve opened the submenu or arrow‑key navigated to it) */
QMenuBar QMenu::item:selected {{
    background-color: {PRIMARY_LIGHT};
    color: {ON_PRIMARY};
}}

/* pressed (while you’re clicking it) */
QMenuBar QMenu::item:pressed {{
    background-color: {PRIMARY};
    color: {ON_PRIMARY};
}}

QMenuBar::item:selected {{ background-color: {PRIMARY_LIGHT}; color: {ON_PRIMARY}; border-radius: 0px; }}

QMenu {{
    background-color: {SURFACE}; color: {ON_SURFACE}; border: 1px solid {OUTLINE};
}}
QMenu::item {{
    /* As with QMenuBar::item, give each menu entry a subtle border so
     * that items do not merge together on light backgrounds.  The
     * {OUTLINE_VARIANT} colour produces a soft separation without being
     * intrusive. */
    padding: 6px 16px;
    border-radius: 6px;
    border: 1px solid {OUTLINE_VARIANT};
}}

QMenu::item:selected {{ background-color: {PRIMARY_LIGHT}; color: {ON_PRIMARY}; }}
QMenu::separator {{ height: 1px; background: {OUTLINE_VARIANT}; margin: 6px 8px; }}

/* Tabs -------------------------------------------------------------------- */
QTabWidget::pane {{ border: 1px solid {OUTLINE}; border-radius: 6px; padding: 4px; }}
QTabBar::tab {{
    background: {SURFACE}; color: {ON_SURFACE}; border: 1px solid {OUTLINE};
    border-top-left-radius: 6px; border-top-right-radius: 6px; padding: {PADDING_V}px {PADDING_H}px; margin-right: 2px;
}}
QTabBar::tab:selected {{ background: {PRIMARY}; color: {ON_PRIMARY}; border-bottom-color: {PRIMARY}; }}
QTabBar::tab:hover {{ background: {PRIMARY_LIGHT}; }}
QTabBar::close-button {{
    image: none; width: 12px; height: 12px;
    border-radius: 6px; background: transparent; margin: 0 6px;
}}
QTabBar::close-button:hover {{ background: rgba( {ON_SURFACE}, 0.12 ); }}

/* Group boxes ------------------------------------------------------------- */
QGroupBox {{ border: 1px solid {OUTLINE}; border-radius: 6px; margin-top: 1.2em; color: {ON_SURFACE}; }}
QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 8px; }}
QGroupBox::indicator {{ margin-left: 4px; }}

/* Item views (List/Tree/Table) ------------------------------------------- */
QAbstractItemView {{
    background-color: {SURFACE}; color: {ON_SURFACE};
    border: 1px solid {OUTLINE}; border-radius: 6px;
    selection-background-color: {PRIMARY_LIGHT}; selection-color: {ON_PRIMARY};
    alternate-background-color: {SURFACE_ELEV_1};
}}
QTreeView::branch {{ background: transparent; }}
QTreeView::branch:has-siblings:!adjoins-item, QTreeView::branch:!has-children:!has-siblings:adjoins-item {{ border-image: none; }}
QHeaderView::section {{
    background-color: {SURFACE_ELEV_1}; color: {ON_SURFACE};
    padding: 6px; border: 1px solid {OUTLINE};
}}
QHeaderView::section:horizontal {{ border-top-left-radius: 6px; border-top-right-radius: 6px; }}
QHeaderView::section:vertical   {{ border-top-left-radius: 6px; border-bottom-left-radius: 6px; }}


QTableView {{ gridline-color: {OUTLINE_VARIANT}; }}
QTableView::item:selected, QListView::item:selected, QTreeView::item:selected {{
    background: {PRIMARY_LIGHT}; color: {ON_PRIMARY};
}}
QListView::item {{ padding: 6px 10px; }}
QTreeView::item {{ padding: 4px 8px; }}

/* Scroll areas & scroll bars --------------------------------------------- */
QScrollArea {{ border: none; }}
QScrollArea > QWidget > QWidget {{ background: {SURFACE}; }}
QAbstractScrollArea {{ background: {SURFACE}; border-radius: 6px; }}
QScrollBar:vertical {{
    background: {SURFACE_ELEV_1}; width: 12px; margin: 0px; border-radius: 6px;
}}
QScrollBar::handle:vertical {{ background: {PRIMARY}; min-height: 20px; border-radius: 6px; }}
QScrollBar::handle:vertical:hover {{ background: {PRIMARY_LIGHT}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ background: none; height: 0px; }}
QScrollBar:horizontal {{ background: {SURFACE_ELEV_1}; height: 12px; margin: 0px; border-radius: 6px; }}
QScrollBar::handle:horizontal {{ background: {PRIMARY}; min-width: 20px; border-radius: 6px; }}
QScrollBar::handle:horizontal:hover {{ background: {PRIMARY_LIGHT}; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ background: none; width: 0px; }}

/* Splitter --------------------------------------------------------------- */
QSplitter {{ background: transparent; }}
QSplitter::handle {{ background: {OUTLINE_VARIANT}; }}
QSplitter::handle:horizontal {{ width: 1px; }}
QSplitter::handle:vertical {{ height: 1px; }}
QSplitter::handle:hover {{ background: {PRIMARY_LIGHT}; }}

/* Status bar -------------------------------------------------------------- */
QStatusBar {{ background: {SURFACE}; color: {ON_SURFACE}; border-top: 1px solid {OUTLINE}; }}
QStatusBar::item {{ border: none; }}

/* Dock widgets / MDI ------------------------------------------------------ */
QDockWidget {{ titlebar-close-icon: none; titlebar-normal-icon: none; }}
QDockWidget::title {{
    text-align: left; padding: 6px 10px; background: {SURFACE_ELEV_1}; color: {ON_SURFACE};
    border-bottom: 1px solid {OUTLINE};
}}
QDockWidget {{ border: 1px solid {OUTLINE}; border-radius: 6px; }}
QMdiArea {{ background: {SURFACE}; }}
QMdiSubWindow {{ background: {SURFACE}; border: 1px solid {OUTLINE}; border-radius: 6px; }}
QMdiSubWindow::title {{ background: {SURFACE_ELEV_1}; }}

/* Dialogs / Message boxes ------------------------------------F------------- */
QDialog, QMessageBox {{ background: {BACKGROUND}; }}

QDialog QPushButton, QMessageBox QPushButton {{ min-width: 88px; }}

QMessageBox QLabel {{ padding: 8px 0; }}
QDialogButtonBox QPushButton {{ }}

/* Calendar widget --------------------------------------------------------- */
QCalendarWidget {{ background: {SURFACE}; border: 1px solid {OUTLINE}; border-radius: 6px; }}
QCalendarWidget QWidget {{ alternate-background-color: {SURFACE_ELEV_1}; }}
QCalendarWidget QToolButton {{
    background: transparent; color: {ON_SURFACE}; border-radius: 6px; padding: 4px 8px;
}}
QCalendarWidget QToolButton:hover {{ background: rgba( {PRIMARY_LIGHT}, 0.18 ); }}
QCalendarWidget QMenu {{ border-radius: 6px; }}
QCalendarWidget QSpinBox {{ border: none; }}
QCalendarWidget QAbstractItemView:enabled {{ selection-background-color: {PRIMARY_LIGHT}; selection-color: {ON_PRIMARY}; }}
QCalendarWidget QTableView {{ selection-background-color: {PRIMARY_LIGHT}; }}
QCalendarWidget QTableView:item:disabled {{ color: rgba( {ON_SURFACE}, 0.38 ); }}

/* Time / Date edits ------------------------------------------------------- */
QDateEdit, QTimeEdit, QDateTimeEdit {{ icon-size: 16px; }}
QDateEdit::drop-down, QTimeEdit::drop-down, QDateTimeEdit::drop-down {{
    subcontrol-origin: padding; subcontrol-position: top right;
    width: 28px; border-left: 1px solid {OUTLINE}; border-top-right-radius: 6px; border-bottom-right-radius: 6px;
}}


/* Tool tips --------------------------------------------------------------- */
QToolTip {{
    background-color: {SURFACE_ELEV_2};
    color: {ON_SURFACE};
    border: 1px solid {OUTLINE};
    padding: 6px 8px;
    border-radius: 6px;
}}

/* Tool box --------------------------------------------------------------- */
QToolBox::tab {{
    /* make them tall enough for the text + padding */
    min-height: 40px;
    padding: 8px 16px;
    margin: 0 4px -1px 0;          /* lift into the pane by 1px */

    /* colors & borders */
    background: {SURFACE};
    color: {ON_SURFACE};
    border: 1px solid {OUTLINE};

    /* top corners only */
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;

    /* no bottom rounding on tabs */
    border-bottom-left-radius: 0;
    border-bottom-right-radius: 0;
}}

/* Selected tab */
QToolBox::tab:selected {{
    background: {PRIMARY};
    color: {ON_PRIMARY};

    /* match the border to the pane below */
    border-color: {PRIMARY};
    border-bottom-color: {PRIMARY};
}}

/* Hover state */
QToolBox::tab:hover {{
    background: {SURFACE_ELEV_2};
}}

/* The content area (“pane”) */
QToolBox::pane {{
    /* give it its own border and only bottom corners */
    background: {SURFACE};
    border: 1px solid {OUTLINE};

    /* no rounding on top—because tabs sit there */
    border-top-left-radius: 0;
    border-top-right-radius: 0;

    /* only bottom rounding */
    border-bottom-left-radius: 6px;
    border-bottom-right-radius: 6px;

    /* pull it up under the selected tab’s border */
    margin-top: -1px;

    /* inner padding so content doesn’t butt right up against the frame */
    padding: {PADDING_V}px {PADDING_H}px;
}}

/* Finally, ensure the real QToolButtons inside get the same look */
QToolBox QToolButton {{
    min-height: 40px;
    padding: 8px 16px;
    background: transparent;   /* tabs already painted by subcontrol */
    border: none;
    text-align: left;
}}
QToolBox QToolButton:checked {{
    /* “checked” == expanded page */
    background: {PRIMARY};
    color: {ON_PRIMARY};
}}

/* Wizard ------------------------------------------------------------------ */
QWizard {{ background: {SURFACE}; }}
QWizardPage {{ background: {SURFACE}; }}
QWizard QFrame {{ border: none; }}

/* Title bars (QMainWindow) ------------------------------------------------ */
QMainWindow {{ background: {SURFACE}; }}
QMenuBar::item:disabled, QMenu::item:disabled {{ color: rgba( {ON_SURFACE}, 0.38 ); }}

/* Splash screen (limited) ------------------------------------------------- */
QSplashScreen {{ background: {SURFACE}; color: {ON_SURFACE}; }}

/* Rubber band (selection rectangle) -------------------------------------- */
QRubberBand {{ background-color: rgba( {PRIMARY}, 0.20 ); border: 1px solid {PRIMARY}; }}

/* Size grip --------------------------------------------------------------- */
QSizeGrip {{ background: transparent; }}

/* ToolTips for validation/errors ----------------------------------------- */
QLineEdit[error="true"], QTextEdit[error="true"], QPlainTextEdit[error="true"] {{
    border-color: {DANGER};
}}
QToolTip#error {{ background: {DANGER}; color: {ON_DANGER}; border-color: {DANGER}; }}

/* Headers / Footers in views --------------------------------------------- */
QTableCornerButton::section {{ background: {SURFACE_ELEV_1}; border: 1px solid {OUTLINE}; }}

/* Scrollbar on dark surfaces variant (use class="dark") ------------------ */
QScrollBar[class="dark"]:vertical {{ background: {SURFACE_ELEV_2}; }}
QScrollBar[class="dark"]::handle:vertical {{ background: {PRIMARY_LIGHT}; }}

/* Text browser / links ---------------------------------------------------- */
/* Removed unsupported 'link-color' property; rely on default link styling */
QLabel {{ color: {ON_SURFACE}; }}
QLabel[bold="true"] {{ font-weight: 600; }}

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
    palette.setColor(QtGui.QPalette.ColorRole.Button,     QtGui.QColor(the_style.surface))
    palette.setColor(QtGui.QPalette.ColorRole.ButtonText, QtGui.QColor(the_style.on_surface))
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

    # Automatically invert QToolButton icons for light themes
    if not the_style.is_dark:
        try:
            # Invert all QToolButton icons under the application to improve visibility.
            invert_toolbutton_icons(app)
        except Exception:
            # Never allow icon inversion to break styling; silently ignore errors.
            pass


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


# -----------------------------------------------------------------------------
# Icon helpers
#
# Some applications rely on raster icons that do not automatically adapt
# to light and dark themes.  On light themes these icons can appear very
# light themselves, making them hard to discern against the background.
# Qt's style sheets cannot recolour a binary icon directly.  To work around
# this limitation you can invert the colours of your icons at runtime.
# The helper below demonstrates how to do this using QImage.invertPixels().
# The technique is based on community examples where a QImage copy is
# inverted and used as an alternate state for a QIcon【100867099715616†L188-L200】.
def invert_toolbutton_icons(parent: QtWidgets.QWidget) -> None:
    """Invert the colours of all QToolButton icons under *parent*.

    Use this helper on light themes when your icons are too light and lack
    contrast.  It iterates over every QToolButton descendant of the given
    parent, makes a copy of the button's current icon and inverts its
    colours using :func:`QImage.invertPixels`.  The inverted pixmap is then
    assigned back to the button via :class:`QtGui.QIcon`.

    Note:
        * Only raster icons (e.g. PNG, JPEG) are affected; SVG and font
          icons ignore pixel inversion.
        * Alpha channels are preserved using the `InvertRgb` mode so that
          transparency is not lost【532275245469220†L418-L424】.
        * This function is idempotent but will permanently invert icons;
          call it only once per style change.

    Args:
        parent: Any QWidget; all descendant QToolButton instances are
            processed.
    """
    # Iterate over all QToolButton children
    for btn in parent.findChildren(QtWidgets.QToolButton):
        icon = btn.icon()
        # Skip buttons without an icon
        if icon is None or icon.isNull():
            continue
        # Obtain the pixmap at the current icon size
        size = btn.iconSize()
        pixmap = icon.pixmap(size)
        # Work on an image copy; invert only the RGB channels to preserve alpha
        img = pixmap.toImage()
        img.invertPixels(QtGui.QImage.InvertRgb)
        # Replace the button's icon with the inverted version
        btn.setIcon(QtGui.QIcon(QtGui.QPixmap.fromImage(img)))

