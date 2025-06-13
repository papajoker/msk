from PySide6.QtWidgets import QWidget, QLabel


def test():
    return True


class UserMain(QWidget):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setWindowTitle("Manage users")

        self.setStyleSheet("background-color: #909;")
        QLabel("Super User", parent=self, margin=20)