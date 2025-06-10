from pathlib import Path
import re
import sys
from PySide6.QtCore import Qt, QProcess, QSize
from PySide6.QtGui import QIcon, QFontDatabase, QAction, QKeySequence
from PySide6.QtWidgets import (
    QListView,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QStyle,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from controler.pacman import PacmanWorker
from controler.eol import EolWorker, EolManager
from model.kernel import Kernel, Kernels, IconMaker
from model.store import KernelModel, KernelModelFilter, DifferenceKernelModel
from ui.widgets import ListView, CustomToolBar

LOCAL_FILE = Path(__file__).parent / "kernels.csv"


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        line_height, _ = IconMaker.get_heights()

        self.initial_state = []
        self.model = None
        self.kernels = None
        self.choice = None
        self.model_diff = None
        self._eol_worker = None

        self.kernels = self.reload()
        self.model = KernelModel(self, self.kernels)
        self.model_diff = DifferenceKernelModel(self, self.kernels)
        # self.manager = KernelManager(self.kernels)
        self._running = False
        self.tabs = QTabWidget(tabPosition=QTabWidget.TabPosition.East, tabsClosable=False)

        self.setWindowTitle("Manjaro System Kernels")
        self.setMinimumSize(400, 335)
        self.resize(780, 550)
        icon = QIcon.fromTheme(QIcon.ThemeIcon.SoftwareUpdateAvailable)
        self.setWindowIcon(icon)

        self.choice = self._init_choices(line_height)

        self.btn = QPushButton(icon, "run transaction")
        self.btn.setEnabled(False)
        self.btn.setToolTip("pacman command")
        self.btn.clicked.connect(self.run_command)

        layout = QVBoxLayout()
        layout.addWidget(self.choice)
        layout.addWidget(self.btn)

        # layout.addWidget(self._diff_list_view)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.show()

        self.pacman = PacmanWorker()
        self.pacman.started.connect(self.handle_started)
        self.pacman.finished.connect(self.handle_finished)
        self.pacman.lineStdErr.connect(self.handle_stderr)
        self.pacman.lineStdOut.connect(self.handle_stdout)
        self.pacman.error.connect(self.handle_error)

        self._diff_list_view = self._init_diff()
        self._init_terminal()
        self._init_bar(line_height)

        self.model.layoutChanged.connect(self._update_difference_list)
        self.model.modelReset.connect(self._update_difference_list)
        self.model.dataChanged.connect(self._update_difference_list)
        self._update_difference_list()

        action = QAction(
            self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload),
            "&Reload",
            self,
        )
        action.setShortcut(QKeySequence.StandardKey.Refresh)  # F5
        action.triggered.connect(self.reload)
        self.addAction(action)

    def _update_difference_list(self):
        self.model_diff.layoutChanged.emit()
        before, after = self.model_diff.counts()
        title = "" if before == after else f" -> {after}"
        self.setWindowTitle(f"Manjaro System Kernels    {before}{title}")

        adds, rms = self.model_diff.todo()
        empty = not adds and not rms
        self.btn.setEnabled(not empty)
        self.tabs.setCurrentWidget(self._diff_list_view)
        if empty:
            return

        print("todo: +", adds, "-", rms)

    def reload(self) -> Kernels:
        worker = EolWorker()
        # worker.finished.connect(worker.deleteLater)
        worker.eol.connect(self.set_eol)
        worker.start()
        kernels = Kernels()
        kernels.load_config(LOCAL_FILE)

        self.kernels = kernels
        if self.model:
            self.model.setKernels(self.kernels)
        if self.model_diff:
            self.model_diff.setKernels(self.kernels)
            self._update_difference_list()
        return kernels

    def set_eol(self, kernels: list[str]):
        print(" -- set eol kernels:", kernels)
        for name in kernels:
            if kernel := self.kernels(name):
                kernel.isEOL = True
                kernel.setIcon()

    def _init_bar(self, line_height: int):
        toolbar = CustomToolBar("available kernels")

        list_view = ListView()
        list_view.setIconSize(QSize(line_height * 3, line_height * 3))

        _available_proxy_model = KernelModelFilter(self, Kernel.Selection.OUT)
        _available_proxy_model.setSourceModel(self.model)
        list_view.setModel(_available_proxy_model)
        list_view.move.connect(_available_proxy_model.handle_move)

        toolbar.addWidget(list_view)
        self.addToolBar(Qt.ToolBarArea.RightToolBarArea, toolbar)

    def _init_terminal(self):
        toolbar = CustomToolBar("terminal / transaction")

        self.terminal = QTextEdit(self)
        self.terminal.setVisible(True)
        self.terminal.setReadOnly(True)
        self.terminal.setProperty("textInteractionFlags", 1)
        self.terminal.ensureCursorVisible()
        self.terminal.setCurrentFont(QFontDatabase.systemFont(QFontDatabase.FixedFont))
        self.terminal.setStyleSheet("QTextEdit { background-color:#222; color: #ccc; }")
        self.terminal.setMinimumSize(750, 150)

        self.tabs.setMovable(True)
        self.tabs.addTab(self.terminal, "Terminal")
        if self._diff_list_view:
            self._diff_list_view.setStyleSheet("""QListView { background-color: transparent; }""")
            self.tabs.addTab(self._diff_list_view, QIcon.fromTheme(QIcon.ThemeIcon.DocumentProperties), "Action")
            self.tabs.setCurrentWidget(self._diff_list_view)

        toolbar.addWidget(self.tabs)
        self.addToolBar(Qt.ToolBarArea.BottomToolBarArea, toolbar)

    def _init_choices(self, line_height: int):
        """display installed kernels"""
        list_view = ListView()
        list_view.setIconSize(QSize(line_height * 5, line_height * 5))
        _installed_proxy_model = KernelModelFilter(self, Kernel.Selection.IN)
        _installed_proxy_model.setSourceModel(self.model)
        list_view.setModel(_installed_proxy_model)
        list_view.move.connect(_installed_proxy_model.handle_move)

        return list_view

    def _init_diff(self):
        """display transaction"""
        list_view = QListView()
        list_view.setViewMode(list_view.ViewMode.IconMode)
        list_view.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        list_view.setSelectionMode(QListView.SelectionMode.NoSelection)
        list_view.setAcceptDrops(False)
        list_view.setModel(self.model_diff)
        return list_view

    @property
    def running(self) -> bool:
        return self._running

    @running.setter
    def running(self, state: bool):
        self._running = state
        self.terminal.setVisible(self._running)
        self.btn.setEnabled(not self._running)
        self.tabs.setCurrentWidget(self.terminal)

    def run_command(self):
        adds, rms = self.model_diff.todo()
        if not adds and not rms:
            return
        if len(rms) >= len(self.kernels.get_installeds()):
            raise Exception("WE DELETE ALL !")

        command = "pacman -Sy; "
        if "--dev" in sys.argv:
            command += " exit 0;"
        if adds:
            command = f"{command} pacman -S {' '.join(adds)} --noconfirm --noprogressbar;"
        if rms:
            command = f"{command} pacman -Rsn {' '.join(rms)} --noconfirm --noprogressbar"
        if len(command) < 10:
            return
        self.terminal.clear()
        self.terminal.append(f"# {command}\n")
        print(f"# {command}")
        self.pacman.start_command(command)

    def handle_started(self):
        self.setCursor(Qt.WaitCursor)
        self.running = True
        print(":: pacman started ...")

    @staticmethod
    def escape_ansi(line):
        ansi_escape = re.compile(r"(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]")
        return ansi_escape.sub("", line)

    def handle_stdout(self, line):
        self.terminal.append(f"{self.escape_ansi(line)}")

    def handle_stderr(self, line):
        print(":: error:", line)
        self.terminal.append(f'\'<span style="color:red;">{self.escape_ansi(line)}</span>')
        self.terminal.setVisible(True)

    def handle_error(self, err):
        # bad command
        print(":: ERROR:", err)
        self.terminal.append(f'\'<span style="color:red;">{self.escape_ansi(err)}</span>')

    def handle_finished(self, exit_code, exit_status):
        self.running = False
        print(":: END", exit_code, exit_status)
        if exit_code:
            print("! One error ", exit_code)
        self.reload()
        self.setCursor(Qt.ArrowCursor)

    def closeEvent(self, event):
        if self.pacman.process.state() == QProcess.ProcessState.NotRunning:
            event.accept()
            EolManager.DB_FILE.unlink(True)
        else:
            event.ignore()
