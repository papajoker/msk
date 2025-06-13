import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from ui.main import Window
from .._plugin.base import PluginBase

sys.path.pop(0)

from PySide6.QtGui import QIcon


class Plugin(PluginBase):
    NAME = "Kernels"
    ORDER = 10  # 10 by 10, order in main app

    @classmethod
    def getTitle(cls) -> str:
        return cls.NAME

    @staticmethod
    def getIcon() -> QIcon:
        return QIcon.fromTheme(QIcon.ThemeIcon.Computer)

    @staticmethod
    def isEnable() -> bool:
        return True

    @staticmethod
    def get_class():
        # return class and not instance
        return Window