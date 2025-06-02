import webbrowser
from PySide6.QtWidgets import (
    QWidget,
    QMenu,
    QPushButton,
    QToolBar,
    QBoxLayout,
)
from PySide6.QtCore import QSize, Signal
from model.kernel import Kernel


class KernelWidget(QPushButton):
    install = Signal(Kernel)

    def __init__(self, kernel: Kernel, parent=None):
        super().__init__(parent)
        self.setObjectName(kernel.name)
        self.kernel = kernel
        self.action = None
        color = "AAAAAA" if self.kernel.isRT else "32BF5C"
        self.setStyleSheet(f"""
            KernelWidget {{
            border-radius:4px; background-color:#{color}; 
            color:#fff;
            padding: 4px; margin: 5px; text-align:left;
            }}
        """)

        title = self.kernel.get_ver()
        if self.kernel.isRT:
            title = f"{title} RT"
        self.setText(title)
        self.setToolTip(f" {self.kernel.name} {'\t(Real Time)' if self.kernel.isRT else ''}")

        self.menu = QMenu(self)
        self.menu.addAction("Install " + self.kernel.name, self._on_install)
        self.menu.addAction("Infos " + self.kernel.name, self._on_info)
        self.setMenu(self.menu)

    def _on_install(self):
        self.install.emit(self.kernel)
        if self.action:
            self.action.setVisible(False)

    def _on_info(self):
        url = self.kernel.get_changelog_url()
        webbrowser.open_new(url)


class KernelMainWidget(KernelWidget):
    uninstall = Signal(Kernel)

    def __init__(self, kernel: Kernel, parent=None):
        super().__init__(kernel, parent)
        self.update()

    def update(self, kernel=None):
        if kernel:
            self.kernel = kernel
        color = "bbbbbb" if self.kernel.isRT else "32BF5C"
        if self.kernel.isInstalled:
            color = "16a085"
        if self.kernel.isActive:
            color = "aa4444"
        self.setStyleSheet(f"""
            KernelMainWidget {{
            border:1px solid #aaa; border-radius:5px; background-color:#{color}; 
            color:#eee;
            padding: 5px; margin: 5px; text-align:left;
            }}
        """)
        self.setMinimumSize(QSize(120, 70))

        self.menu.clear()
        if not self.kernel.isActive:
            self.menu.addAction("unInstall " + self.kernel.name, self._on_uninstall)
        self.menu.addAction("Infos " + self.kernel.name, self._on_info)

    def _on_uninstall(self):
        self.uninstall.emit(self.kernel)


class ToolBar(QToolBar):
    def __init__(self, title: str):
        super().__init__(title)
        self.setMovable(True)
        self.setFloatable(True)

        widget = QWidget()
        self.layout = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        widget.setLayout(self.layout)
        self.addWidget(widget)

    def addActionKernel(self, kernel) -> KernelWidget:
        kw = KernelWidget(kernel, parent=self)
        self.layout.addWidget(kw)
        kw.action = self.addWidget(kw)
        if kernel.isInstalled:
            kw.action.setVisible(False)
        return kw

    def get_widget(self, objectName: str):
        return self.findChild(KernelWidget, objectName)


"""
class KernelsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(200)
        self.layout = QGridLayout()
        self.layout.setColumnMinimumWidth(0, 210)
        self.setLayout(self.layout)

    def setModel(self, kernels: Kernels, install_callback=None):
        row, col = 0, 0
        for kernel in (k for k in kernels if k.isInstalled):
            item = KernelMainWidget(kernel)
            item.uninstall.connect(install_callback)
            self.layout.addWidget(item, row, col)
            col += 1
            if col > 2:
                row += 1
                col = 0

    def append(self, kernel, install_callback=None) -> KernelMainWidget:
        item = KernelMainWidget(kernel)
        item.uninstall.connect(install_callback)
        self.layout.addWidget(item)
        return item

    def get_kernels(self):
        for child in self.children():
            if isinstance(child, KernelWidget):
                yield child.kernel.name


class ListBoxWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIconSize(QSize(72, 72))
        self.setAcceptDrops(True)
        # self.setDragEnabled(True)
        # self.setDropIndicatorShown(True)
        self.resize(600, 600)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setViewMode(QListWidget.ViewMode.IconMode)

    def dragEnterEvent(self, event: QDragEnterEvent):
        print("enter", event.mimeData().formats())
        print("source:", event.source())
        if event.source() == self:
            return
        if event.mimeData().hasFormat("application/x-qabstractitemmodeldatalist"):
            event.accept()  # force oui
            super().dragEnterEvent(event)

    def dropEvent(self, event: QDropEvent):
        if event.source() == self:
            return
        print("drop", event.mimeData())
        mime_dict = {}
        for format in event.mimeData().formats():
            mime_dict[format] = event.mimeData().data(format)
        self.mime_dict = mime_dict
        print(event.mimeData().formats())

        if event.mimeData().hasFormat("application/x-qabstractitemmodeldatalist"):
            source_item = QStandardItemModel()
            data = event.mimeData()
            source_item.dropMimeData(data, Qt.CopyAction, 0, 0, QModelIndex())
            print(source_item.item(0, 0).text(), source_item)
            self.addItems(source_item.item(0, 0).text())
        else:
            super().dropEvent(event)

    def XdragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            super().dragMoveEvent(event)
"""