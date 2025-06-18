#!/usr/bin/env python
import sys
from functools import partial

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QStackedLayout,
    QTabWidget,
    QToolBar,
    QWidget,
)

from modules._plugin.base import PluginBase, PluginManager


class MainWindow(QMainWindow):
    USE_TABS = False

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manjaro System Kernels")
        self.setMinimumSize(400, 335)
        self.resize(780, 550)

        if self.USE_TABS:
            self.tabs = QTabWidget()  # TODO rewrite paint() for display icon + text in tab
            self.tabs.setTabPosition(QTabWidget.TabPosition.East)
            self.tabs.setIconSize(QSize(42, 42))
            self.tabs.setTabBarAutoHide(True)
            self.tabs.setStyleSheet("QTabBar::tab { min-width: 100px;  alignment: center;}")
        else:
            self.tabs = QStackedLayout()
        self.tabs.currentChanged.connect(self.module_changed)

        if isinstance(self.tabs, QTabWidget):
            self.setCentralWidget(self.tabs)
        else:
            widget = QWidget()
            widget.setLayout(self.tabs)
            self.setCentralWidget(widget)

        self.toolbar = QToolBar("modules")
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(48, 48))
        self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.toolbar)

        self._init_plugins()

    def _init_plugins(self):
        want_one = ""
        exclude = ("--dev", "--help")
        if args := [a.removeprefix("--").lower() for a in sys.argv if a.startswith("--") and a not in exclude]:
            want_one = args[0]
            print("load one plugin ?", want_one)

        plugin_manager = PluginManager()
        plugin_manager.scan("")

        if "-h" in sys.argv or "--help" in sys.argv:
            self.usage(plugin_manager, want_one)

        self.load_plugins(plugin_manager)

    def load_plugins(self, plugin_manager: PluginManager, want_one=""):
        count = 0
        for name in plugin_manager.modules:
            if want_one and name != want_one:
                continue
            plugin: PluginBase = plugin_manager.modules[name]

            if not plugin.is_enable():
                # plugin is not for this desktop or config
                continue

            # create zone
            widget_class = plugin.get_class()  # get widjet class
            if not widget_class or not issubclass(widget_class, QWidget):
                continue

            widget = widget_class(self)
            widget.windowTitleChanged.connect(self.window_title_changed)
            if not widget:
                continue

            if isinstance(self.tabs, QTabWidget):
                tab_id = self.tabs.addTab(
                    widget,
                    plugin.get_icon(self.tabs.iconSize().height()),
                    "",
                )
            else:
                tab_id = self.tabs.addWidget(widget)
            count += 1

            # create entries
            action = QAction(plugin.get_icon(self.toolbar.iconSize().height()), plugin.get_title(), self)
            action.triggered.connect(partial(self.change_module, tab_id, plugin.NAME))
            self.toolbar.addAction(action)

        self.toolbar.setVisible(count > 1)

    def module_changed(self, tab_id: int):
        self.setWindowTitle(self.tabs.currentWidget().windowTitle())

    def change_module(self, tab_id: int, title: str):
        self.tabs.setCurrentIndex(tab_id)

    def window_title_changed(self, title):
        self.setWindowTitle(title)

    def usage(self, plugin_manager: PluginManager, want_one):
        print()
        print("Available plugins: ", ", ".join(f"--{p.lower()}" for p in plugin_manager.modules.keys()))
        print()
        print("--dev : not run pacman command + create fake EOL")
        exit(0)


app = QApplication([])
window = MainWindow()
window.show()
app.exec()
