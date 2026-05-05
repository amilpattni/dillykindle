import sys
from pathlib import Path


waveshare_lib_path = Path.home() / "e-Paper" / "RaspberryPi_JetsonNano" / "python" / "lib"
if str(waveshare_lib_path) not in sys.path:
    sys.path.append(str(waveshare_lib_path))

from waveshare_epd import epd7in5_V2


class EPaperDisplay:
    def __init__(self):
        self.portrait_width = 480
        self.portrait_height = 800
        self.display_width = 800
        self.display_height = 480
        self.epd = epd7in5_V2.EPD()
        self.partial_mode = False

    def _to_display_image(self, portrait_image):
        return portrait_image.convert("1").rotate(90, expand=True)

    def startup(self, portrait_image):
        image = self._to_display_image(portrait_image)
        self.epd.init_fast()
        self.epd.display(self.epd.getbuffer(image))
        self.partial_mode = False

    def full_refresh(self, portrait_image):
        image = self._to_display_image(portrait_image)
        self.epd.init()
        self.epd.display(self.epd.getbuffer(image))
        self.partial_mode = False

    def partial_refresh(self, portrait_image):
        image = self._to_display_image(portrait_image)

        if not self.partial_mode:
            self.epd.init_part()
            self.partial_mode = True

        self.epd.display_Partial(
            self.epd.getbuffer(image),
            0,
            0,
            self.display_width,
            self.display_height
        )

    def sleep(self):
        self.epd.sleep()
