from PySide6.QtCore import QProcess, QObject, Signal

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

    def start_command(self, arguments: str):
        if arguments is None:
            return
        self.buffer_output = bytearray()
        self.buffer_error = bytearray()

        cmd = "run0 --description='manjaro kernel' --unit=manjaroKernelTransaction --property='CPUQuota=80%' --background="
        cmd = f"echo '{arguments}' | {cmd}"
        print(f"::run : {cmd}")
        self.process.startCommand(
            f'bash -c "{cmd}"',
        )

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
