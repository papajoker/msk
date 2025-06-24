import os
import sys
from pathlib import Path

from .._plugin.base import PluginBase

sys.path.insert(0, str(Path(__file__).parent))
from ui.test import UserMain

sys.path.pop(0)


class Plugin(PluginBase):
    NAME = "User"
    ORDER = 20  # 10 by 10, order in main app
    # COLOR = "#440066"

    @classmethod
    def get_title(cls) -> str:
        return cls.NAME

    @staticmethod
    def is_enable() -> bool:
        if os.environ.get("XDG_CURRENT_DESKTOP") == "KDE":
            print("User config exists with plasma")
            # return False
        return True

    @staticmethod
    def get_class():
        # return class and not instance
        return UserMain
