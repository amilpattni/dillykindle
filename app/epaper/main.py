from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from app.epaper.display import EPaperDisplay


REFRESH_ON_MOVE = False


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

        draw.text((45, 730), "select changes screen | back returns home", font=small_font, fill=0)

        return image

    def render_placeholder(self, title):
        image = Image.new("1", (480, 800), 255)
        draw = ImageDraw.Draw(image)

        title_font = self.load_font(30)
        body_font = self.load_font(18)
        small_font = self.load_font(14)

        draw.text((45, 70), title, font=title_font, fill=0)
        draw.text((45, 160), "placeholder screen", font=body_font, fill=0)
        draw.text((45, 210), "press q/back to go home", font=body_font, fill=0)
        draw.text((45, 730), "minimal-refresh test mode", font=small_font, fill=0)

        return image

    def current_image(self):
        if self.screen == "home":
            return self.render_home()

        if self.screen == "read":
            return self.render_placeholder("read")

        if self.screen == "edit books":
            return self.render_placeholder("edit books")

        if self.screen == "bookmarks":
            return self.render_placeholder("bookmarks")

        return self.render_placeholder("unknown")

    def redraw(self):
        image = self.current_image()
        self.display.show_portrait_image(image)

    def print_state(self):
        if self.screen == "home":
            selected = self.home_options[self.selected_index]
            print(f"home selection: {selected}")
        else:
            print(f"screen: {self.screen}")

    def handle_up(self):
        if self.screen == "home":
            self.selected_index = (self.selected_index - 1) % len(self.home_options)

        self.print_state()

        if REFRESH_ON_MOVE:
            self.redraw()

    def handle_down(self):
        if self.screen == "home":
            self.selected_index = (self.selected_index + 1) % len(self.home_options)

        self.print_state()

        if REFRESH_ON_MOVE:
            self.redraw()

    def handle_select(self):
        if self.screen == "home":
            self.screen = self.home_options[self.selected_index]
            self.redraw()
            self.print_state()

    def handle_back(self):
        if self.screen != "home":
            self.screen = "home"
            self.redraw()

        self.print_state()

    def run(self):
        self.display.init()
        self.redraw()
        self.print_state()

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

        self.display.sleep()


if __name__ == "__main__":
    app = EPaperApp()
    app.run()
