import sys
from pathlib import Path
from PIL import Image

waveshare_lib_path = Path.home() / "e-Paper" / "RaspberryPi_JetsonNano" / "python" / "lib"
if waveshare_lib_path.exists():
    sys.path.append(str(waveshare_lib_path))

from waveshare_epd import epd7in5_V2


class EPaperDisplay:
    def __init__(self):
        self.width = 480
        self.height = 800
        self.epd = epd7in5_V2.EPD()

    def init(self):
        self.epd.init()
        self.epd.Clear()

    def show_portrait_image(self, portrait_image):
        image = portrait_image.rotate(90, expand=True)
        self.epd.display(self.epd.getbuffer(image))

    def sleep(self):
        self.epd.sleep()

    def clear(self):
        self.epd.init()
        self.epd.Clear()