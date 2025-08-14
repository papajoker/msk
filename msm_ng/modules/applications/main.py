#!/usr/bin/env python

from ui.main import ApplicationsMain

from PySide6.QtWidgets import QApplication


def main():
    app = QApplication([])
    win = ApplicationsMain(None)
    win.show()
    app.exec()


if __name__ == "__main__":
    main()