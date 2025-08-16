import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from .._plugin.base import PluginBase

sys.path.insert(0, str(Path(__file__).parent))
from .ui import MirrorsWidget

sys.path.pop(0)


class Plugin(PluginBase):
    NAME = QApplication.translate("entry", "Mirrors")
    ORDER = 100  # 10 by 10, order in main app

    @staticmethod
    def i_enable() -> bool:
        return Path("/usr/bin/pacman-mirrors").exists()

    @staticmethod
    def get_class():
        # return class and not instance
        return MirrorsWidget
