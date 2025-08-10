import os
import sys

# Use the offscreen platform to run Qt without a display.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# Remove any stubbed modules from other tests so real PySide6 can be loaded.
for name in [
    m for m in list(sys.modules) if m.startswith(("PySide6", "q_materialise"))
]:
    sys.modules.pop(name)

from PySide6 import QtGui, QtWidgets  # type: ignore  # noqa: E402
from q_materialise.core import get_style, inject_style, list_styles  # noqa: E402


def test_lcd_numbers_use_theme_colours() -> None:
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    style_name = list_styles()[0]
    style = get_style(style_name)

    lcd = QtWidgets.QLCDNumber()
    lcd.display(42)

    inject_style(app, style_name)

    assert lcd.segmentStyle() == QtWidgets.QLCDNumber.SegmentStyle.Flat
    palette = lcd.palette()
    assert (
        palette.color(QtGui.QPalette.ColorRole.WindowText).name().lower()
        == style.on_surface.lower()
    )
    assert (
        palette.color(QtGui.QPalette.ColorRole.Window).name().lower()
        == style.surface.lower()
    )
