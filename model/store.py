from PySide6.QtCore import (
    Qt,
    QObject,
    QAbstractItemModel,
    QAbstractTableModel,
    QAbstractProxyModel,
    QSortFilterProxyModel,
    QModelIndex,
)
from PySide6.QtWidgets import QStyle
from model.kernel import Kernel, Kernels


class KernelModel(QAbstractTableModel):
    def __init__(self, parent: QObject, kernels: Kernels):
        super().__init__(parent=parent)
        self.ICO_TRUE = parent.style().standardIcon(QStyle.StandardPixmap.SP_DialogOkButton)
        self.ICO_FALSE = parent.style().standardIcon(QStyle.StandardPixmap.SP_DialogNoButton)
        self._data: Kernels = Kernels()
        if kernels:
            self.setKernels(kernels)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(Kernel.__annotations__.keys())

    def headerData(self, section: int, orientation: Qt.Orientation, role: int):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return list(Kernel.__annotations__)[section].capitalize()
        if orientation == Qt.Orientation.Vertical:
            return f"{section + 1}"

    def data(self, index, role):
        if not index.isValid():
            return False

        row = index.row()
        col = index.column()
        if not (0 <= row < len(self._data)):
            return None
        data = self._data[row]

        if role == Qt.ItemDataRole.DisplayRole:
            result = getattr(data, list(Kernel.__annotations__)[col])
            if isinstance(result, bool):
                return self.ICO_TRUE if result else self.ICO_FALSE
            return result
        if role == Qt.ItemDataRole.DecorationRole and col > 1:
            result = getattr(data, list(Kernel.__annotations__)[col])
            if isinstance(result, bool):
                return self.ICO_TRUE if result else self.ICO_FALSE
        if role == Qt.ItemDataRole.UserRole:
            return data

    def flags(self, index):
        flags = super().flags(index)
        if index.isValid():
            flags |= Qt.ItemFlags.ItemIsDragEnabled
            # flags |= Qt.ItemFlags.ItemIsDropEnabled
        return flags

    def kernels(self) -> Kernels:
        return self._data

    def setKernels(self, ks: Kernels):
        self.beginResetModel()
        self._data = ks  # .copy() ?
        self.endResetModel()


class InstallKernelModel(KernelModel):
    def setKernels(self, ks: Kernels):
        self._data.clear()
        self.beginResetModel()
        # self._data = ks  # .copy() ?
        for k in (k for k in ks if k.isInstalled):
            self._data.append(k)  # .copy() ?
        self.endResetModel()


class KernelModelFilter(QSortFilterProxyModel):
    def __init__(self, parent=None, ok=True, sourceModel=None):
        super().__init__(parent)
        self.want = ok
        if sourceModel:
            self.setSourceModel(sourceModel)

    def filterAcceptsRow(self, sourceRow, sourceParent):
        model = self.sourceModel()
        if data := model.data(model.index(sourceRow, 4, sourceParent), Qt.ItemDataRole.UserRole):
            return data.isInstalled is self.want
        return False