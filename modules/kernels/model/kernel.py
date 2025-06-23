import platform
import subprocess
import sys
from enum import Enum
from pathlib import Path
from typing import Self
from urllib import error, request

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QFontMetrics, QIcon, QPainter, QPalette, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication

"""
csv content = '''
LTS;linux54, linux510 ; linux515;linux61; linux66; linux612;;;
recommended; linux510; linux612
'''
"""


class Kernel:
    name: str
    version: str
    isRT: bool
    isRecommended: bool
    isInstalled: bool
    isActive: bool
    isEOL: bool

    class Selection(Enum):
        OUT = 0
        IN = 1

    CURRENT = ".".join(platform.release().split(".", maxsplit=2)[0:2])

    def __init__(self, name: str, version=""):
        self.name = name
        self.version = version
        self.selection = self.Selection.OUT

        self.major = 0
        self.minor = 0
        self.isRT = False
        self.parse_version(name)

        self.isLTS = False
        self.isEOL = False
        self.isRecommended = False
        self.isInstalled = self._set_installed()
        self._initial_selection = self.isInstalled

        self.isActive = False
        if not self.isRT:
            self.isActive = self.get_ver().strip() == self.CURRENT
        else:
            if self.isActive:
                self.isActive = "-rt" in platform.release()

        self.icon = self.setIcon()

    def setIcon(self):
        maker = IconMaker(self)
        self.icon = maker.make(128)
        return self.icon

    def parse_version(self, name):
        name = name.removeprefix("linux")
        if name.endswith("-rt"):
            self.isRT = True
            name = name.removesuffix("-rt")
        self.major = int(name[0])
        self.minor = int(name[1:])

    def _set_installed(self):
        # not perfect if partial update, prefer test if pacman -Qi self.name return 0
        path = Path("/var/lib/pacman/local") / f"{self.name}-{self.version}"
        is_installed = path.exists()
        self.selection = self.Selection.IN if is_installed else self.Selection.OUT
        return is_installed

    def get_ver(self) -> str:
        ret = f"{self.major}.{self.minor}"
        return f"{ret:4} {'LTS' if self.isLTS else '   '}"

    def isExperimental(self) -> bool:
        return ".0rc" in self.version

    def get_changelog_url(self) -> str:
        return f"https://kernelnewbies.org/Linux_{self.major}.{self.minor}?action=print"

    @property
    def has_changed(self) -> bool:
        return self.selection != self._initial_selection

    def __hash__(self) -> int:
        return hash(self.name)

    def __str__(self) -> str:
        return f"{self.name} -> {self.get_ver()} -> {self.version} {'(rt)' if self.isRT else ''} {'***' if self.isRecommended else ''}"

    def __lt__(self, other: Self):
        """for good sort"""
        if self.isRT != other.isRT:
            return self.isRT and not other.isRT
        a, b = self.major, other.major
        if a != b:
            return a < b
        a, b = self.minor, other.minor
        if a != b:
            return a < b


class Kernels(list):
    CURRENT = ".".join(platform.release().split(".", maxsplit=2)[0:2])

    def __init__(self):
        super().__init__()
        self.config = {"LTS": [], "RECOMMENDED": []}

    def load_config(self, local_file: Path):
        if local_file.exists():
            self.config = self._load_file(str(local_file))

        try:
            # useful if gitlab ko
            self.config = self._get_lts_from_kernel_org()
        except error.URLError as err:
            print(f"no internet ! {err}\nwe use local datas", file=sys.stderr)

        try:
            self.config = self._get_kernels_from_gitlab()
        except error.URLError as err:
            print(f"no internet ! {err}\nwe use local datas", file=sys.stderr)

        kernels = self.get_kernels()
        for k in self.config.get("LTS"):
            if kernel := kernels.get(k):
                kernel.isLTS = True
                kernel.setIcon()
        for k in self.config.get("RECOMMENDED"):
            if kernel := kernels.get(k):
                kernel.isRecommended = True
                kernel.setIcon()

        for k in sorted(kernels.values(), reverse=True):
            self.append(k)

    def __call__(self, name: str) -> Kernel | None:
        if not name.startswith("linux"):
            name = f"linux{name}"
        return next((k for k in self if name == k.name), None)

    def __getitem__(self, key: str | int):
        """not usefull"""
        if isinstance(key, str):
            return self.__call__(key)
        return super().__getitem__(key)

    def get_installeds(self) -> list[Kernel]:
        return [k for k in self if k.isInstalled]

    @staticmethod
    def _parse_file(content) -> dict[str, list[str]]:
        results = {"LTS": [], "RECOMMENDED": []}
        for line in content.split("\n"):
            if not line or line.startswith("#"):
                continue
            parts = line.split(";")
            results[parts[0].upper()] = [k.strip() for k in parts[1:] if k.strip()]
        return results

    @classmethod
    def _load_file(cls, url: str) -> dict[str, list[str]]:
        content = ""
        if url.startswith("http"):
            # TODO tests
            with request.urlopen(url) as response:
                content = response.read().decode("utf-8")
        else:
            content = Path(url).read_text()

        if not content:
            return {}

        if url.endswith("csv"):
            return cls._parse_file(content)
        return {}

    @staticmethod
    def get_kernels() -> dict[str, Kernel]:
        reg = r"LANG=en pacman -Si | grep -E '^(Name|Version)' | grep -E 'Name.*linux[0-9]{2,3}(-rt)?$' -A1"

        output = subprocess.run(reg, capture_output=True, shell=True, text=True, timeout=30).stdout
        lines = iter(line for line in output.split("\n") if line and not line.startswith("--"))
        kernels = {}
        for name, version in zip(lines, lines):
            name = name.split(":")[1].strip()
            version = version.split(":")[1].strip()
            if name not in kernels:
                # ignore duplicates
                kernels[name] = Kernel(name, version)
        return kernels

    @staticmethod
    def _get_kernels_from_gitlab() -> dict[str, list[str]]:
        """read manjaro datas from gitlab .c file"""

        def filter_line(line) -> bool:
            if "::getLtsKernels" in line or "::getRecommendedKernels" in line:
                return True
            if "return QStringList() <<" in line:
                return True
            return False

        results = {"LTS": [], "RECOMMENDED": []}
        with request.urlopen(
            "https://gitlab.manjaro.org/applications/manjaro-settings-manager/-/raw/master/src/libmsm/KernelModel.cpp",
            timeout=3,
        ) as response:
            content = [
                line.replace('"', "").replace(";", "")
                for line in response.read().decode("utf-8").split("\n")
                if filter_line(line)
            ]
            results["LTS"] = [k.strip() for k in content[1].split("<<")[1:]]
            results["RECOMMENDED"] = [k.strip() for k in content[3].split("<<")[1:]]
        return results

    @staticmethod
    def _get_lts_from_kernel_org() -> dict[str, list[str]]:
        import xml.etree.ElementTree as ET

        results = {"LTS": [], "RECOMMENDED": []}
        with request.urlopen(
            "https://www.kernel.org/feeds/kdist.xml",
            timeout=3,
        ) as response:
            root = ET.fromstring(response.read().decode("utf-8"))[0]
            for title in root.iter("title"):
                if "longterm" not in title.text:
                    continue
                ver = title.text.split(".")[0:2]
                results["LTS"].append(f"linux{ver[0]}{ver[1]}")
        return results


class IconMaker:
    STAR_SVG = """
        <polygon points="50,10 61,35 89,35 68,57 79,83 50,68 21,83 32,57 11,35 39,35" fill="currentColor"/>
        """  # remove tag <svg...></svg> if want use manjaro logo

    def __init__(self, kernel: Kernel, size=128):
        self.kernel = kernel
        self.size = size

    @staticmethod
    def create_icon_from_svg_string(svg_string: str, size: QSize = QSize(128, 128)) -> QIcon:
        renderer = QSvgRenderer(svg_string.encode("utf-8"))
        pixmap = QPixmap(size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        return QIcon(pixmap)

    def main_color(self, palette) -> str:
        if self.kernel.isActive:
            return "#bb0000"
        elif self.kernel.isInstalled:
            return palette.color(QPalette.ColorRole.Highlight).name()
        elif self.kernel.isRT:
            return palette.color(QPalette.ColorRole.PlaceholderText).name()
        return "#22aF4C"

    def _get_puces(self, line_height, palette) -> str:
        # radius, offset = size / 3, size / 1.5
        puces = []
        if self.kernel.isRecommended:
            star_color = palette.color(QPalette.ColorRole.BrightText).name()  # "#22aF4C"
            star_size_scale = line_height / 70
            # puces.append(f'<circle cx="{self.size - offset}" cy="{offset}" r="{radius}" fill="#22aF4C"/>')
            puces.append(f"""
                    <g transform="translate({self.size - line_height - 2}, {2}) scale({star_size_scale})">
                        {self.STAR_SVG.replace('fill="currentColor"', f'fill="{star_color}"')}
                    </g>
                """)

        """
        if self.kernel.isRT:
            puces.append(f'<circle cx="{offset}" cy="{offset}" r="{radius}" fill="#333333"/>')

        if self.kernel.isActive:
            puces.append(f'<circle cx="{offset}" cy="{self.size - offset}" r="{radius}" fill="#bb0000"/>')
        if self.kernel.isInstalled and not self.kernel.isActive:
            puces.append(f'<circle cx="{offset}" cy="{self.size - offset}" r="{radius}" fill="#8A2BE2"/>')
        # right bottom is free ... cx="{self.size - offset}" cy="{self.size - offset}"
        """

        return "".join(puces)

    def _get_eol(self, icon_size, line_height, palette) -> str:
        if not self.kernel.isEOL:
            return ""
        cross_color = palette.color(QPalette.ColorRole.Dark).name()
        cross_svg = ""
        cross_stroke_width = line_height
        margin = line_height * 1.5

        x1_diag = margin
        y1_diag = margin
        x2_diag = icon_size - margin
        y2_diag = icon_size - margin
        cross_svg += f'<line x1="{x1_diag}" y1="{y1_diag}" x2="{x2_diag}" y2="{y2_diag}" stroke="{cross_color}" stroke-width="{cross_stroke_width}" stroke-linecap="round"/>'

        x1_diag_alt = icon_size - margin
        y1_diag_alt = margin
        x2_diag_alt = margin
        y2_diag_alt = icon_size - margin
        cross_svg += f'<line x1="{x1_diag_alt}" y1="{y1_diag_alt}" x2="{x2_diag_alt}" y2="{y2_diag_alt}" stroke="{cross_color}" stroke-width="{cross_stroke_width}" stroke-linecap="round"/>'
        return cross_svg

    def _get_subtext(self, text_color) -> str:
        if not self.kernel.isRT and not self.kernel.isLTS:
            return ""
        attrs = (
            (str(self.size / 5.2)[:5], "RT"),
            (str(self.size / 4.7)[:5], "LTS"),
        )
        if self.kernel.isRT:
            attr = attrs[0]
        if self.kernel.isLTS:
            attr = attrs[1]
        return f'<text x="{self.size / 2}" y="{self.size - self.size / 8}" dominant-baseline="middle" text-anchor="middle" font-size="{attr[0]}" fill="{text_color}">{attr[1]}</text>'

    def make(self, icon_size: int) -> QIcon:
        if icon_size:
            self.size = icon_size
        h, _ = self.get_heights()
        width = h // 1.5

        palette = QApplication.palette()

        main_color = self.main_color(palette)

        text_version = f"{self.kernel.major}.{self.kernel.minor}"
        text_color = palette.color(QPalette.ColorRole.Text).name()

        lts_svg = self._get_subtext(text_color)
        puces_svg = self._get_puces(h, palette)

        svg_content = f"""
            <svg width="{self.size}" height="{self.size}" viewBox="0 0 {self.size} {self.size}" fill="none" xmlns="http://www.w3.org/2000/svg">
                {self._get_eol(icon_size, width, palette)}
                {lts_svg}
                <circle cx="{self.size / 2}" cy="{self.size / 2}" r="{self.size / 2 - width / 2}" stroke="{main_color}" stroke-width="{width}" fill="none"/>
                <text x="{self.size / 2}" y="{self.size / 2 + (self.size / h) + h / 2.5}" dominant-baseline="middle" text-anchor="middle" font-family="Arial" font-size="{self.size / 3.5}" fill="{text_color}">{text_version}</text>
                {puces_svg}
            </svg>
        """
        # print(svg_content)
        return self.create_icon_from_svg_string(svg_content, QSize(self.size, self.size))

    @staticmethod
    def get_heights() -> tuple[int, int]:
        metrics = QFontMetrics(QApplication.font())
        line_height = metrics.height()
        return line_height, line_height * 4


if platform.freedesktop_os_release()["ID"].lower() != "manjaro":
    exit(66)
if platform.machine() != "x86_64":
    exit(67)

if __name__ == "__main__":

    class Style(Enum):
        RED = "\033[31m"
        GREEN = "\033[32m"
        BLUE = "\033[34m"
        GRAY = "\033[90m"
        RESET = "\033[0m"

        def txt(self, text: str):
            return f"{self.value}{text}{self.RESET.value}"

        # @classmethod
        @staticmethod
        def color(text: str, color: "Style", long: int = 0):
            return color.txt(text.ljust(long, " "))

    local_file = Path(__file__).parent / "kernels.csv"

    kernels = Kernels()
    kernels.load_config(local_file)

    print("run:", "linux", platform.release())
    print()

    for k in kernels:
        v = f"{k.major}.{k.minor} {'LTS' if k.isLTS else ''}"
        print(
            f"{Style.color(k.name, Style.GREEN if k.isLTS else Style.RESET, 12)} -> {k.get_ver():8}  {Style.GRAY.txt(k.version)} {'(rt)' if k.isRT else ''} {'***' if k.isRecommended else ''} {Style.BLUE.txt('\tInstalled') if k.isInstalled else ''}",
            end="",
        )
        if k.isActive:
            print(" ", Style.RED.txt("CURRENT"), end="")
        print()

    print()

    """        extended list :"""

    print()
    k = kernels("677")
    print("linux677 : ", k)
    k = kernels("612")
    print("linux612 : ", k)
    k = kernels("linux614")
    print("linux614 : ", k)
    k = kernels["54"]
    print("linux54 : ", k)

    k = kernels[2]
    print("second linux in list : ", k)
