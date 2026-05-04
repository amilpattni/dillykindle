from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from app.epaper.display import EPaperDisplay


class EPaperApp:
    def __init__(self):
        self.display = EPaperDisplay()
        self.screen = "home"
        self.selected_index = 0
        self.home_options = [
            "read",
            "edit books",
            "bookmarks",
        ]

    def load_font(self, size):
        possible_fonts = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]

        for font_path in possible_fonts:
            if Path(font_path).exists():
                return ImageFont.truetype(font_path, size)

        return ImageFont.load_default()

    def render_home(self):
        image = Image.new("1", (480, 800), 255)
        draw = ImageDraw.Draw(image)

        title_font = self.load_font(34)
        subtitle_font = self.load_font(16)
        menu_font = self.load_font(24)
        small_font = self.load_font(14)

        draw.text((45, 70), "dillykindle", font=title_font, fill=0)
        draw.text((45, 120), "for when diya wants to read", font=subtitle_font, fill=0)

        y_positions = [260, 320, 380]

        for i, option in enumerate(self.home_options):
            text = f"> {option} <" if i == self.selected_index else option
            draw.text((70, y_positions[i]), text, font=menu_font, fill=0)

        draw.text((45, 730), "w/s = move   e = select   q = back", font=small_font, fill=0)

        return image

    def render_placeholder(self, title):
        image = Image.new("1", (480, 800), 255)
        draw = ImageDraw.Draw(image)

        title_font = self.load_font(30)
        body_font = self.load_font(18)

        draw.text((45, 70), title, font=title_font, fill=0)
        draw.text((45, 160), "placeholder screen", font=body_font, fill=0)
        draw.text((45, 210), "press q to go home", font=body_font, fill=0)

        return image

    def redraw(self):
        if self.screen == "home":
            image = self.render_home()
        elif self.screen == "read":
            image = self.render_placeholder("read")
        elif self.screen == "edit books":
            image = self.render_placeholder("edit books")
        elif self.screen == "bookmarks":
            image = self.render_placeholder("bookmarks")
        else:
            image = self.render_placeholder("unknown")

        self.display.show_portrait_image(image)

    def handle_up(self):
        if self.screen == "home":
            self.selected_index = (self.selected_index - 1) % len(self.home_options)

    def handle_down(self):
        if self.screen == "home":
            self.selected_index = (self.selected_index + 1) % len(self.home_options)

    def handle_select(self):
        if self.screen == "home":
            self.screen = self.home_options[self.selected_index]

    def handle_back(self):
        self.screen = "home"

    def run(self):
        self.display.init()
        self.redraw()

        while True:
            command = input("Command (w/s/e/q/x): ").strip().lower()

            if command == "w":
                self.handle_up()
            elif command == "s":
                self.handle_down()
            elif command == "e":
                self.handle_select()
            elif command == "q":
                self.handle_back()
            elif command == "x":
                break

            self.redraw()

        self.display.sleep()


if __name__ == "__main__":
    app = EPaperApp()
    app.run()