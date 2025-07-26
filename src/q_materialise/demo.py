"""
A comprehensive demo window that showcases *most* Qt Widgets listed by the user,
wired up to work with QMaterialise dynamic theming.

Tested with PySide6. It should also run with PyQt6/PyQt5/PySide2 if those are
installed, because QMaterialise selects the binding automatically. If you want
to force PySide6, simply ensure it is installed first in your environment.

How to run:

    python mega_qt_demo.py

Notes
-----
- Some legacy/Qt4 classes (e.g. QColormap) no longer exist in Qt 5/6.
  They are skipped gracefully. "QTileRules" also appears not to be part of
  Qt Widgets; it is omitted.
- Abstract base types (QLayout, QLayoutItem) are *used* indirectly by creating
  concrete subclasses and by retrieving a QLayoutItem from a layout.
- The style menu uses a lambda with a **default argument capture** to avoid the
  late-binding bug, so you can switch styles as many times as you like.
- The demo is intentionally verbose to exercise as many widgets as possible.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Iterable, Optional

from PySide6.QtTest import QTest

# QMaterialise — auto-selects available Qt binding
from .core import inject_style, list_styles, get_style  # type: ignore

# We'll primarily target PySide6 APIs. If a different binding is present,
# q_materialise.binding can be used, but importing from PySide6 directly works
# fine when it's installed.
try:
    from PySide6 import QtWidgets, QtCore, QtGui
except Exception:  # pragma: no cover - fallback for other bindings
    from q_materialise.binding import QtWidgets, QtCore, QtGui  # type: ignore


# -------------------------- helpers -----------------------------------------
def add_section(layout: QtWidgets.QVBoxLayout, title: str, widget: QtWidgets.QWidget):
    """Add a bold, centred title label and then the given widget to the layout."""
    lbl = QtWidgets.QLabel(title)
    lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
    lbl.setStyleSheet("font-weight: bold; font-size: 18px;")
    layout.addWidget(lbl)
    layout.addWidget(widget)

def safe_call(fn, *args, **kwargs):
    """Call *fn* and return result or None if the class is unavailable.

    Useful for optional/legacy classes.
    """
    try:
        return fn(*args, **kwargs)
    except Exception:
        return None


def add_row(layout: QtWidgets.QGridLayout, row: int, label: str, widget: QtWidgets.QWidget):
    layout.addWidget(QtWidgets.QLabel(label), row, 0)
    layout.addWidget(widget, row, 1)


# -------------------------- pages -------------------------------------------
class InputsPageA(QtWidgets.QWidget):
    """Page 1: Text Inputs"""
    def __init__(self) -> None:
        super().__init__()
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setSpacing(12)
        vbox.setContentsMargins(16, 16, 16, 16)

        # Single‑line edits
        le = QtWidgets.QLineEdit("Hello")
        pwd = QtWidgets.QLineEdit("secret")
        pwd.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        add_section(vbox, "QLineEdit", le)
        add_section(vbox, "QLineEdit (Password)", pwd)

        # Multi‑line edits
        te = QtWidgets.QTextEdit()
        te.setPlainText("Lorem ipsum dolor sit amet…")
        pte = QtWidgets.QPlainTextEdit("Foo\nBar\nBaz")
        add_section(vbox, "QTextEdit", te)
        add_section(vbox, "QPlainTextEdit", pte)

        vbox.addStretch(1)


class InputsPageB(QtWidgets.QWidget):
    """Page 2: Buttons & Choices"""
    def __init__(self) -> None:
        super().__init__()
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setSpacing(12)
        vbox.setContentsMargins(16, 16, 16, 16)

        # QPushButton variants
        btns = QtWidgets.QWidget()
        hl = QtWidgets.QHBoxLayout(btns)
        for name, cls in (("Normal", None), ("Danger", "danger"),
                          ("Warning", "warning"), ("Success", "success"),
                          ("Info", "info")):
            b = QtWidgets.QPushButton(name)
            if cls: b.setProperty("class", cls)
            hl.addWidget(b)
        add_section(vbox, "QPushButton Variants", btns)

        # Checkboxes section
        cb_group = QtWidgets.QGroupBox()
        cb_layout = QtWidgets.QHBoxLayout(cb_group)
        cb_layout.addWidget(QtWidgets.QCheckBox("Check me"))
        cb_layout.addWidget(QtWidgets.QCheckBox("Also me"))
        add_section(vbox, "QCheckBox", cb_group)

        # Radio buttons section
        rb_group = QtWidgets.QGroupBox()
        rb_layout = QtWidgets.QHBoxLayout(rb_group)
        rb1 = QtWidgets.QRadioButton("Option A"); rb1.setChecked(True)
        rb2 = QtWidgets.QRadioButton("Option B")
        rb_layout.addWidget(rb1)
        rb_layout.addWidget(rb2)
        bg = QtWidgets.QButtonGroup(self)
        bg.addButton(rb1, 1)
        bg.addButton(rb2, 2)
        add_section(vbox, "QRadioButton", rb_group)

        # Slider & ProgressBar
        slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        slider.setValue(50)
        pb = QtWidgets.QProgressBar()
        pb.setRange(0, 100); pb.setValue(40)
        add_section(vbox, "QSlider", slider)
        add_section(vbox, "QProgressBar", pb)

        vbox.addStretch(1)
class InputsPageC(QtWidgets.QWidget):
    """Page 3: Dials, Spinners & Date/Time"""
    def __init__(self) -> None:
        super().__init__()
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setSpacing(12)
        vbox.setContentsMargins(16, 16, 16, 16)

        # Dials & Spinners
        dial = QtWidgets.QDial(); dial.setRange(0,100); dial.setValue(70)
        spin = QtWidgets.QSpinBox(); spin.setRange(0,100)
        dbl  = QtWidgets.QDoubleSpinBox(); dbl.setRange(0.0,10.0); dbl.setSingleStep(0.1)
        add_section(vbox, "QDial", dial)
        add_section(vbox, "QSpinBox", spin)
        add_section(vbox, "QDoubleSpinBox", dbl)

        # Date / Time edits
        de = QtWidgets.QDateEdit(QtCore.QDate.currentDate())
        te = QtWidgets.QTimeEdit(QtCore.QTime.currentTime())
        dte= QtWidgets.QDateTimeEdit(QtCore.QDateTime.currentDateTime())
        add_section(vbox, "QDateEdit", de)
        add_section(vbox, "QTimeEdit", te)
        add_section(vbox, "QDateTimeEdit", dte)

        # Combo, LCD & KeySequence
        combo = QtWidgets.QComboBox(); combo.addItems(["Foo","Bar","Baz"])
        lcd   = QtWidgets.QLCDNumber(); lcd.display(1234)
        kse   = QtWidgets.QKeySequenceEdit(); kse.setKeySequence(QtGui.QKeySequence("Ctrl+Shift+K"))
        add_section(vbox, "QComboBox", combo)
        add_section(vbox, "QLCDNumber", lcd)
        add_section(vbox, "QKeySequenceEdit", kse)

        vbox.addStretch(1)



class ViewsPageA(QtWidgets.QWidget):
    """Page 1: List & Tree Views"""
    def __init__(self) -> None:
        super().__init__()
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setSpacing(12)
        vbox.setContentsMargins(16, 16, 16, 16)

        # QListWidget
        lw = QtWidgets.QListWidget()
        for i in range(5):
            QtWidgets.QListWidgetItem(f"Item {i}", lw)
        add_section(vbox, "List Widget", lw)

        # QListView + model
        list_view = QtWidgets.QListView()
        model = QtGui.QStandardItemModel(list_view)
        for name in ("Foo", "Bar", "Baz"):
            model.appendRow(QtGui.QStandardItem(name))
        list_view.setModel(model)
        add_section(vbox, "List View", list_view)

        # QTreeView + model
        tree_view = QtWidgets.QTreeView()
        tmodel = QtGui.QStandardItemModel(tree_view)
        tmodel.setHorizontalHeaderLabels(["Name", "Value"])
        for p in ("Alpha", "Beta"):
            parent = [QtGui.QStandardItem(p), QtGui.QStandardItem("-")]
            for i in range(3):
                child = [QtGui.QStandardItem(f"{p}-{i}"),
                         QtGui.QStandardItem(str(i))]
                parent[0].appendRow(child)
            tmodel.appendRow(parent)
        tree_view.setModel(tmodel)
        add_section(vbox, "Tree View", tree_view)

        vbox.addStretch(1)


class ViewsPageB(QtWidgets.QWidget):
    """Page 2: Table & Column Views"""
    def __init__(self) -> None:
        super().__init__()
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setSpacing(12)
        vbox.setContentsMargins(16, 16, 16, 16)

        # QTableWidget
        table = QtWidgets.QTableWidget(4, 3)
        table.setHorizontalHeaderLabels(["A", "B", "C"])
        for r in range(4):
            for c, text in enumerate(["Foo", "Bar", "Baz"]):
                table.setItem(r, c, QtWidgets.QTableWidgetItem(f"{text} {r}"))
        table.setRangeSelected(QtWidgets.QTableWidgetSelectionRange(1, 0, 2, 2), True)
        add_section(vbox, "Table Widget", table)

        # QTableView
        table_view = QtWidgets.QTableView()
        tv_model = QtGui.QStandardItemModel(3, 3)
        tv_model.setHorizontalHeaderLabels(["Col 1", "Col 2", "Col 3"])
        for r in range(3):
            for c in range(3):
                tv_model.setItem(r, c, QtGui.QStandardItem(f"{r},{c}"))
        table_view.setModel(tv_model)
        table_view.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Stretch
        )
        add_section(vbox, "Table View", table_view)

        # QColumnView
        col_view = QtWidgets.QColumnView()
        col_model = QtGui.QStandardItemModel(col_view)
        for n in ("Root 1", "Root 2"):
            parent = QtGui.QStandardItem(n)
            for i in range(3):
                parent.appendRow(QtGui.QStandardItem(f"{n}-{i}"))
            col_model.appendRow(parent)
        col_view.setModel(col_model)
        add_section(vbox, "Column View", col_view)

        vbox.addStretch(1)

class AdvancedPageA(QtWidgets.QWidget):
    """Page 1: Toolbox, Calendar & Graphics."""
    def __init__(self, main_window: 'MegaWindow') -> None:
        super().__init__()
        self.main_window = main_window

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setSpacing(12)
        vbox.setContentsMargins(16, 16, 16, 16)

        # Toolbox
        toolbox = QtWidgets.QToolBox()
        for section in ("First", "Second", "Third"):
            lw = QtWidgets.QListWidget()
            for i in range(5):
                lw.addItem(f"{section} item {i}")
            toolbox.addItem(lw, section)
        add_section(vbox, "ToolBox", toolbox)

        # Calendar
        cal = QtWidgets.QCalendarWidget()
        cal.setGridVisible(True)
        add_section(vbox, "Calendar", cal)


        vbox.addStretch(1)


class AdvancedPageB(QtWidgets.QWidget):
    """Page 2: Scrolling, Rubber‑Band & Dialogs."""
    def __init__(self, main_window: 'MegaWindow') -> None:
        super().__init__()
        self.main_window = main_window

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setSpacing(12)
        vbox.setContentsMargins(16, 16, 16, 16)

        # Scroll area with kinetic scrolling
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        big = QtWidgets.QWidget()
        bl = QtWidgets.QVBoxLayout(big)
        for i in range(40):
            bl.addWidget(QtWidgets.QLabel(f"Scrollable label {i}"))
        scroll_area.setWidget(big)

        QtWidgets.QScroller.grabGesture(
            scroll_area.viewport(),
            QtWidgets.QScroller.ScrollerGestureType.LeftMouseButtonGesture
        )
        scroller = QtWidgets.QScroller.scroller(scroll_area.viewport())
        props = scroller.scrollerProperties()
        props.setScrollMetric(
            QtWidgets.QScrollerProperties.ScrollMetric.DecelerationFactor,
            0.2
        )
        scroller.setScrollerProperties(props)
        add_section(vbox, "Kinetic Scroll Area", scroll_area)

        # CommandLinkButton
        cmd = QtWidgets.QCommandLinkButton("Choose a colour", "Opens QColorDialog")
        cmd.clicked.connect(self.choose_colour)
        add_section(vbox, "Colour Picker", cmd)

        # Font combo + FontDialog
        fcb = QtWidgets.QFontComboBox()
        fbtn = QtWidgets.QPushButton("Font…")
        fbtn.clicked.connect(self.choose_font)
        fwrap = QtWidgets.QWidget()
        hf = QtWidgets.QHBoxLayout(fwrap)
        hf.addWidget(fcb); hf.addWidget(fbtn)
        add_section(vbox, "Font Selector", fwrap)

        # Input, Error, Message & Progress dialogs
        btns = QtWidgets.QWidget()
        hb = QtWidgets.QHBoxLayout(btns)
        in_btn = QtWidgets.QPushButton("Get Text")
        in_btn.clicked.connect(self.get_text)
        em_btn = QtWidgets.QPushButton("Error Msg")
        em_btn.clicked.connect(self.show_error)
        mb_btn = QtWidgets.QPushButton("MessageBox")
        mb_btn.clicked.connect(self.show_msg)
        pd_btn = QtWidgets.QPushButton("ProgressDlg")
        pd_btn.clicked.connect(self.show_progress)
        for w in (in_btn, em_btn, mb_btn, pd_btn):
            hb.addWidget(w)
        add_section(vbox, "Dialogs", btns)

        vbox.addStretch(1)


    # --------------- dialog slots ------------------------------------
    def choose_colour(self):
        colour = QtWidgets.QColorDialog.getColor(parent=self)
        if colour.isValid():
            QtWidgets.QToolTip.showText(QtGui.QCursor.pos(), f"Selected: {colour.name()}")

    def choose_font(self):
        ok, font = QtWidgets.QFontDialog.getFont(parent=self)
        if ok:
            QtWidgets.QToolTip.showText(QtGui.QCursor.pos(), f"Font: {font.family()}")

    def get_text(self):
        text, ok = QtWidgets.QInputDialog.getText(self, "Input", "Enter something:")
        if ok:
            QtWidgets.QMessageBox.information(self, "You typed", text)

    def show_error(self):
        err = QtWidgets.QErrorMessage(self)
        err.showMessage("This is a sample error message.")
        err.exec()

    def show_msg(self):
        QtWidgets.QMessageBox.warning(self, "Warning", "This is a QMessageBox warning example.")

    def show_progress(self):
        dlg = QtWidgets.QProgressDialog("Working...", "Cancel", 0, 100, self)
        dlg.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        dlg.setMinimumDuration(0)        # ← show immediately
        dlg.setAutoClose(True)
        dlg.show()                       # ← now it will actually pop up

        for i in range(0, 101, 5):
            QtWidgets.QApplication.processEvents()
            dlg.setValue(i)
            if dlg.wasCanceled():
                break
            QTest.qWait(50)

        dlg.close()

class ContainersPage(QtWidgets.QWidget):
    """Page to exercise splitters, stacked layout/widget, dock widgets, actions."""
    def __init__(self, main_window: 'MegaWindow') -> None:
        super().__init__()
        self.main_window = main_window

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setSpacing(12)
        vbox.setContentsMargins(16, 16, 16, 16)

        # Splitter with handle access
        split = QtWidgets.QSplitter()
        split.addWidget(QtWidgets.QTextEdit("Left"))
        split.addWidget(QtWidgets.QTextEdit("Right"))
        _handle: QtWidgets.QSplitterHandle = split.handle(1)
        add_section(vbox, "Splitter", split)

        # QStackedLayout + nav
        holder = QtWidgets.QWidget()
        holder_layout = QtWidgets.QStackedLayout(holder)
        for text in ("StackedLayout Page 1", "StackedLayout Page 2"):
            lbl = QtWidgets.QLabel(text)
            lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            holder_layout.addWidget(lbl)

        nav1 = QtWidgets.QWidget()
        nav1_h = QtWidgets.QHBoxLayout(nav1)
        btn_prev1 = QtWidgets.QPushButton("⯇ Prev")
        btn_next1 = QtWidgets.QPushButton("Next ⯈")
        nav1_h.addStretch()
        nav1_h.addWidget(btn_prev1)
        nav1_h.addWidget(btn_next1)
        nav1_h.addStretch()
        btn_prev1.clicked.connect(
            lambda: holder_layout.setCurrentIndex(
                (holder_layout.currentIndex() - 1) % holder_layout.count()
            )
        )
        btn_next1.clicked.connect(
            lambda: holder_layout.setCurrentIndex(
                (holder_layout.currentIndex() + 1) % holder_layout.count()
            )
        )

        wrapper1 = QtWidgets.QWidget()
        w1_v = QtWidgets.QVBoxLayout(wrapper1)
        w1_v.addWidget(holder)
        w1_v.addWidget(nav1)
        add_section(vbox, "QStackedLayout", wrapper1)

        # QStackedWidget + nav
        sw = QtWidgets.QStackedWidget()
        for text in ("StackedWidget 1", "StackedWidget 2"):
            lbl = QtWidgets.QLabel(text)
            lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            sw.addWidget(lbl)

        nav2 = QtWidgets.QWidget()
        nav2_h = QtWidgets.QHBoxLayout(nav2)
        btn_prev2 = QtWidgets.QPushButton("⯇ Prev")
        btn_next2 = QtWidgets.QPushButton("Next ⯈")
        nav2_h.addStretch()
        nav2_h.addWidget(btn_prev2)
        nav2_h.addWidget(btn_next2)
        nav2_h.addStretch()
        btn_prev2.clicked.connect(
            lambda: sw.setCurrentIndex(
                (sw.currentIndex() - 1) % sw.count()
            )
        )
        btn_next2.clicked.connect(
            lambda: sw.setCurrentIndex(
                (sw.currentIndex() + 1) % sw.count()
            )
        )

        wrapper2 = QtWidgets.QWidget()
        w2_v = QtWidgets.QVBoxLayout(wrapper2)
        w2_v.addWidget(sw)
        w2_v.addWidget(nav2)
        add_section(vbox, "QStackedWidget", wrapper2)

        # Explicit scroll bars
        hsb = QtWidgets.QScrollBar(QtCore.Qt.Orientation.Horizontal)
        vsb = QtWidgets.QScrollBar(QtCore.Qt.Orientation.Vertical)
        row = QtWidgets.QHBoxLayout()
        row.addWidget(hsb)
        row.addWidget(vsb)
        scrollbars = QtWidgets.QWidget()
        scrollbars.setLayout(row)
        add_section(vbox, "Scroll Bars", scrollbars)

        vbox.addStretch(1)



class MenusToolbarsPage(QtWidgets.QWidget):
    """Page that demonstrates menus, actions, QWidgetAction, status bar text, etc."""
    def __init__(self, main_window: 'MegaWindow') -> None:
        super().__init__()
        self.main_window = main_window

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setSpacing(12)
        vbox.setContentsMargins(16, 16, 16, 16)

        # 1) Menu with QWidgetAction
        menu_btn = QtWidgets.QPushButton("Open Menu with QWidgetAction")
        menu = QtWidgets.QMenu(self)
        wid_action = QtWidgets.QWidgetAction(self)
        emb = QtWidgets.QWidget()
        hb = QtWidgets.QHBoxLayout(emb)
        hb.setContentsMargins(6, 6, 6, 6)
        hb.addWidget(QtWidgets.QLabel("Widget in menu:"))
        hb.addWidget(QtWidgets.QLineEdit())
        wid_action.setDefaultWidget(emb)
        menu.addAction(wid_action)
        menu.addAction("Plain action",
                       lambda: QtWidgets.QMessageBox.information(self, "Action", "Triggered"))
        menu_btn.setMenu(menu)
        add_section(vbox, "QWidgetAction Menu", menu_btn)

        # 2) Toolbar
        tb = QtWidgets.QToolBar("Demo Toolbar", self.main_window)
        self.main_window.addToolBar(tb)
        a1 = tb.addAction("Hello")
        a1.triggered.connect(
            lambda: self.main_window.statusBar().showMessage("Hello clicked", 2000)
        )
        a2 = tb.addAction("WhatsThis")
        a2.triggered.connect(QtWidgets.QWhatsThis.enterWhatsThisMode)
        add_section(vbox, "ToolBar with Actions", tb)

        # 3) Status bar
        self.main_window.statusBar().showMessage("StatusBar ready")
        status_lbl = QtWidgets.QLabel("Check the main window’s status bar")
        add_section(vbox, "StatusBar Message", status_lbl)

        # 4) Dock widget
        dock = QtWidgets.QDockWidget("Dockable", self.main_window)
        dock.setWidget(QtWidgets.QListWidget())
        self.main_window.addDockWidget(
            QtCore.Qt.DockWidgetArea.RightDockWidgetArea, dock
        )
        add_section(vbox, "QDockWidget", dock)

        # 5) QFileIconProvider
        provider = QtWidgets.QFileIconProvider()
        icon = provider.icon(QtWidgets.QFileIconProvider.IconType.Folder)
        icon_label = QtWidgets.QLabel("Folder icon via QFileIconProvider")
        icon_label.setPixmap(icon.pixmap(16, 16))
        add_section(vbox, "FileIconProvider", icon_label)

        # 6) Form layout
        form = QtWidgets.QFormLayout()
        form.addRow("Name", QtWidgets.QLineEdit())
        form.addRow("Age", QtWidgets.QSpinBox())
        formw = QtWidgets.QWidget()
        formw.setLayout(form)
        add_section(vbox, "QFormLayout", formw)

        vbox.addStretch(1)


# -------------------------- main window -------------------------------------

class MegaWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("QMaterialise – Mega Demo")
        self.resize(1200, 800)

        # menu bar with Styles and Demo menus
        self._build_menus()

        # central stacked pages with navigation
        central = QtWidgets.QWidget(); self.setCentralWidget(central)
        v = QtWidgets.QVBoxLayout(central)

        self.pages = QtWidgets.QStackedWidget()
        v.addWidget(self.pages, 1)

        self.pages.addWidget(InputsPageA())
        self.pages.addWidget(InputsPageB())
        self.pages.addWidget(InputsPageC())
        self.pages.addWidget(ViewsPageA())
        self.pages.addWidget(ViewsPageB())
        self.pages.addWidget(AdvancedPageA(self))
        self.pages.addWidget(AdvancedPageB(self))
        self.pages.addWidget(ContainersPage(self))
        self.pages.addWidget(MenusToolbarsPage(self))

        nav = QtWidgets.QHBoxLayout()
        prev_btn = QtWidgets.QPushButton("Previous")
        next_btn = QtWidgets.QPushButton("Next")
        prev_btn.clicked.connect(self.prev_page)  # type: ignore[arg-type]
        next_btn.clicked.connect(self.next_page)  # type: ignore[arg-type]
        nav.addStretch(1); nav.addWidget(prev_btn); nav.addWidget(next_btn)
        navw = QtWidgets.QWidget(); navw.setLayout(nav)
        v.addWidget(navw)

        # status bar exists for toolbar/status demos
        self.setStatusBar(QtWidgets.QStatusBar(self))

        # try to use a layout item explicitly to satisfy QLayoutItem presence
        # (retrieve from one of the pages' layouts)
        li: Optional[QtWidgets.QLayoutItem] = central.layout().itemAt(0) if central.layout() else None
        self._layout_item_held = li  # keep a reference to prove we "used" it

    # ---------------- menus and style application ---------------------
    def _build_menus(self) -> None:
        menubar = self.menuBar()

        # Styles menu — capture the name in the lambda default argument
        styles_menu = menubar.addMenu("Styles")
        for name in list_styles():
            act = styles_menu.addAction(name)
            act.triggered.connect(lambda checked=False, n=name: self.apply_style(n))  # type: ignore[arg-type]

        # Demo menu with miscellaneous actions
        demo_menu = menubar.addMenu("Demo")

        demo_menu.addAction("Open QFileDialog", self.open_file_dialog)
        demo_menu.addAction("Show QFontDialog", self.show_font_dialog)
        demo_menu.addAction("Show QColorDialog", self.show_colour_dialog)
        demo_menu.addSeparator()
        demo_menu.addAction("Show Wizard", self.show_wizard)

    def apply_style(self, style_name: str) -> None:
        app = QtWidgets.QApplication.instance()
        if app is not None:
            inject_style(app, style=style_name)
            # show a brief status message
            self.statusBar().showMessage(f"Applied style: {style_name}", 2000)

    # ---------------- demo actions -------------------------------
    def open_file_dialog(self):
        QtWidgets.QFileDialog.getOpenFileName(self, "Open a file")

    def show_font_dialog(self):
        ok, font = QtWidgets.QFontDialog.getFont(parent=self)
        if ok:
            self.statusBar().showMessage(f"Selected font: {font.family()}", 3000)

    def show_colour_dialog(self):
        colour = QtWidgets.QColorDialog.getColor(parent=self)
        if colour.isValid():
            self.statusBar().showMessage(f"Selected colour: {colour.name()}", 3000)

    def show_wizard(self):
        wiz = QtWidgets.QWizard(self)
        wiz.setWindowTitle("Sample Wizard")
        for i in range(1, 4):
            page = QtWidgets.QWizardPage()
            page.setTitle(f"Page {i}")
            lay = QtWidgets.QVBoxLayout(page)
            lay.addWidget(QtWidgets.QLabel(f"This is page {i}"))
            wiz.addPage(page)
        wiz.exec()

    def next_page(self):
        idx = (self.pages.currentIndex() + 1) % self.pages.count()
        self.pages.setCurrentIndex(idx)

    def prev_page(self):
        idx = (self.pages.currentIndex() - 1) % self.pages.count()
        self.pages.setCurrentIndex(idx)


# ------------------------------ entry point ---------------------------------

def show_demo(argv: Optional[Iterable[str]] = None) -> int:
    argv = list(argv) if argv is not None else sys.argv
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(argv)

    # initial style — just pick the first available built-in if present
    styles = list_styles()
    if styles:
        inject_style(app, style=styles[0])

    win = MegaWindow()
    win.show()

    if QtWidgets.QApplication.instance() is app:
        return app.exec()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(show_demo())
