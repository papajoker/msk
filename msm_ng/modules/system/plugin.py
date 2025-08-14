import sys
from pathlib import Path

from .._plugin.base import PluginBase

sys.path.insert(0, str(Path(__file__).parent))
from main import SystemWidget

sys.path.pop(0)


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
