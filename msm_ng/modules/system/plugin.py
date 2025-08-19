import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from .._plugin.base import PluginBase

sys.path.insert(0, str(Path(__file__).parent))
from main import SystemWidget

sys.path.pop(0)


class Plugin(PluginBase):
    NAME = QApplication.translate("entry", "System Info")
    ORDER = 30  # 10 by 10, order in main app
    # COLOR = "#440066"

    @staticmethod
    def is_enable() -> bool:
        #return False  # BUG in gui ?
        return True

    @staticmethod
    def get_class():
        # return class and not instance
        return SystemWidget
