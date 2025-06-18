import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from .._plugin.base import PluginBase

sys.path.pop(0)
from PySide6.QtWidgets import QHBoxLayout, QTextEdit, QWidget


class SystemWidget(QWidget):
    def __init__(self, parent: QWidget | None):
        super().__init__(parent=parent)
        self.setWindowTitle(Plugin.get_title())
        self.mlayout = QHBoxLayout()
        self.setLayout(self.mlayout)

        self._set()

    def _set(self) -> None:
        """inxi infos"""
        try:
            result = subprocess.run(
                "/usr/bin/inxi -Fx --output json --output-file print",
                capture_output=True,
                text=True,
                shell=True,
                check=True,
            )
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


class Plugin(PluginBase):
    NAME = "System Info"
    ORDER = 30  # 10 by 10, order in main app
    # COLOR = "#440066"

    @staticmethod
    def i_enable() -> bool:
        # if kde : return False
        # or if wayland : return False
        return True

    @staticmethod
    def get_class():
        # return class and not instance
        return SystemWidget
