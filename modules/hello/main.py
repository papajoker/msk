#!/usr/bin/env python

from ui.hello import HelloMain

from PySide6.QtWidgets import QApplication


def main():
    app = QApplication([])
    win = HelloMain(None)
    win.show()
    app.exec()


if __name__ == "__main__":
    main()
