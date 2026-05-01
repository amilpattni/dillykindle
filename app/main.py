import customtkinter as ctk

from app.config import APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT, MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT
from app.ui.home_screen import HomeScreen
from app.ui.start_book_screen import StartBookScreen
from app.ui.edit_books_screen import EditBooksScreen
from app.ui.bookmarks_screen import BookmarksScreen
from app.ui.reader_screen import ReaderScreen


class DillyPieApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.fullscreen = False
        self.current_frame = None

        self.bind("<F11>", self.toggle_fullscreen)

        self.show_home()

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
    app = DillyPieApp()
    app.mainloop()
