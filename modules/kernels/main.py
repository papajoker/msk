#!/usr/bin/env python

from ui.window import MainWindow

from PySide6.QtWidgets import QApplication


def main():
    print("Hello from msk!")
    app = QApplication([])
    win = MainWindow()
    win.show()
    app.exec()


if __name__ == "__main__":
    main()
