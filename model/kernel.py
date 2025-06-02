#!/usr/bin/env python


from enum import Enum
import os
from pathlib import Path
import platform
import subprocess
from urllib import request, error
from typing import Self


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
    isRecommanded: bool
    isInstalled: bool
    isActive: bool

    CURRENT = ".".join(platform.release().split(".", maxsplit=2)[0:2])

    def __init__(self, name: str, version=""):
        self.name = name
        self.version = version

        self.major = 0
        self.minor = 0
        self.isRT = False
        self.parse_version(name)

        self.isLTS = False
        self.isRecommanded = False
        self.isInstalled = False
        self._set_installed()

        self.isActive = False
        if not self.isRT:
            self.isActive = self.get_ver().strip() == self.CURRENT
        else:
            if self.isActive:
                self.isActive = "-rt" in platform.release()

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
        self.isInstalled = path.exists()
        if self.isInstalled and Path("/etc/mkinitcpio.d").exists():
            self.isInstalled = Path(f"/etc/mkinitcpio.d/{self.name}.preset").exists()

    def get_ver(self) -> str:
        ret = f"{self.major}.{self.minor}"
        return f"{ret:4} {'LTS' if self.isLTS else '   '}"

    def isExperimental(self) -> bool:
        return ".0rc" in self.version

    def isEOL(self) -> bool:
        # TODO if branch:= unstable : async is present in unstable/core.db ?
        pass

    def get_changelog_url(self) -> str:
        return f"https://kernelnewbies.org/Linux_{self.major}.{self.minor}?action=print"

    def __str__(self) -> str:
        return (
            f"{self.name} -> {self.get_ver()} -> {self.version} {'(rt)' if self.isRT else ''} {'***' if self.isRecommanded else ''}"
        )

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
        self.config = {"LTS": [], "RECOMMENDED": []}

    def load_config(self, local_file: Path):
        if local_file.exists():
            self.config = self._load_file(str(local_file))

        try:
            self.config = self._get_lts_from_kernel_org()
        except error.URLError as err:
            print(f"no internet ! {err}\nwe use local datas", file=os.stderr)

        try:
            self.config = self._get_kernels_from_gitlab()
        except error.URLError as err:
            print(f"no internet ! {err}\nwe use local datas", file=os.stderr)

        kernels = self.get_kernels()
        for k in self.config.get("LTS"):
            if kernel := kernels.get(k):
                kernel.isLTS = True
        for k in self.config.get("RECOMMENDED"):
            if kernel := kernels.get(k):
                kernel.isRecommanded = True

        for k in sorted((k for k in kernels.values()), reverse=True):
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

    def get_installeds(self):
        return [k for k in self if k.isInstalled]

    @staticmethod
    def _parse_file(content):
        results = {"LTS": [], "RECOMMENDED": []}
        for line in content.split("\n"):
            if not line or line.startswith("#"):
                continue
            parts = line.split(";")
            results[parts[0].upper()] = [k.strip() for k in parts[1:] if k.strip()]
        return results

    @classmethod
    def _load_file(cls, url: str) -> dict:
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

    @staticmethod
    def get_kernels() -> dict[str, Kernel]:
        reg = r"LANG=en pacman -Si | grep -E '^(Name|Version)' | grep -E 'Name.*linux[0-9]{2,3}(-rt)?$' -A1"

        output = subprocess.run(reg, capture_output=True, shell=True, text=True, timeout=30).stdout
        lines = iter(l for l in output.split("\n") if l and not l.startswith("--"))
        kernels = {}
        for name, version in zip(lines, lines):
            name = name.split(":")[1].strip()
            version = version.split(":")[1].strip()
            kernels[name] = Kernel(name, version)
        return kernels

    @staticmethod
    def _get_kernels_from_gitlab():
        """read manjaro datas from gitlab .c file"""

        def filter(line):
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
            content = [l.replace('"', "").replace(";", "") for l in response.read().decode("utf-8").split("\n") if filter(l)]
            results["LTS"] = [k.strip() for k in content[1].split("<<")[1:]]
            results["RECOMMENDED"] = [k.strip() for k in content[3].split("<<")[1:]]
        return results

    @staticmethod
    def _get_lts_from_kernel_org():
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


if platform.freedesktop_os_release()["ID"].lower() != "manjaro":
    exit(66)
if platform.machine() != "x86_64":
    # kernel names differ !
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
        def color(text: str, color: Self, long: int = 0):
            return color.txt(text.ljust(long, " "))

    local_file = Path(__file__).parent / "kernels.csv"

    kernels = Kernels()
    kernels.load_config(local_file)

    print("run:", "linux", platform.release())
    print()

    for k in kernels:
        v = f"{k.major}.{k.minor} {'LTS' if k.isLTS else ''}"
        print(
            f"{Style.color(k.name, Style.GREEN if k.isLTS else Style.RESET, 12)} -> {k.get_ver():8}  {Style.GRAY.txt(k.version)} {'(rt)' if k.isRT else ''} {'***' if k.isRecommanded else ''} {Style.BLUE.txt('\tInstalled') if k.isInstalled else ''}",
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