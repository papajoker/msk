#!/usr/bin/env python
import json
import sys
import subprocess
from pathlib import Path
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QApplication, QHBoxLayout, QTextEdit, QWidget


class InxiWorker(QThread):
    eol = Signal(str)

    def run(self):
        """inxi infos"""
        try:
            result = subprocess.run(
                "/usr/bin/inxi -Fx --tty --output json --output-file print",
                capture_output=True,
                #stdout=f_obj,
                text=True,
                shell=True,
                check=True,
            )
            data = result.stdout
        except subprocess.CalledProcessError as err:
            print(f"Error inxi call : {err}", file=sys.stderr)
        except Exception as err:
            print(f"Error running inxi : {err}", file=sys.stderr)
        if data:
            self.eol.emit(data)

class SystemWidget(QWidget):
    def __init__(self, parent: QWidget | None):
        super().__init__(parent=parent)
        self.setMinimumWidth(400)
        self.setMinimumHeight(600)
        self.setWindowTitle("System Info")
        self.mlayout = QHBoxLayout()
        self.setLayout(self.mlayout)

        self.inxi = InxiWorker()
        self.inxi.eol.connect(self._set)
        self.inxi.start()

    def _set(self, datas):
        """display inxi infos"""

        # print(data)
        data_json = json.loads(datas)
        txt = ""
        for rub in data_json:
            for key, value in rub.items():
                txt = f"{txt}<br><br> <b>{key.split('#')[-1].upper()}</b><br>"
                for srub in value:
                    for key, val in dict(sorted(srub.items())).items():
                        if val in ("N/A", "<superuser required>"):
                            continue
                        if val:
                            txt = f"{txt}         {key.split('#')[-1]} : {val}<br>"
                        else:
                            txt = f"{txt}     <b>{key.split('#')[-1]}</b> :<br>"

        edit = QTextEdit(readOnly=True)
        # edit.setCurrentFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
        edit.setHtml(txt.replace(" ", "&nbsp;"))
        self.mlayout.addWidget(edit)


def main():
    app = QApplication([])
    win = SystemWidget(None)
    win.show()
    app.exec()


if __name__ == "__main__":
    main()