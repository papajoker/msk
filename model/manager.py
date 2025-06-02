from pathlib import Path
import subprocess
from kernel import Kernel, Kernels


class KernelManager:
    """
    TODO : manage linux***-headers as `linux510-headers` ... `linux612-rt-headers`
    TODO : manage ? linux-meta, linux-headers-meta ?
    """

    # https://gitlab.manjaro.org/applications/application-utility/-/blob/master/application_utility/browser/alpm.py
    # pamac-installer --remove pkg1 pkg2
    # pamac-installer pkg1 pkg2  # install
    # subprocess.run(['pamac-installer'] + install + pkg_list, capture_output=True, check=True)
    # is NOT good, no return if Ok or not
    # ? gui is fixed or not ?
    # TODO test

    """
    best : use python binding:
        import gi
        gi.require_version("Pamac", "11")
        from gi.repository import Pamac
    """

    def __init__(self, kernels: Kernels):
        # HELP usefull ??? is not in mhwd-kernels ?
        self.use_header = self._use_header(kernels)
        # TODO other modules ??? -nvidia-** , -r8168 ???

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
