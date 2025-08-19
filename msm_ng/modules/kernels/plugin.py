import platform
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from .._plugin.base import PluginBase

sys.path.insert(0, str(Path(__file__).parent))
from .ui.main import Window

sys.path.pop(0)

# from PySide6.QtGui import QIcon


class Plugin(PluginBase):
    NAME = QApplication.translate("entry", "Kernels")
    ORDER = 10  # 10 by 10, order in main app

    @classmethod
    def get_title(cls) -> str:
        return cls.NAME

    """
    def get_icon(self, size=48) -> QIcon:
        return QIcon.fromTheme(QIcon.ThemeIcon.Computer)
    """

    @staticmethod
    def is_enable() -> bool:
        if platform.machine() != "x86_64":
            print("Only for x86 cpu", file=sys.stderr)
            return False
        if platform.freedesktop_os_release()["ID"].lower() != "manjaro":
            print("Only for manjaro", file=sys.stderr)
            return False
        return True

    @staticmethod
    def get_class():
        # return class and not instance
        return Window
