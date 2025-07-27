# Opt-out / bookkeeping flags
import re
from pathlib import Path

from PySide6 import QtCore, QtGui, QtSvg, QtWidgets
from PySide6.QtCore import QDir, QStandardPaths
from PySide6.QtWidgets import QApplication

_NO_TINT_PROP = "_no_icon_tint"
_TINTED_PROP = "_icon_tinted"

_ICONS_DIR = Path(__file__).resolve().parent / "icons"

from xml.etree import ElementTree as ET

_SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", _SVG_NS)

# Shapes that may appear without explicit fill and default to black
_SVG_FILLABLE_TAGS = {
    f"{{{_SVG_NS}}}path",
    f"{{{_SVG_NS}}}rect",
    f"{{{_SVG_NS}}}circle",
    f"{{{_SVG_NS}}}ellipse",
    f"{{{_SVG_NS}}}polygon",
    f"{{{_SVG_NS}}}polyline",
}

def write_svg_with_missing_fill_added(src: Path, dest: Path, fill_hex: str) -> None:
    """
    Read SVG, add fill=fill_hex to elements that *lack* a 'fill' attribute.
    Existing fills (including 'none') are preserved.
    """
    tree = ET.parse(src)
    root = tree.getroot()

    for el in root.iter():
        if el.tag in _SVG_FILLABLE_TAGS:
            # Leave explicit fills alone (including "none")
            if "fill" not in el.attrib:
                el.set("fill", fill_hex)

    # Write back
    dest.write_text(
        ET.tostring(root, encoding="unicode", method="xml"),
        encoding="utf-8",
    )

def _icon_uri(rel: str) -> str:
    return (_ICONS_DIR / rel).as_posix()


def _tint_pixmap(pix: QtGui.QPixmap, color: QtGui.QColor) -> QtGui.QPixmap:
    if pix.isNull():
        return pix
    out = QtGui.QPixmap(pix.size())
    out.fill(QtCore.Qt.GlobalColor.transparent)
    p = QtGui.QPainter(out)
    p.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_Source)
    p.drawPixmap(0, 0, pix)
    p.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_SourceIn)
    p.fillRect(out.rect(), color)
    p.end()
    return out

def _render_svg_tinted(path: Path, size: QtCore.QSize, color: QtGui.QColor) -> QtGui.QPixmap:
    w = size.width() if size.width() > 0 else 24
    h = size.height() if size.height() > 0 else 24
    pm = QtGui.QPixmap(w, h)
    pm.fill(QtCore.Qt.GlobalColor.transparent)
    if QtSvg is not None and path.suffix.lower() == ".svg":
        renderer = QtSvg.QSvgRenderer(str(path))
        p = QtGui.QPainter(pm)
        renderer.render(p)
        p.end()
        return _tint_pixmap(pm, color)
    # Fallback: load raster and tint
    base = QtGui.QPixmap(str(path))
    if not base.isNull():
        base = base.scaled(w, h, QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                           QtCore.Qt.TransformationMode.SmoothTransformation)
        return _tint_pixmap(base, color)
    return pm

def _colorize_icon(icon: QtGui.QIcon, color: QtGui.QColor,
                   sizes=(16, 20, 24, 32, 48)) -> QtGui.QIcon:
    if icon.isNull():
        pm = QtGui.QPixmap(24, 24)
        pm.fill(QtCore.Qt.GlobalColor.transparent)
        return QtGui.QIcon(_tint_pixmap(pm, color))
    out = QtGui.QIcon()
    for s in sizes:
        pm = icon.pixmap(s, s)
        if pm.isNull():
            continue
        out.addPixmap(_tint_pixmap(pm, color))
    return out

def _set_all_icons(app: QtWidgets.QApplication,
                   primary_color: str,
                   default_px: int = 24) -> QApplication:
    class IconProxyStyle(QtWidgets.QProxyStyle):
        def __init__(self, base, color: QtGui.QColor, default_px: int):
            super().__init__(base)
            self._color = color
            self._default_px = default_px

        # Set default icon sizes; explicit setIconSize() still overrides.
        def pixelMetric(self, metric, option=None, widget=None) -> int:
            if metric in (
                QtWidgets.QStyle.PixelMetric.PM_SmallIconSize,
                QtWidgets.QStyle.PixelMetric.PM_ToolBarIconSize,
                QtWidgets.QStyle.PixelMetric.PM_MessageBoxIconSize,
            ):
                return self._default_px
            return super().pixelMetric(metric, option, widget)

        def standardIcon(self, sp, option=None, widget=None) -> QtGui.QIcon:
            # Your custom mapping, now tinted and sized
            if sp == QtWidgets.QStyle.SP_MessageBoxInformation:
                pm = _render_svg_tinted(_ICONS_DIR / "info_outline.svg",
                                        QtCore.QSize(self._default_px, self._default_px),
                                        self._color)
                return QtGui.QIcon(pm)

            base = super().standardIcon(sp, option, widget)
            return _colorize_icon(base, self._color)

    style = IconProxyStyle(app.style(), QtGui.QColor(primary_color), default_px)
    app.setStyle(style)
    return app

def _tint_widget_icons(color: QtGui.QColor, default_px: int = 24) -> None:
    def tint_action(act: QtGui.QAction):
        if act.property(_NO_TINT_PROP) is True or act.property(_TINTED_PROP) is True:
            return
        ic = act.icon()
        if not ic.isNull():
            act.setIcon(_colorize_icon(ic, color))
            act.setProperty(_TINTED_PROP, True)

    for w in QtWidgets.QApplication.allWidgets():
        if w.property(_NO_TINT_PROP) is True:
            continue

        # Common containers of actions
        for act in w.actions():
            tint_action(act)

        # Buttons
        if isinstance(w, QtWidgets.QAbstractButton):
            ic = w.icon()
            if not ic.isNull() and w.property(_TINTED_PROP) is not True:
                w.setIcon(_colorize_icon(ic, color))
                w.setProperty(_TINTED_PROP, True)

        # Tabs
        if isinstance(w, QtWidgets.QTabBar):
            for i in range(w.count()):
                ic = w.tabIcon(i)
                if not ic.isNull():
                    w.setTabIcon(i, _colorize_icon(ic, color))

class _IconTintFilter(QtCore.QObject):
    def __init__(self, color: QtGui.QColor, default_px: int = 24, parent=None):
        super().__init__(parent)
        self._color = color
        self._px = default_px

    def eventFilter(self, obj, ev):
        t = ev.type()
        if t in (QtCore.QEvent.Type.Polish, QtCore.QEvent.Type.Show):
            if isinstance(obj, QtWidgets.QWidget):
                _tint_widget_icons(self._color, self._px)
        if t == QtCore.QEvent.Type.ActionAdded:
            if isinstance(obj, QtWidgets.QWidget):
                for act in obj.actions():
                    if act.property(_NO_TINT_PROP) is not True and act.property(_TINTED_PROP) is not True:
                        ic = act.icon()
                        if not ic.isNull():
                            act.setIcon(_colorize_icon(ic, self._color))
                            act.setProperty(_TINTED_PROP, True)
        return super().eventFilter(obj, ev)

def _apply_global_icon_tint(app: QtWidgets.QApplication,
                            primary_color: str,
                            default_px: int = 24) -> None:
    color = QtGui.QColor(primary_color)
    _tint_widget_icons(color, default_px)
    filt = _IconTintFilter(color, default_px, parent=app)
    app.installEventFilter(filt)
    app._icon_tint_filter = filt  # prevent GC

def _write_tinted_svg(src: Path, dest: Path, fill_hex: str) -> None:
    # naive replace; ensure your SVG uses fill attributes
    text = src.read_text(encoding="utf-8")
    # replace any existing fill=... with your fill; adapt as needed
    text = re.sub(r'fill="[^"]*"', f'fill="{fill_hex}"', text)
    dest.write_text(text, encoding="utf-8")

def _prepare_arrow_icons(primary_hex: str) -> str:
    base = Path(QtCore.QStandardPaths.writableLocation(
        QtCore.QStandardPaths.StandardLocation.AppDataLocation
    ))
    outdir = base / "qmaterialise" / "icons" / primary_hex.lstrip("#")
    outdir.mkdir(parents=True, exist_ok=True)

    write_svg_with_missing_fill_added(_ICONS_DIR / "arrow_drop_down.svg",
                                      outdir / "down.svg", primary_hex)
    write_svg_with_missing_fill_added(_ICONS_DIR / "arrow_drop_up.svg",
                                      outdir / "up.svg", primary_hex)

    QtCore.QDir.setSearchPaths("icons", [str(outdir)])
    return "icons:"