"""Tests for stylesheet generation utilities."""

import sys
import types
import unittest
from unittest.mock import patch


class DummyModule(types.ModuleType):
    def __getattr__(self, name: str):  # pragma: no cover - dynamic stub
        stub = type(name, (), {})
        setattr(self, name, stub)
        return stub


qt = DummyModule("PySide6")
qtcore = DummyModule("PySide6.QtCore")
qtgui = DummyModule("PySide6.QtGui")
qtwidgets = DummyModule("PySide6.QtWidgets")
qtsvg = DummyModule("PySide6.QtSvg")
qt.QtCore = qtcore
qt.QtGui = qtgui
qt.QtWidgets = qtwidgets
qt.QtSvg = qtsvg
sys.modules.update(
    {
        "PySide6": qt,
        "PySide6.QtCore": qtcore,
        "PySide6.QtGui": qtgui,
        "PySide6.QtWidgets": qtwidgets,
        "PySide6.QtSvg": qtsvg,
        # Prevent q_materialise.__init__ from importing the real demo module
        "q_materialise.demo": types.ModuleType("q_materialise.demo"),
    }
)

sys.modules["q_materialise.demo"].show_demo = lambda: None

from q_materialise.core import _build_qss, generate_style  # noqa: E402


class TestStyleSheet(unittest.TestCase):
    def setUp(self) -> None:  # noqa: D401
        """Create a basic style for use in tests."""
        self.style = generate_style("test", "#ff0000", "#00ff00")

    def _patched_qss(self) -> str:
        with patch("q_materialise.core._prepare_arrow_icons") as prep:
            prep.side_effect = lambda color, alias: f"{alias}:"
            return _build_qss(self.style)

    def test_arrow_icon_paths_distinct(self) -> None:
        qss = self._patched_qss()
        self.assertIn("image: url(arrow_active:down.svg)", qss)
        self.assertIn("image: url(arrow_primary:down.svg)", qss)
        self.assertIn("image: url(arrow_active:up.svg)", qss)
        self.assertIn("image: url(arrow_primary:up.svg)", qss)

    def test_menu_has_border(self) -> None:
        qss = self._patched_qss()
        self.assertRegex(qss, r"QMenu \{[^}]*border: 1px solid")


if __name__ == "__main__":  # pragma: no cover - manual execution
    unittest.main()
