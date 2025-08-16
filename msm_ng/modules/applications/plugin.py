import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from .._plugin.base import PluginBase

sys.path.insert(0, str(Path(__file__).parent))
from .ui.main import ApplicationsMain

sys.path.pop(0)


class Plugin(PluginBase):
    NAME = QApplication.translate("entry", "Applications")
    ORDER = 95

    @classmethod
    def get_title(cls) -> str:
        return cls.NAME

    @staticmethod
    def get_class():
        # return class and not instance
        return ApplicationsMain
