#!/usr/bin/env python

from ui.main import Window

from PySide6.QtWidgets import QApplication


def main():
    print("Hello from msk!")
    app = QApplication([])
    win = Window()
    win.show()
    app.exec()


if __name__ == "__main__":
    main()
