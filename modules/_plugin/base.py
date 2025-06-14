from abc import ABC, abstractmethod
from pathlib import Path
import random
import importlib.util

from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtGui import QIcon, QFont, QPainter, QBrush, QColor, QPen, QPixmap, QPalette
from PySide6.QtSvg import QSvgRenderer
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
    def getIcon(cls, size) -> QIcon:
        return cls.createIcon(cls.NAME[0].upper(), size, cls.COLOR)

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
    def createIconOLD(letter: str, size=72, color=""):
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

    @classmethod
    def createIcon(cls, letter: str, size=72, color=""):
        palette = QApplication.palette()
        color_txt = palette.color(QPalette.ColorRole.Text).name()

        color_h = palette.color(QPalette.ColorRole.BrightText).name()
        color_s = palette.color(QPalette.ColorRole.Shadow).name()
        if not color:
            color = QColor(
                random.randint(40, 200),
                random.randint(40, 240),
                random.randint(40, 200),
            )
        else:
            color = QColor(color)
        color_dark = color.darker(100)
        # print(color, color_dark)
        content = f"""<?xml version="1.0"?>
            <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" 
                width="{size}" height="{size}"
                viewBox="0 0 100 100" fill="none">
                <defs>
                    <linearGradient id="a" gradientTransform="rotate(45)">
                        <stop offset="5%" stop-color="{color_dark.name()}"/>
                        <stop offset="95%" stop-color="{color.name()}" stop-opacity="0.7"/>
                    </linearGradient>
                </defs>
                <circle cx="50" cy="50" r="47" stroke="{color_txt}" stroke-width="6"/>
                <circle cx="50" cy="50" r="36" fill="url(#a)"/>
                <text x="51" y="75" text-anchor="middle" font-family="Arial" font-size="72" fill="{color_s}">{letter.upper()}</text>
                <text x="50" y="76" text-anchor="middle" font-family="Arial" font-size="72" fill="{color_h}">{letter.upper()}</text>
            </svg>
        """
        return cls.create_icon_from_svg(content, size=QSize(size, size))

    @staticmethod
    def create_icon_from_svg(svg_content: str, size: QSize = QSize(128, 128)) -> QIcon:
        # print(svg_string)
        renderer = QSvgRenderer(svg_content.encode("utf-8"))
        pixmap = QPixmap(size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        renderer.render(painter)
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
