#!/usr/bin/env python
import sys
from functools import partial
from pathlib import Path

from PySide6.QtCore import (
    QLibraryInfo,
    QLocale,
    QSize,
    Qt,
    QTextStream,
    QTranslator,
    Signal,
)
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QSizePolicy,
    QStackedLayout,
    QTabWidget,
    QToolBar,
    QWidget,
)

try:
    from modules._plugin.base import PluginBase, PluginManager
except ImportError:
    # if run as module
    from .modules._plugin.base import PluginBase, PluginManager


class MainWindow(QMainWindow):
    USE_TABS = False

    def __init__(self, plugins: PluginManager, want_one=""):
        super().__init__()
        self.plugins = plugins
        self.plugins.loaded.connect(self.plugin_loaded)
        self.plugins.loaded_end.connect(self.plugins_loaded)
        self.want_one = want_one
        self.setWindowTitle(self.tr("Manjaro System Kernels"))
        self.setWindowIcon(QIcon.fromTheme("manjaro"))
        self.setMinimumSize(400, 335)
        self.resize(790, 600)

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
        self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.toolbar)

    def load_plugins(self):
        # not call by this object !
        icon_size = self.plugins.get_icon_size()
        self.toolbar.setIconSize(QSize(icon_size, icon_size))

        # create menu
        is_first = True
        for name in self.plugins.modules:
            if self.want_one and name != self.want_one:
                continue
            plugin: PluginBase = self.plugins.modules[name]

            action = QAction(
                plugin.get_icon(self.toolbar.iconSize().height()),
                plugin.get_title(),
                parent=self,
            )
            action.setObjectName(f"action_{name}")
            if "--dev" in sys.argv:
                action.setEnabled(False)  # only view the loading speed  #TODO comment for production
            self.toolbar.addAction(action)
            if is_first:
                self.toolbar.addSeparator()
                sep = QWidget()
                sep.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
                sep.setMinimumWidth(100)
                self.toolbar.addWidget(sep)
                is_first = False

        QApplication.processEvents()
        self.plugins.load_plugins(want_one=self.want_one, parent=self)

    def plugin_loaded(self, widget: QWidget, name: str):
        # responses to self.plugins.load_plugins()
        plugin: PluginBase = self.plugins.modules[name]
        widget.setParent(self)
        if isinstance(self.tabs, QTabWidget):
            tab_id = self.tabs.addTab(
                widget,
                plugin.get_icon(self.tabs.iconSize().height()),
                "",
            )
        else:
            tab_id = self.tabs.addWidget(widget)
        if action := self.findChild(QAction, f"action_{name}"):
            action.triggered.connect(partial(self.change_module, tab_id, plugin.get_title()))
            action.setShortcut(QKeySequence().fromString(f"CTRL+{tab_id + 1}"))
            action.setEnabled(True)
        QApplication.processEvents()

    def plugins_loaded(self):
        """all plugins loaded"""
        self.toolbar.setVisible(self.tabs.count() > 1)

    def module_changed(self, tab_id: int):
        self.setWindowTitle(self.tabs.currentWidget().windowTitle())

    def change_module(self, tab_id: int, title: str):
        """display one plugin afer selected"""
        self.tabs.setCurrentIndex(tab_id)

    def window_title_changed(self, title):
        self.setWindowTitle(title)

    def receive_command(self, data: str):
        PREFIX = "OPEN: "
        if data.startswith(PREFIX):
            print("  CMD from other instance application :", data)
            plugin_name = data.removeprefix(PREFIX)
            """ # not usefull, search action is enough here
            plugin: PluginBase = self.plugins.modules.get(plugin_name, None)
            if not plugin:
                return
            """
            if action := self.findChild(QAction, f"action_{plugin_name}"):
                action.activate(action.ActionEvent.Trigger)
                QApplication.topLevelWindows()[0].requestActivate()

            # self.truc.setEditText(data[5:])
        else:
            print(f"  # ? receive CMD {data} ?")


class QOneApplication(QApplication):
    message = Signal(str)

    def __init__(self, args, idApp="PPJ25", name=""):
        super().__init__(args)
        if name:
            self.setApplicationName(name)
        idApp = f"{self.applicationName().replace(' ', '_')}-{idApp}"

        self._socket = QLocalSocket()
        self._socket.connectToServer(idApp)
        self.isActive = self._socket.waitForConnected(1000)
        if not self.isActive:
            self._server = QLocalServer()
            self._server.listen(idApp)
            self._server.newConnection.connect(self._onNewConnection)

    def sendMessage(self, msg):
        if not self.isActive:
            return 0
        self._socket.write(str.encode(msg + "\n"))
        return self._socket.waitForBytesWritten()

    def _onNewConnection(self):
        self._socket = self._server.nextPendingConnection()
        if self._socket:
            self._socket.readyRead.connect(self._onReadLine)

    def _onReadLine(self):
        in_stream = QTextStream(self._socket)
        while not in_stream.atEnd():
            if msg := in_stream.readLine():
                self.message.emit(msg)


def usage(plugins: PluginManager, want_one: str):
    print()
    print(
        QApplication.translate("help", "Available plugins") + ": ",
        ", ".join(f"--{p.lower()}" for p in plugins.modules.keys()),
    )
    print()
    print("--dev : not run pacman command + create fake EOL")
    exit(0)


def main():
    # best lang = QLocale.system().bcp47Name()
    lang = QLocale.languageToCode(QLocale.system().language())

    app = QOneApplication(sys.argv, idApp="MANJA-007", name="msm")

    trans = QTranslator()
    if len(lang) > 1:
        if trans.load(f"qt_{lang}", QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)):
            app.installTranslator(trans)  # dialog btns translate

        dir_ = Path(__file__).resolve().parent
        locale_dir = Path(f"/usr/share/locale/{lang}/LC_MESSAGES/")
        if not str(dir_).startswith("/usr/"):
            locale_dir = dir_ / f"../i18n/{lang}/LC_MESSAGES/"

        locale_directory = locale_dir.resolve()
        print("localisations is in ", locale_directory)

        locale_dir = locale_directory.resolve() / f"msm_{lang}.qm"
        trans = QTranslator()

        if trans.load(str(locale_dir)):
            if not app.installTranslator(trans):
                print(f"Warning: {locale_dir} not installed !")
            else:
                print(f"{locale_dir} installed")
        else:
            print(f"Warning: {locale_dir} not loaded !")

    want_one = ""
    exclude = ("--dev", "--help")
    if args := [a.removeprefix("--").lower() for a in sys.argv if a.startswith("--") and a not in exclude]:
        want_one = args[0]
        tr = QApplication.translate("help", "Load one plugin")
        print(f"# {tr} :", want_one)

    plugins = PluginManager()
    plugins.scan("modules")

    if "-h" in sys.argv or "--help" in sys.argv:
        usage(plugins, want_one)
        exit(0)

    if app.isActive:
        print("already launched", file=sys.stderr)
        if want_one:
            app.sendMessage(f"OPEN: {want_one}")
        exit(app.quit())

    window = MainWindow(plugins, want_one)
    app.message.connect(window.receive_command)
    window.show()
    window.load_plugins()
    app.exec()


if __name__ == "__main__":
    main()
