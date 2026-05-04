import inspect
from pathlib import Path
from textwrap import shorten

import fitz
from PIL import Image, ImageDraw, ImageFont, ImageOps

from app.core.book_manager import get_books, get_book
from app.core import bookmark_manager, progress_manager
from app.epaper.display import EPaperDisplay


PORTRAIT_WIDTH = 480
PORTRAIT_HEIGHT = 800

HOME_OPTIONS = ["read", "edit books", "bookmarks"]

MENU_PARTIAL_LIMIT = 14
READER_PARTIAL_LIMIT = 10


class EPaperApp:
    def __init__(self):
        self.display = EPaperDisplay()

        self.screen = "home"
        self.home_index = 0
        self.list_index = 0

        self.current_book_id = None
        self.current_page = 0
        self.reader_message = ""

        self.partial_count_since_full = 0

        self.font_cache = {}
        self.total_pages_cache = {}
        self.page_cache = {}

    def load_font(self, size):
        if size in self.font_cache:
            return self.font_cache[size]

        possible_fonts = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]

        for font_path in possible_fonts:
            if Path(font_path).exists():
                font = ImageFont.truetype(font_path, size)
                self.font_cache[size] = font
                return font

        font = ImageFont.load_default()
        self.font_cache[size] = font
        return font

    def clip_text(self, text, width=26):
        return shorten(text, width=width, placeholder="...")

    def save_progress(self, book_id, page):
        if hasattr(progress_manager, "set_page"):
            progress_manager.set_page(book_id, page)
            return

        if hasattr(progress_manager, "save_page"):
            progress_manager.save_page(book_id, page)
            return

        if hasattr(progress_manager, "set_progress"):
            progress_manager.set_progress(book_id, page)
            return

    def add_bookmark(self, book_id, page):
        func = getattr(bookmark_manager, "add_bookmark", None)
        if func is None:
            return

        book = get_book(book_id)
        title = book["title"] if book else "unknown"

        try:
            parameter_count = len(inspect.signature(func).parameters)
        except Exception:
            parameter_count = 2

        try:
            if parameter_count == 2:
                func(book_id, page)
            elif parameter_count == 3:
                func(book_id, title, page)
            else:
                func({
                    "book_id": book_id,
                    "book_title": title,
                    "page": page,
                })
        except TypeError:
            try:
                func(book_id, page)
            except Exception:
                pass

    def get_bookmarks(self):
        if not hasattr(bookmark_manager, "get_bookmarks"):
            return []

        bookmarks = []
        for bookmark in reversed(bookmark_manager.get_bookmarks()):
            book = get_book(bookmark["book_id"])
            if book is not None:
                bookmarks.append(bookmark)

        return bookmarks

    def get_total_pages(self, book_id):
        if book_id in self.total_pages_cache:
            return self.total_pages_cache[book_id]

        book = get_book(book_id)
        if book is None:
            return 0

        doc = fitz.open(book["path"])
        total = len(doc)
        doc.close()

        self.total_pages_cache[book_id] = total
        return total

    def get_rendered_page(self, book_id, page_index, max_width, max_height):
        cache_key = (book_id, page_index, max_width, max_height)
        if cache_key in self.page_cache:
            return self.page_cache[cache_key].copy()

        book = get_book(book_id)
        if book is None:
            image = Image.new("1", (max_width, max_height), 255)
            return image

        doc = fitz.open(book["path"])
        page = doc.load_page(page_index)
        rect = page.rect

        zoom = min(max_width / rect.width, max_height / rect.height) * 1.8
        matrix = fitz.Matrix(zoom, zoom)

        pix = page.get_pixmap(matrix=matrix, colorspace=fitz.csGRAY, alpha=False)
        image = Image.frombytes("L", [pix.width, pix.height], pix.samples)
        image = ImageOps.autocontrast(image)
        image.thumbnail((max_width, max_height))

        image = image.point(lambda p: 0 if p < 185 else 255, mode="1")

        doc.close()

        self.page_cache[cache_key] = image.copy()

        if len(self.page_cache) > 8:
            first_key = next(iter(self.page_cache))
            del self.page_cache[first_key]

        return image

    def partial_limit(self):
        if self.screen == "reader":
            return READER_PARTIAL_LIMIT
        return MENU_PARTIAL_LIMIT

    def show_current(self, mode="full"):
        image = self.render_current()

        if mode == "startup":
            self.display.startup(image)
            self.partial_count_since_full = 0
            return

        if mode == "full":
            self.display.full_refresh(image)
            self.partial_count_since_full = 0
            return

        self.partial_count_since_full += 1

        if self.partial_count_since_full >= self.partial_limit():
            self.display.full_refresh(image)
            self.partial_count_since_full = 0
        else:
            self.display.partial_refresh(image)

    def render_current(self):
        if self.screen == "home":
            return self.render_home()

        if self.screen == "read":
            return self.render_read()

        if self.screen == "bookmarks":
            return self.render_bookmarks()

        if self.screen == "reader":
            return self.render_reader()

        if self.screen == "edit books":
            return self.render_edit_placeholder()

        return self.render_edit_placeholder()

    def render_home(self):
        image = Image.new("1", (PORTRAIT_WIDTH, PORTRAIT_HEIGHT), 255)
        draw = ImageDraw.Draw(image)

        title_font = self.load_font(34)
        subtitle_font = self.load_font(16)
        menu_font = self.load_font(26)
        small_font = self.load_font(14)

        draw.text((42, 70), "dillykindle", font=title_font, fill=0)
        draw.text((42, 120), "for when diya wants to read", font=subtitle_font, fill=0)

        y_positions = [260, 320, 380]

        for i, option in enumerate(HOME_OPTIONS):
            text = f"> {option} <" if i == self.home_index else option
            draw.text((70, y_positions[i]), text, font=menu_font, fill=0)

        draw.text((42, 730), "w/s move  e select  q back  x exit", font=small_font, fill=0)

        return image

    def render_read(self):
        image = Image.new("1", (PORTRAIT_WIDTH, PORTRAIT_HEIGHT), 255)
        draw = ImageDraw.Draw(image)

        title_font = self.load_font(30)
        item_font = self.load_font(18)
        small_font = self.load_font(13)

        draw.text((42, 54), "read", font=title_font, fill=0)

        books = get_books()

        if not books:
            draw.text((42, 180), "no books imported yet", font=item_font, fill=0)
            draw.text((42, 220), "press q to go home", font=item_font, fill=0)
            return image

        max_visible = 8
        start = max(0, self.list_index - max_visible // 2)
        end = min(len(books), start + max_visible)

        if end - start < max_visible:
            start = max(0, end - max_visible)

        y = 140
        for i in range(start, end):
            book = books[i]
            selected = i == self.list_index

            title = self.clip_text(book["title"], 28)
            line = f"> {title}" if selected else title
            draw.text((42, y), line, font=item_font, fill=0)

            saved_page = progress_manager.get_page(book["id"]) + 1
            draw.text((62, y + 24), f"page {saved_page}", font=small_font, fill=0)

            y += 72

        draw.text((42, 740), "select = open book", font=small_font, fill=0)

        return image

    def render_bookmarks(self):
        image = Image.new("1", (PORTRAIT_WIDTH, PORTRAIT_HEIGHT), 255)
        draw = ImageDraw.Draw(image)

        title_font = self.load_font(30)
        item_font = self.load_font(17)
        small_font = self.load_font(13)

        draw.text((42, 54), "bookmarks", font=title_font, fill=0)

        bookmarks = self.get_bookmarks()

        if not bookmarks:
            draw.text((42, 180), "no bookmarks yet", font=item_font, fill=0)
            draw.text((42, 220), "open a book and press select", font=item_font, fill=0)
            return image

        max_visible = 8
        start = max(0, self.list_index - max_visible // 2)
        end = min(len(bookmarks), start + max_visible)

        if end - start < max_visible:
            start = max(0, end - max_visible)

        y = 132
        for i in range(start, end):
            bookmark = bookmarks[i]
            selected = i == self.list_index

            title = self.clip_text(bookmark["book_title"], 22)
            line = f"> {title}" if selected else title
            draw.text((42, y), line, font=item_font, fill=0)
            draw.text((62, y + 24), f"page {bookmark['page'] + 1}", font=small_font, fill=0)

            y += 72

        draw.text((42, 740), "select = open bookmark", font=small_font, fill=0)

        return image

    def render_edit_placeholder(self):
        image = Image.new("1", (PORTRAIT_WIDTH, PORTRAIT_HEIGHT), 255)
        draw = ImageDraw.Draw(image)

        title_font = self.load_font(28)
        body_font = self.load_font(18)
        small_font = self.load_font(13)

        draw.text((42, 70), "edit books", font=title_font, fill=0)
        draw.text((42, 180), "not built in e-paper mode yet", font=body_font, fill=0)
        draw.text((42, 220), "for now use the desktop version", font=body_font, fill=0)
        draw.text((42, 740), "press q to go home", font=small_font, fill=0)

        return image

    def render_reader(self):
        image = Image.new("1", (PORTRAIT_WIDTH, PORTRAIT_HEIGHT), 255)
        draw = ImageDraw.Draw(image)

        if self.current_book_id is None:
            draw.text((42, 100), "no book open", font=self.load_font(22), fill=0)
            return image

        content_x = 24
        content_y = 18
        content_width = 432
        content_height = 720

        page_image = self.get_rendered_page(
            self.current_book_id,
            self.current_page,
            content_width,
            content_height
        )

        paste_x = content_x + (content_width - page_image.width) // 2
        paste_y = content_y + (content_height - page_image.height) // 2

        image.paste(page_image, (paste_x, paste_y))

        small_font = self.load_font(13)

        total_pages = self.get_total_pages(self.current_book_id)
        footer = f"{self.current_page + 1} / {total_pages}"
        draw.text((24, 760), footer, font=small_font, fill=0)

        if self.reader_message:
            draw.text((350, 760), self.reader_message, font=small_font, fill=0)

        return image

    def enter_reader(self, book_id, page):
        total_pages = self.get_total_pages(book_id)
        if total_pages <= 0:
            return

        self.current_book_id = book_id
        self.current_page = max(0, min(page, total_pages - 1))
        self.reader_message = ""

        self.save_progress(self.current_book_id, self.current_page)

        self.screen = "reader"
        self.show_current("full")

    def handle_up(self):
        if self.screen == "home":
            self.home_index = (self.home_index - 1) % len(HOME_OPTIONS)
            self.show_current("partial")
            return

        if self.screen == "read":
            books = get_books()
            if books:
                self.list_index = (self.list_index - 1) % len(books)
                self.show_current("partial")
            return

        if self.screen == "bookmarks":
            bookmarks = self.get_bookmarks()
            if bookmarks:
                self.list_index = (self.list_index - 1) % len(bookmarks)
                self.show_current("partial")
            return

        if self.screen == "reader":
            if self.current_page > 0:
                self.current_page -= 1
                self.reader_message = ""
                self.save_progress(self.current_book_id, self.current_page)
                self.show_current("partial")
            return

    def handle_down(self):
        if self.screen == "home":
            self.home_index = (self.home_index + 1) % len(HOME_OPTIONS)
            self.show_current("partial")
            return

        if self.screen == "read":
            books = get_books()
            if books:
                self.list_index = (self.list_index + 1) % len(books)
                self.show_current("partial")
            return

        if self.screen == "bookmarks":
            bookmarks = self.get_bookmarks()
            if bookmarks:
                self.list_index = (self.list_index + 1) % len(bookmarks)
                self.show_current("partial")
            return

        if self.screen == "reader":
            total_pages = self.get_total_pages(self.current_book_id)
            if self.current_page < total_pages - 1:
                self.current_page += 1
                self.reader_message = ""
                self.save_progress(self.current_book_id, self.current_page)
                self.show_current("partial")
            return

    def handle_select(self):
        if self.screen == "home":
            choice = HOME_OPTIONS[self.home_index]

            if choice == "read":
                self.screen = "read"
                self.list_index = 0
                self.show_current("full")
                return

            if choice == "bookmarks":
                self.screen = "bookmarks"
                self.list_index = 0
                self.show_current("full")
                return

            if choice == "edit books":
                self.screen = "edit books"
                self.show_current("full")
                return

        if self.screen == "read":
            books = get_books()
            if books:
                book = books[self.list_index]
                start_page = progress_manager.get_page(book["id"])
                self.enter_reader(book["id"], start_page)
            return

        if self.screen == "bookmarks":
            bookmarks = self.get_bookmarks()
            if bookmarks:
                bookmark = bookmarks[self.list_index]
                self.enter_reader(bookmark["book_id"], bookmark["page"])
            return

        if self.screen == "reader":
            self.add_bookmark(self.current_book_id, self.current_page)
            self.reader_message = "marked"
            self.show_current("partial")
            return

    def handle_back(self):
        if self.screen == "home":
            return

        if self.screen == "reader":
            self.reader_message = ""
            self.screen = "read"
            self.show_current("full")
            return

        self.screen = "home"
        self.show_current("full")

    def run(self):
        self.show_current("startup")

        try:
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

        finally:
            self.display.sleep()


if __name__ == "__main__":
    app = EPaperApp()
    app.run()
