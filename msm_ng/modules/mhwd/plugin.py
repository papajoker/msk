import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from .._plugin.base import PluginBase

sys.path.insert(0, str(Path(__file__).parent))
from .main import MaterialWidget

sys.path.pop(0)


class Plugin(PluginBase):
    NAME = QApplication.translate("entry", "Material")
    ORDER = 80  # 10 by 10, order in main app

    @staticmethod
    def is_enable() -> bool:
        return Path("/usr/bin/mhwd").exists()

    @staticmethod
    def get_class():
        # return class and not instance
        return MaterialWidget
