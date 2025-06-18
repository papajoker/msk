import importlib
import random
import sys
from abc import ABC, abstractmethod
from pathlib import Path

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QIcon, QPainter, QPalette, QPen, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication


def dark_theme_exists() -> bool:
    """QT user have a light or dark theme ?"""
    return QApplication.palette().color(QPalette.ColorRole.Text).lightnessF() <= 0.179


class PluginBase(ABC):
    NAME = ""
    ORDER = 100
    CATEGORY = ""

    def __init__(self, color=None):
        self.color = color if color else ""

    @classmethod
    def get_action(cls):
        pass

    def get_icon(self, size=48) -> QIcon:
        return self.create_icon(self.NAME[0].upper(), size, self.color)

    @classmethod
    def get_menu(cls):
        # if necessary ?
        pass

    @classmethod
    def get_title(cls) -> str:
        return cls.NAME

    @staticmethod
    def is_enable() -> bool:
        # if not kesktop, or if desktop ...
        # or if wayland : return False, or ?...
        return True

    @staticmethod
    @abstractmethod
    def get_class() -> type:
        pass

    @staticmethod
    def create_Icon_old(letter: str, size=72, color=""):
        palette = QApplication.palette()
        pixmap = QPixmap(size, size)  # Create a larger pixmap with extra width on the left
        pixmap.fill(QColor("transparent"))
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

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
        font.setPixelSize(int(h))
        painter.setFont(font)
        r = QRect(0, 0, size, size)
        # text Shadow
        painter.drawText(r.translated(2, 2), Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignHCenter, letter)
        painter.setPen(QPen(QColor("white"), 1))
        painter.drawText(r, Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignHCenter, letter)
        painter.end()
        return QIcon(pixmap)

    @classmethod
    def create_icon(cls, letter: str, size=72, color=""):
        palette = QApplication.palette()
        color_txt = palette.color(QPalette.ColorRole.Text).name()

        color_h = palette.color(QPalette.ColorRole.BrightText).name()
        color_s = palette.color(QPalette.ColorRole.Shadow).name()
        if not color:
            color = QColor.fromHsv(
                random.randint(0, 259),
                random.randint(0, 200),
                random.randint(0, 180),
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
        return cls._create_icon_from_svg(content, size=QSize(size, size))

    @staticmethod
    def _create_icon_from_svg(svg_content: str, size: QSize = QSize(128, 128)) -> QIcon:
        # print(svg_string)
        renderer = QSvgRenderer(svg_content.encode("utf-8"))
        pixmap = QPixmap(size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        return QIcon(pixmap)


"""
manager assign always sames colors
"""
colors = [
    "#30b882",
    "#f8da38",
    "#bb9b93",
    "#a451bb",
    "#1f6d80",
    "#603817",
    "#d2dccc",
    "#1e3058",
    "#89d99c",
    "#53c3d4",
    "#fc6f60",
    "#de00ee",
    "#7e7e7f",
    "#bc3a13",
    "#5978cc",
    "#348f3d",
    "#a6a13e",
    "#9e9bd6",
    "#0e1d0a",
    "#533796",
    "#d3d56d",
    "#9a5151",
    "#333cd7",
    "#38da38",
]


class PluginManager:
    def __init__(self):
        self.modules: dict[str, PluginBase] = {}
        self.path = Path(__file__).parent.parent

    def scan(self, path=""):
        if path:
            self.path = Path(path)
        i = 0
        for directory in (d for d in self.path.iterdir() if d.is_dir() and not d.name.startswith("_")):
            name = directory.name
            file_ = directory / "plugin.py"
            if not file_.exists():
                continue
            try:
                mod = importlib.import_module(f"{self.path.parts[-1]}.{name}.plugin")
            except ModuleNotFoundError as err:
                print(err, file=sys.stderr)
                continue
            if mod:
                try:
                    self.modules[name] = mod.Plugin()  # save the class instance
                    i += 1
                    try:
                        self.modules[name].color = colors[i]
                    except IndexError:
                        i = 0
                        self.modules[name].color = colors[i]
                except AttributeError as err:
                    # no class Plugin in file !
                    print(err, file=sys.stderr)

        # sort plugins
        sorts = {k: v for k, v in sorted(self.modules.items(), key=lambda item: item[1].ORDER)}
        self.modules = sorts

        return self.modules
