import webbrowser
from PySide6.QtCore import Qt, QObject, Signal
from PySide6.QtGui import QIcon, QFont, QDragEnterEvent
from PySide6.QtWidgets import QListView, QMenu, QSizePolicy, QToolBar
from model.kernel import Kernel


class ListView(QListView):
    move = Signal(QListView, QObject, Kernel)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setViewMode(self.ViewMode.IconMode)
        self.setUniformItemSizes(True)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(False)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setDragDropMode(self.DragDropMode.DragDrop)
        self.setSelectionMode(self.SelectionMode.SingleSelection)
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_kernel_context_menu)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.source() == self:
            return
        if event.mimeData().hasFormat("application/x-kernel"):
            event.accept()
            super().dragEnterEvent(event)

    def _show_kernel_context_menu(self, pos):
        sender_view: QListView = self.sender()
        index = sender_view.indexAt(pos)
        if not index.isValid():
            return

        source_index = sender_view.model().mapToSource(index)
        if not source_index.isValid():
            return
        kernel: Kernel = source_index.data(Qt.ItemDataRole.UserRole)
        if not kernel:
            return

        menu = QMenu(self)
        if kernel.isEOL:
            # or ? self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning)
            action = menu.addAction(QIcon.fromTheme(QIcon.ThemeIcon.SecurityLow), "End of Life", None)
            action.triggered.connect(lambda: self.show_kernel_life(kernel))
            f = action.font()
            f.setLetterSpacing(QFont.SpacingType.PercentageSpacing, 150)
            f.setWeight(QFont.Weight.ExtraBold)
            x = f.pointSize()
            f.setPointSize(x * 1.3)
            action.setFont(f)
            menu.addSeparator()
        if kernel.selection == Kernel.Selection.IN:
            if not kernel.isActive:
                menu.addAction(
                    QIcon.fromTheme(QIcon.ThemeIcon.ListRemove),
                    f"Uninstall  {kernel.name} package",
                    lambda: self._on_uninstall(source_index, kernel),
                )
        else:
            if kernel.isEOL and not kernel._initial_selection:
                pass
            else:
                menu.addAction(
                    QIcon.fromTheme(QIcon.ThemeIcon.ListAdd),
                    f"Install  {kernel.name} package",
                    lambda: self._on_install(source_index, kernel),
                )

        action = menu.addAction(
            QIcon.fromTheme(QIcon.ThemeIcon.DialogInformation),
            f"{kernel.get_ver()} kernel changelog",
        )
        action.triggered.connect(lambda: self.show_kernel_info(kernel))

        menu.exec(sender_view.mapToGlobal(pos))

    def show_kernel_info(self, kernel: Kernel):
        url = kernel.get_changelog_url()
        webbrowser.open(url, new=2)

    def show_kernel_life(self, kernel: Kernel):
        url = f"https://en.wikipedia.org/wiki/Linux_kernel_version_history#Releases_{kernel.major}.x.y"
        webbrowser.open(url, new=2)

    def _on_install(self, index, kernel: Kernel):
        self.move.emit(self, index, kernel)

    def _on_uninstall(self, index, kernel: Kernel):
        self.move.emit(self, index, kernel)


class CustomToolBar(QToolBar):
    def __init__(self, title="ToolBar"):
        super().__init__(title)
        self.setMovable(False)
        self.setFloatable(False)
        self.setContextMenuPolicy(Qt.PreventContextMenu)