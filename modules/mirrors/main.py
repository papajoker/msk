#!/usr/bin/env python

from plugin import MirrorsWidget

from PySide6.QtWidgets import QApplication


def main():
    app = QApplication([])
    win = MirrorsWidget(None)
    win.show()
    app.exec()


if __name__ == "__main__":
    main()
