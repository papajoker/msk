from pathlib import Path
import subprocess

from PySide6.QtCore import QObject, Signal

from model.kernel import Kernel, Kernels


class KernelManager(QObject):
    """
    TODO : get code from ui.main.py
    """

    usefull_or_not = Signal()

    def __init__(self, kernels: Kernels):
        self.kernels = kernels
        """
            ? all kernels in list or only ok ?
        """
        self.origin = self.kernels.get_installeds()
        self.todo = []
        # HELP usefull ??? is not in mhwd-kernels ?
        self.use_header = self._use_header(kernels)
        # TODO other modules ??? -nvidia-** , -r8168 ???

    def origin_to_str(self) -> str:
        return ", ".join(self.origin)

    def todo_to_str(self) -> str:
        return ", ".join(self.origin)

    def compare(self) -> list:
        #
        [k for k in self.todo if k not in self.origin]
        [k for k in self.origin if k not in self.todo]

    # -- old to remove

    def get_pkg_list(self, kernels: list[Kernel]):
        results = []
        for kernel in (k for k in kernels if k):
            results.append(kernel.name)
            if self.use_header:
                results.append(f"{kernel.name}-headers")
        return results

    def install(self, pkgs: list):
        ...
        if Path("/usr/bin/grub-mkconfig").exists():
            # run update_grub
            ...

    def uninstall(self, pkgs: list): ...

    def _use_header(self, kernels: Kernels) -> bool:
        """ok if ONE use"""
        status, _ = subprocess.getstatusoutput("pacman -Qi linux-headers-meta")
        if status == 0:
            return True
        for want in (f"{k.name}-headers" for k in kernels if k.isInstalled):
            status, _ = subprocess.getstatusoutput(f"pacman -Qi {want}")
            if status == 0:
                return True
        return False


if __name__ == "__main__":
    local_file = Path(__file__).parent / "kernels.csv"

    kernels = Kernels()
    kernels.load_config(local_file)

    kernel_manager = KernelManager(kernels)

    if not kernel_manager.use_header:
        print("# this system not use -headers")

    if ks := kernel_manager.get_pkg_list([kernels["642"]]):
        print("pacman -S", " ".join(ks))
    print("add ? 611 612 610 ?")
    if ks := kernel_manager.get_pkg_list(
        [
            kernels["611"],
            kernels["612"],
            kernels["610"],
        ]
    ):
        print("pacman -S", " ".join(ks))
