from pathlib import Path

from PySide6.QtCore import Qt, QProcess
from PySide6.QtGui import QIcon, QFontDatabase
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from controler.pacman import PacmanWorker
from controler.manager import KernelManager
from model.kernel import Kernel, Kernels
from ui.widgets import KernelMainWidget, ToolBar

LOCAL_FILE = Path(__file__).parent / "kernels.csv"


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initial_state = []
        self.choice = None
        self.model = self.reload()
        self.manager = KernelManager(self.model)
        self._running = False
        self.toolbar_action = None

        self.setWindowTitle("Manjaro System Kernels")
        self.setMinimumSize(400, 335)
        self.resize(780, 550)
        icon = QIcon.fromTheme(QIcon.ThemeIcon.SoftwareUpdateAvailable)
        self.setWindowIcon(icon)

        self.choice = self._init_choices()

        self.btn = QPushButton(icon, "run transaction")
        self.btn.setToolTip("pacman command")
        self.btn.clicked.connect(self.run_command)

        layout = QVBoxLayout()
        layout.addWidget(self.choice)
        layout.addWidget(self.btn)

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

        self._init_terminal()
        self._init_bar()

    def reload(self) -> Kernels:
        model = Kernels()
        model.load_config(LOCAL_FILE)
        self.initial_state = [k.name for k in model if k.isInstalled]
        if self.choice:
            for child in self.choice.children():
                if not isinstance(child, KernelMainWidget):
                    continue
                kernel = model[child.kernel.name]
                child.update(kernel)
                child.setVisible(kernel.isInstalled)
            installeds = sorted(self.initial_state)
            states = sorted(list(self._get_choices()))
            self.setWindowTitle(f"Manjaro System Kernels  {len(installeds)} -> {len(states)}")
            print("verif:", self.get_commands())
        # TODO update left kernels (if error)
        return model

    def _init_bar(self):
        self.toolbar = ToolBar("available kernels")

        for kernel in self.model:
            kw = self.toolbar.addActionKernel(kernel)
            kw.install.connect(self.on_add_kernel)

        self.addToolBar(Qt.ToolBarArea.RightToolBarArea, self.toolbar)

    def _init_terminal(self):
        toolbar = QToolBar("terminal")
        toolbar.setMovable(False)
        # toolbar.setFloatable(False)
        self.terminal = QTextEdit(self)
        self.terminal.setVisible(True)
        self.terminal.setReadOnly(True)
        self.terminal.setProperty("textInteractionFlags", 1)
        self.terminal.ensureCursorVisible()
        self.terminal.setCurrentFont(QFontDatabase.systemFont(QFontDatabase.FixedFont))
        self.terminal.setStyleSheet("QTextEdit { background-color:#222; color: #ccc; }")
        self.terminal.setMinimumSize(750, 150)
        self.toolbar_action = toolbar.addWidget(self.terminal)

        self.update_terminal()

        self.addToolBar(Qt.ToolBarArea.BottomToolBarArea, toolbar)

    def _init_choices(self):
        """display installed kernels"""
        choice = QWidget()

        layoutv = QVBoxLayout()
        layout = QHBoxLayout()
        old = True
        for k in self.model:
            if k.isRT and old:
                old = False
                layoutv.addLayout(layout)
                layout = QHBoxLayout()
            w = KernelMainWidget(k, parent=self)
            w.uninstall.connect(self.on_remove_kernel)
            layout.addWidget(w, stretch=0)
            w.setVisible(k.isInstalled)
        layoutv.addLayout(layout)
        choice.setLayout(layoutv)
        return choice

    def on_add_kernel(self, kernel: Kernel):
        if w := self.choice.findChild(KernelMainWidget, kernel.name):
            print("add:", kernel)
            w.setVisible(True)
        self.update_terminal()

    def on_remove_kernel(self, kernel: Kernel):
        if len(list(self._get_choices())) < 2:
            # always one kernel installed
            return
        if w := self.toolbar.get_widget(kernel.name):
            w.action.setVisible(True)
        if w := self.choice.findChild(KernelMainWidget, kernel.name):
            print("remove", kernel, w)
            w.setVisible(False)
        self.update_terminal()

    def get_commands(self) -> list:
        new = list(self._get_choices())
        cmds = {"ADD": [], "RM": []}
        cmds["ADD"] = [k for k in new if k not in self.initial_state]
        cmds["RM"] = [k for k in self.initial_state if k not in new]
        return cmds

    def update_terminal(self, use_term=True):
        installeds = sorted(self.initial_state)
        states = sorted(list(self._get_choices()))
        installed = ", ".join(installeds)
        state = ", ".join(states)
        if use_term:
            self.terminal.clear()
            self.terminal.insertPlainText(f"{'installed :':12} {installed}")
            if installed != state:
                self.terminal.append(f"{'want :':12} {state}")
                if not self._running:
                    self.btn.setEnabled(True)
                self.terminal.append("")
                commands = self.get_commands()
                self.terminal.append("TODO:")
                if commands["ADD"]:
                    self.terminal.append(f"  pacman -S {' '.join(commands['ADD'])}")
                if commands["RM"]:
                    self.terminal.append(f"  pacman -Rsn {' '.join(commands['RM'])}")

        if installed == state:
            self.btn.setEnabled(False)
        self.setWindowTitle(f"Manjaro System Kernels  {len(installeds)} -> {len(states)}")

    def _get_choices(self):
        """to rewrite"""
        for child in self.choice.children():
            if isinstance(child, KernelMainWidget):
                if child.isVisible():
                    yield child.kernel.name

    @property
    def running(self) -> bool:
        return self._running

    @running.setter
    def running(self, state: bool):
        self._running = state
        self.terminal.setVisible(self._running)
        self.btn.setEnabled(not self._running)

    def run_command(self):
        commands = self.get_commands()
        if len(commands["RM"]) >= len(self.model.get_installeds()):
            raise Exception("WE DELETE ALL !")
            return
        command = "pacman -Sy;"
        if commands["ADD"]:
            command = f"{command} pacman -S {' '.join(commands['ADD'])} --noconfirm;"
        if commands["RM"]:
            command = f"{command} pacman -Rsn {' '.join(commands['RM'])} --noconfirm"
        if len(command) < 16:
            return
        self.terminal.clear()
        self.terminal.append(f"# {command}\n")
        print(f"# {command}")
        self.pacman.start_command(command)

    def handle_started(self):
        self.setCursor(Qt.WaitCursor)
        self.running = True
        print(":: pacman started ...")

    def handle_stdout(self, line):
        # TODO clear color codes
        self.terminal.append(f"{line}")

    def handle_stderr(self, line):
        print(":: error:", line)
        self.terminal.insertPlainText(f"!!! {line}\n")
        self.terminal.setVisible(True)

    def handle_error(self, err):
        # bad command
        print(":: ERROR:", err)

    def handle_finished(self, exit_code, exit_status):
        self.running = False
        print(":: END", exit_code, exit_status)
        if exit_code:
            print("! One error ", exit_code)
        self.reload()
        self.update_terminal(False)  # not clear terminal
        self.setCursor(Qt.ArrowCursor)

    def closeEvent(self, event):
        if self.pacman.process.state() == QProcess.ProcessState.NotRunning:
            event.accept()
        else:
            event.ignore()
