from abc import ABC, abstractmethod
from pathlib import Path
import random
import importlib.util

from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QIcon, QFont, QPainter, QBrush, QColor, QPen, QPixmap, QPalette
from PySide6.QtWidgets import QApplication


class PluginBase(ABC):
    NAME = ""
    ORDER = 100
    CATEGORY = ""
    COLOR = ""

    @classmethod
    def getAction(cls):
        pass

    @classmethod
    def getIcon(cls) -> QIcon:
        return cls.createIcon(cls.NAME[0].upper(), 32, cls.COLOR)

    @classmethod
    def getMenu(cls):
        # if necessary ?
        pass

    @classmethod
    def getTitle(cls) -> str:
        return cls.NAME

    @staticmethod
    def isEnable() -> bool:
        return True

    @staticmethod
    @abstractmethod
    def get_class() -> type:
        pass

    @staticmethod
    def createIcon(letter: str, size=22, color=""):
        palette = QApplication.palette()
        pixmap = QPixmap(size, size)  # Create a larger pixmap with extra width on the left
        pixmap.fill(QColor("transparent"))
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        if not color:
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
            color = QColor(r, g, b)
        else:
            color = QColor(color)

        # dark = color.darker() # other way to Shadow color ?
        dark = palette.color(QPalette.ColorRole.Shadow)
        dark.setAlpha(100)
        # painter.setPen(QPen(dark, 1))
        painter.setPen(dark)

        painter.setBrush(QBrush(color))

        painter.drawEllipse(0, 0, size, size)
        font = QFont()
        h = size * 0.8
        font.setPixelSize(h)
        painter.setFont(font)
        r = QRect(0, 0, size, size)
        # text Shadow
        painter.drawText(r.translated(2, 2), Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignHCenter, letter)
        painter.setPen(QPen(QColor("white"), 1))
        painter.drawText(r, Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignHCenter, letter)
        painter.end()
        return QIcon(pixmap)


class PluginManager:
    def __init__(self):
        self.modules: dict[str, PluginBase] = {}
        self.path = Path(__file__).parent.parent

    def scan(self, path=""):
        if path:
            self.path = Path(path)
        for directory in (d for d in self.path.iterdir() if d.is_dir() and not d.name.startswith("_")):
            name = directory.name
            file_ = directory / "plugin.py"
            if not file_.exists():
                continue
            try:
                mod = importlib.import_module(f"{self.path.parts[-1]}.{name}.plugin")
            except ModuleNotFoundError as err:
                print(err)
                continue
            if mod:
                try:
                    # self.modules[name] = getattr(mod, "Plugin")
                    self.modules[name] = mod.Plugin()  # save the class instance
                except AttributeError as err:
                    print(err)
                    # no class Plugin in file !
                    pass

        # sort plugins
        sorts = {k: v for k, v in sorted(self.modules.items(), key=lambda item: item[1].ORDER)}
        self.modules = sorts

        return self.modules
