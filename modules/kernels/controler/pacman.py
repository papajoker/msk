import os
from datetime import datetime
from pathlib import Path
from textwrap import dedent
from zoneinfo import ZoneInfo

from PySide6.QtCore import QObject, QProcess, Signal

"""
 run0 --description="manjaro kernel" --unit=manjaroKernelTransaction --property="CPUQuota=30%" --background= env
 echo "env ; ls -l" | run0 --description="manjaro kernel" --unit=manjaroKernelTransaction --property="CPUQuota=30%" --background=
"""


class PacmanWorker(QObject):
    lineStdOut = Signal(str)
    lineStdErr = Signal(str)
    started = Signal()
    finished = Signal(int, QProcess.ExitStatus)
    error = Signal(QProcess.ProcessError)
    SCRIPT = Path("/tmp/msk.sh")

    def __init__(self):
        super().__init__()
        self.buffer_output = None
        self.buffer_error = None
        self.process = QProcess(self)

        self.process.started.connect(self.started)
        self.process.errorOccurred.connect(self.error)
        self.process.readyReadStandardOutput.connect(self._read_standard_output)
        self.process.readyReadStandardError.connect(self._read_standard_error)
        self.process.finished.connect(self._handle_finished)

    def __del__(self):
        # self.SCRIPT.unlink(True)
        pass

    def start_command(self, arguments: str):
        if arguments is None:
            return
        self.buffer_output = bytearray()
        self.buffer_error = bytearray()

        script = self._create_script(arguments)
        cmd = "run0 --description='manjaro kernel' --unit=manjaroKernelTransaction --property='CPUQuota=80%' --background="
        # cmd = f"echo '{arguments}' | {cmd}"
        print(f"::run : echo '{arguments}' | {cmd}")  # false
        self.process.startCommand(
            f'bash -c "{cmd} {script}"',
        )

    def _create_script(self, arguments) -> str:
        content = f"""\
            #!/usr/bin/bash
            set -e

            echo -e "{self.get_log(arguments)}" >> /var/log/pacman.log && sleep 1

            {arguments}
        """
        script = self.SCRIPT
        script.write_text(dedent(content))
        script.chmod(0o776)
        return str(script)

    @staticmethod
    def get_log(msg):
        tz_path = os.readlink("/etc/localtime")
        tz_name = "/".join(tz_path.split("/")[4:])
        now = datetime.now(ZoneInfo(tz_name))
        result = now.isoformat(timespec="seconds")
        if result[-6] in ("+", "-"):
            result = f"{result[:-3]}{result[-2:]}"
        return f"[{result}] [MSK] {msg}"

    def terminate(self):
        self.process.terminate()

    def kill(self):
        self.process.kill()

    def _read_standard_output(self):
        data = self.process.readAllStandardOutput()
        self.buffer_output.extend(data)
        while b"\n" in self.buffer_output:
            line, self.buffer_output = self.buffer_output.split(b"\n", 1)
            self.lineStdOut.emit(line.decode(errors="ignore"))

    def _read_standard_error(self):
        data = self.process.readAllStandardError()
        self.buffer_error.extend(data)
        while b"\n" in self.buffer_error:
            line, self.buffer_error = self.buffer_error.split(b"\n", 1)
            self.lineStdErr.emit(line.decode(errors="ignore").strip())

    def _handle_finished(self, exit_code, exit_status):
        if self.buffer_output:
            self.lineStdOut.emit(self.buffer_output.decode(errors="ignore"))
            self.buffer_output = bytearray()
        if self.buffer_error:
            self.lineStdErr.emit(self.buffer_error.decode(errors="ignore"))
            self.buffer_error = bytearray()

        self.finished.emit(exit_code, exit_status)
