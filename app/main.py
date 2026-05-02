import os

import customtkinter as ctk

from app.config import APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT, MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT
from app.core.startup import initialize_app_files
from app.ui.home_screen import HomeScreen
from app.ui.start_book_screen import StartBookScreen
from app.ui.edit_books_screen import EditBooksScreen
from app.ui.bookmarks_screen import BookmarksScreen
from app.ui.reader_screen import ReaderScreen


class DillyKindleApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.fullscreen = False
        self.start_fullscreen = os.environ.get("DILLYKINDLE_FULLSCREEN") == "1"
        self.current_frame = None
        self.gpio_controller = None

        self.bind("<F11>", self.toggle_fullscreen)
        self.bind_all("<Up>", lambda event: self.handle_hardware_button("up"))
        self.bind_all("<Down>", lambda event: self.handle_hardware_button("down"))
        self.bind_all("<Return>", lambda event: self.handle_hardware_button("select"))
        self.bind_all("<BackSpace>", lambda event: self.handle_hardware_button("back"))
        self.bind_all("h", lambda event: self.handle_hardware_button("back"))
        self.bind_all("H", lambda event: self.handle_hardware_button("back"))

        self.show_home()
        self.setup_gpio_buttons()

        if self.start_fullscreen:
            self.after(700, self.enter_fullscreen)

    def setup_gpio_buttons(self):
        if os.environ.get("DILLYKINDLE_GPIO") != "1":
            return

        try:
            from app.core.gpio_controller import HardwareButtonController
            self.gpio_controller = HardwareButtonController(self)
            print("GPIO buttons enabled.")
        except Exception as error:
            print(f"GPIO buttons disabled: {error}")

    def handle_hardware_button(self, action):
        if self.current_frame is None:
            return

        method_name = f"handle_{action}"
        method = getattr(self.current_frame, method_name, None)

        if method is not None:
            method()

    def enter_fullscreen(self):
        self.fullscreen = True
        self.attributes("-fullscreen", True)
        self.lift()
        self.focus_force()

    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.attributes("-fullscreen", self.fullscreen)

    def clear_screen(self):
        if self.current_frame is not None:
            self.current_frame.destroy()
            self.current_frame = None

    def set_screen(self, screen_class):
        self.clear_screen()
        self.current_frame = screen_class(self, self)
        self.current_frame.pack(fill="both", expand=True)

    def show_home(self):
        self.set_screen(HomeScreen)

    def show_start_book(self):
        self.set_screen(StartBookScreen)

    def show_edit_books(self):
        self.set_screen(EditBooksScreen)

    def show_bookmarks(self):
        self.set_screen(BookmarksScreen)

    def show_reader(self, book_id, start_page=None):
        self.clear_screen()
        self.current_frame = ReaderScreen(self, self, book_id, start_page)
        self.current_frame.pack(fill="both", expand=True)


if __name__ == "__main__":
    initialize_app_files()
    app = DillyKindleApp()
    app.mainloop()
