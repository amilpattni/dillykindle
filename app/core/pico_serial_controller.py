import time
from glob import glob

try:
    import serial
except Exception:
    serial = None


COMMAND_MAP = {
    "UP": "w",
    "DOWN": "s",
    "SELECT": "e",
    "BACK": "q",
    "POWER": "x",
}


class PicoSerialController:
    def __init__(self):
        self.ports = []
        self.known_paths = set()
        self.last_scan = 0
        self.scan()

    def scan(self):
        if serial is None:
            return

        now = time.time()
        if now - self.last_scan < 1:
            return

        self.last_scan = now

        paths = sorted(glob("/dev/ttyACM*") + glob("/dev/ttyUSB*"))

        for path in paths:
            if path in self.known_paths:
                continue

            try:
                port = serial.Serial(path, baudrate=115200, timeout=0)
                port.reset_input_buffer()
            except Exception:
                continue

            self.ports.append(port)
            self.known_paths.add(path)

    def read_command(self):
        if serial is None:
            return None

        self.scan()

        for port in list(self.ports):
            try:
                raw = port.readline()
            except Exception:
                try:
                    path = port.port
                    port.close()
                except Exception:
                    path = ""

                self.ports.remove(port)
                if path:
                    self.known_paths.discard(path)
                continue

            if not raw:
                continue

            text = raw.decode("utf-8", errors="ignore").strip().upper()

            if text in COMMAND_MAP:
                return COMMAND_MAP[text]

        return None
