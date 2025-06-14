import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from ui.test import UserMain
from .._plugin.base import PluginBase

from PySide6.QtWidgets import QWidget, QLabel

sys.path.pop(0)


class SystemWidget(QWidget):
    pass


class Plugin(PluginBase):
    NAME = "System Info"
    ORDER = 30  # 10 by 10, order in main app
    # COLOR = "#440066"

    @staticmethod
    def isEnable() -> bool:
        # if kde : return False
        # or if wayland : return False
        return True

    @staticmethod
    def get_class():
        # return class and not instance
        return SystemWidget