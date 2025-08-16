import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from .._plugin.base import PluginBase

sys.path.insert(0, str(Path(__file__).parent))
from ui.hello import HelloMain

sys.path.pop(0)


class Plugin(PluginBase):
    NAME = QApplication.translate("entry", "Hello")
    ORDER = 0  # Always the first !
    COLOR = "#35bf5c"

    @classmethod
    def get_title(cls) -> str:
        return cls.NAME

    @staticmethod
    def get_class():
        # return class and not instance
        return HelloMain
