from PySide6.QtCore import (
    Qt,
    QObject,
    QAbstractItemModel,
    QAbstractTableModel,
    QAbstractProxyModel,
    QSortFilterProxyModel,
    QMimeData,
    QModelIndex,
)
from PySide6.QtWidgets import QStyle
from model.kernel import Kernel, Kernels


class KernelModel(QAbstractTableModel):
    def __init__(self, parent: QObject, kernels: Kernels):
        super().__init__(parent=parent)
        self._data: Kernels = Kernels()
        if kernels:
            self.setKernels(kernels)
        self.ICO_TRUE = parent.style().standardIcon(QStyle.StandardPixmap.SP_DialogOkButton)
        self.ICO_FALSE = parent.style().standardIcon(QStyle.StandardPixmap.SP_DialogNoButton)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._data)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return 1
        return len(Kernel.__annotations__.keys())

    def headerData(self, section: int, orientation: Qt.Orientation, role: int):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return list(Kernel.__annotations__)[section].capitalize()
        if orientation == Qt.Orientation.Vertical:
            return f"{section + 1}"

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return False

        row = index.row()
        col = index.column()
        if not (0 <= row < len(self._data)):
            return None
        kernel = self._data[row]

        if role == Qt.ItemDataRole.DisplayRole:
            return
            result = getattr(kernel, list(Kernel.__annotations__)[col])
            if isinstance(result, bool):
                return self.ICO_TRUE if result else self.ICO_FALSE
            return result
        if role == Qt.ItemDataRole.DecorationRole:
            result = getattr(kernel, list(Kernel.__annotations__)[col])
            if isinstance(result, bool):
                return self.ICO_TRUE if result else self.ICO_FALSE
            return kernel.icon
        if role == Qt.ItemDataRole.UserRole:
            return kernel
        if role == Qt.ItemDataRole.ToolTipRole:
            return (
                f"{kernel.name}\n"
                f"{kernel.version}\n"
                f"{'Real Time' if kernel.isRT else ''}\n"
                "\n"
                f"{'Recommended\n' if kernel.isRecommanded else ''}"
                f"{'Installed\n' if kernel.isInstalled else ''}"
                f"{'Current\n' if kernel.isActive else ''}"
                # f"{kernel.selection.name.lower()}\n"
            )

    def flags(self, index) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.ItemIsDropEnabled | Qt.ItemFlag.ItemIsEnabled
        kernel = self._data[index.row()]
        item_flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsDropEnabled

        if not kernel.isActive:
            item_flags |= Qt.ItemFlag.ItemIsDragEnabled

        return item_flags

    def kernels(self) -> Kernels:
        return self._data

    def setKernels(self, kernels: Kernels):
        self.beginResetModel()
        self._data = kernels
        self.endResetModel()

    def supportedDropActions(self) -> Qt.DropAction:
        return Qt.DropAction.MoveAction

    def mimeTypes(self) -> list[str]:
        return ["application/x-kernel"]

    def mimeData(self, indexes: list[QModelIndex]) -> QMimeData:
        mime_data = QMimeData()
        if indexes:
            kernel = self._data[indexes[0].row()]
            if kernel.isActive:
                return QMimeData()

            data = kernel.name.encode("utf-8")
            mime_data.setData("application/x-kernel", data)
        return mime_data


class KernelModelFilter(QSortFilterProxyModel):
    def __init__(self, parent: QObject, target_selection: Kernel.Selection):
        super().__init__(parent=parent)
        self._target_selection = target_selection
        self.setFilterRole(Qt.ItemDataRole.UserRole + 1)

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        index = self.sourceModel().index(source_row, 0, source_parent)
        if not index.isValid():
            return False

        kernel: Kernel = self.sourceModel()._data[index.row()]
        return kernel.selection == self._target_selection

    def canDropMimeData(self, data: QMimeData, action: Qt.DropAction, row: int, column: int, parent: QModelIndex) -> bool:
        return data.hasFormat("application/x-kernel")

    def dropMimeData(self, data: QMimeData, action: Qt.DropAction, row: int, column: int, parent: QModelIndex) -> bool:
        if action == Qt.DropAction.IgnoreAction:
            return True
        if not data.hasFormat("application/x-kernel"):
            return False

        k_name = data.data("application/x-kernel").data().decode("utf-8")

        source_model = self.sourceModel()
        if original_kernel := source_model._data(k_name):
            source_model_row = source_model._data.index(original_kernel)
            source_model_index = source_model.index(source_model_row, 0)

            original_kernel.selection = self._target_selection
            source_model.dataChanged.emit(
                source_model_index,
                source_model_index,
                [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.ToolTipRole, Qt.ItemDataRole.UserRole + 1],
            )
            return True
        return False

    def handle_move(self, source, index: QModelIndex, kernel: Kernel):
        source_model = self.sourceModel()
        kernel.selection = Kernel.Selection.OUT if kernel.selection == Kernel.Selection.IN else Kernel.Selection.IN
        source_model.dataChanged.emit(
            index,
            index,
            [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.ToolTipRole, Qt.ItemDataRole.UserRole + 1],
        )


class DifferenceKernelModel(QAbstractTableModel):
    def __init__(self, parent: QObject, all_kernels: Kernels):
        super().__init__(parent=parent)
        self.kernels = all_kernels

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len([k for k in self.kernels if k.has_changed])

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return 1

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        changed_kernels = [k for k in self.kernels if k.has_changed]
        if not changed_kernels:
            return None

        kernel = changed_kernels[index.row()]

        if role == Qt.ItemDataRole.DisplayRole:
            if kernel.selection == Kernel.Selection.IN and not kernel.isInstalled:
                return f"+ {kernel.major}.{kernel.minor}{'-rt' if kernel.isRT else ''}"
            elif kernel.selection == Kernel.Selection.OUT and kernel.isInstalled:
                return f"- {kernel.major}.{kernel.minor}{'-rt' if kernel.isRT else ''}"
            return None
        elif role == Qt.ItemDataRole.DecorationRole:
            if (kernel.selection == Kernel.Selection.IN and not kernel.isInstalled) or (
                kernel.selection == Kernel.Selection.OUT and kernel.isInstalled
            ):
                return kernel.icon
        return None

    def todo(self) -> tuple[list, list]:
        """as data() return to install et to uninstall"""
        add = []
        remove = []
        for kernel in self.kernels:
            if kernel.selection == Kernel.Selection.IN and not kernel.isInstalled:
                add.append(kernel.name)
            elif kernel.selection == Kernel.Selection.OUT and kernel.isInstalled:
                remove.append(kernel.name)
        return add, remove

    @staticmethod
    def toto_is_empty(todos: tuple[list, list]) -> bool:
        return not todos[0] and not todos[1]

    def counts(self) -> tuple[int, int]:
        return (
            len([True for k in self.kernels if k.isInstalled]),
            len([True for k in self.kernels if k.selection == Kernel.Selection.IN]),
        )

    def setKernels(self, kernels: Kernels):
        self.beginResetModel()
        self.kernels = kernels
        self.endResetModel()
