import sys
from pathlib import Path

from .._plugin.base import PluginBase

sys.path.insert(0, str(Path(__file__).parent))
from .main import MaterialWidget

sys.path.pop(0)


class Plugin(PluginBase):
    NAME = "Material"
    ORDER = 80  # 10 by 10, order in main app

    @staticmethod
    def i_enable() -> bool:
        return Path("/usr/bin/mhwd").exists()

    @staticmethod
    def get_class():
        # return class and not instance
        return MaterialWidget
