#!/usr/bin/env python

from ui.test import UserMain

from PySide6.QtWidgets import QApplication


def main():
    app = QApplication([])
    win = UserMain(None)
    win.show()
    app.exec()


if __name__ == "__main__":
    main()
