#!/usr/bin/env python
import gzip
import re
import subprocess
import sys
from pathlib import Path
from urllib import request

from PySide6.QtCore import QThread, Signal


class EolManager:
    DB_FILE = Path("/tmp/unstable.core.db")

    def __init__(self):
        self.state = 0
        self.unstable = []
        self.kernels = []
        if self.download():
            self.state = 1
            self.unstable = sorted(self.filter_kernels(self.get_pkgs(self.DB_FILE)))
            if not self.unstable:
                return

    def __del__(self):
        # self.DB_FILE.unlink(True)
        pass

    def get_eol(self) -> list[str]:
        if not self.state or not self.unstable:
            return []
        if not self.kernels:
            self.kernels = sorted(list(self._get_current_kernels()))

            if "--dev" in sys.argv:
                print("  # --dev : add fake EOL kernels : 66 and 54")
                if i := self.unstable.index("linux66"):
                    del self.unstable[i]
                if i := self.unstable.index("linux54"):
                    del self.unstable[i]

        return [k for k in self.kernels if k not in self.unstable]

    def download(self) -> bool:
        if self.DB_FILE.exists():
            return True
        url = self._get_url()
        if not url:
            return False
        try:
            with request.urlopen(url, timeout=4) as response:
                with open(self.DB_FILE, "wb") as downloaded:
                    downloaded.write(response.read())
                    print("  #", self.DB_FILE, "downloaded")
                    return True
        except Exception:
            return False

    @staticmethod
    def _get_current_kernels():
        output = subprocess.run(
            "pacman -Ssq |  grep -E '^linux[0-9]{2,3}(-rt)?$'", capture_output=True, shell=True, text=True, timeout=3
        ).stdout
        return output.splitlines()

    @staticmethod
    def get_pkgs(file_):
        """parse pacman database gz file"""
        """
        %NAME%
        linux612
        %VERSION%
        6.12.32-1
        %BUILDDATE%
        1749062743
        """
        with gzip.open(file_, "rt") as f:
            for line in f:
                if not line.startswith("%NAME%"):
                    continue
                name = next(f)
                if not name.startswith("linux"):
                    continue
                yield name.rstrip()

    @staticmethod
    def filter_kernels(names):
        # filter only kernels
        reg = re.compile(r"^linux[0-9]{2,3}(-rt)?$")
        yield from (n for n in names if reg.match(n))

    @staticmethod
    def _get_url() -> str:
        # search unstable url for core
        output = subprocess.run(
            "pacman-conf -r core | grep '^Server' -m1", capture_output=True, shell=True, text=True, timeout=3
        ).stdout
        if not output or "/unstable/" in output:
            return ""
        url = output.split("=")[1].strip()
        url = url.replace("/stable/", "/unstable/")
        url = url.replace("/testing/", "/unstable/")
        return f"{url}/core.db"


class EolWorker(QThread):
    eol = Signal(list)

    def __init__(self):
        super().__init__()
        self.finished.connect(self.deleteLater)

    def __del__(self):
        # print("deleted ! EolWorker")
        pass

    def run(self):
        manager = EolManager()
        kernels = manager.get_eol()
        self.eol.emit(kernels)
        self.deleteLater()


if __name__ == "__main__":
    manager = EolManager()
    print("state:", manager.state)
    print("unstable:", manager.unstable)
    print("local kernels:", manager.kernels)

    print()
    if i := manager.unstable.index("linux515"):
        del manager.unstable[i]
    print()
    print("EOL kernels:", manager.get_eol())
    print("local kernels:", manager.kernels)

    print()
    manager.kernels = ("linux66", "linux405", "linux406")
    print("EOL kernels:", manager.get_eol())
    print("local kernels:", manager.kernels)
