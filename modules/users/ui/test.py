from PySide6.QtWidgets import QLabel, QWidget


class UserMain(QWidget):
    def __init__(self, parent: QWidget | None):
        super().__init__(parent=parent)
        self.setWindowTitle("Manage users")
        users = []
        with open("/etc/passwd") as f:
            for line in f:
                if "/home/" not in line:
                    continue
                parts = line.split(":", maxsplit=6)
                users.append(f"{parts[0]} ({parts[2]}) {parts[4]}")

        # self.setStyleSheet("background-color: #909;")
        QLabel("\n* " + "\n* ".join(users), parent=self, margin=20)
