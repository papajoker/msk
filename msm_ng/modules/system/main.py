#!/usr/bin/env python
import json
import subprocess
import logging
from pathlib import Path
from PySide6.QtWidgets import QApplication, QHBoxLayout, QTextEdit, QWidget

logger = logging.getLogger("plugin.system")
logging.basicConfig(filename=str(Path(__file__).parent / "msm.log"), level=logging.DEBUG)

class SystemWidget(QWidget):
    def __init__(self, parent: QWidget | None):
        super().__init__(parent=parent)
        self.setWindowTitle("System Info")
        self.mlayout = QHBoxLayout()
        self.setLayout(self.mlayout)

        self._set()

    def _set(self) -> None:
        """inxi infos"""
        try:
            logger.info("run inxi...")
            result = subprocess.run(
                "/usr/bin/inxi -Fx --output json --output-file print",
                capture_output=True,
                text=True,
                shell=True,
                check=True,
            )
            #BUG if loaded in gui : crash
            logger.info("end inxi")
            data = result.stdout
        except subprocess.CalledProcessError as e:
            data = f"Error running inxi: {e}"

        # print(data)
        data_json = json.loads(data)
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

        # label = QLabel(txt, parent=self, margin=20)
        edit = QTextEdit(readOnly=True)
        edit.setHtml(txt.replace(" ", "&nbsp;"))
        # edit.setCurrentFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
        self.mlayout.addWidget(edit)


def main():
    app = QApplication([])
    win = SystemWidget(None)
    win.show()
    app.exec()


if __name__ == "__main__":
    main()