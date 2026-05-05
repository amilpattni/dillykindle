import inspect
from pathlib import Path
from textwrap import shorten

import fitz
from PIL import Image, ImageDraw, ImageFont, ImageOps

from app.core.book_manager import get_books, get_book, add_book, remove_book
from app.core import bookmark_manager, progress_manager
from app.epaper.display import EPaperDisplay


PORTRAIT_WIDTH = 480
PORTRAIT_HEIGHT = 800

HOME_OPTIONS = ["read", "edit books", "bookmarks"]

MENU_PARTIAL_LIMIT = 40
READER_PARTIAL_LIMIT = 10


class EPaperApp:
    def __init__(self):
        self.display = EPaperDisplay()

        self.screen = "home"

        self.home_index = 0
        self.list_index = 0
        self.action_index = 0

        self.current_book_id = None
        self.current_page = 0
        self.reader_message = ""

        self.read_focus = "list"
        self.bookmark_focus = "list"
        self.edit_focus = "list"
        self.edit_index = 0
        self.edit_action_index = 0
        self.usb_index = 0
        self.usb_pdfs = []
        self.edit_status = ""

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
        text = str(text).strip()

        if len(text) <= width:
            return text

        if width <= 8:
            return text[:width]

        front_count = max(1, (width - 3) // 2)
        back_count = max(1, width - 3 - front_count)

        return text[:front_count] + "..." + text[-back_count:]

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

    def remove_bookmark(self, bookmark_id):
        func = getattr(bookmark_manager, "remove_bookmark", None)

        if func is not None:
            func(bookmark_id)

    def get_bookmarks(self):
        if not hasattr(bookmark_manager, "get_bookmarks"):
            return []

        bookmarks = []

        for bookmark in reversed(bookmark_manager.get_bookmarks()):
            book = get_book(bookmark["book_id"])
            if book is not None:
                bookmarks.append(bookmark)

        return bookmarks

    def get_recent_bookmark_for_book(self, book_id):
        if not hasattr(bookmark_manager, "get_bookmarks"):
            return None

        for bookmark in reversed(bookmark_manager.get_bookmarks()):
            if bookmark["book_id"] == book_id:
                return bookmark

        return None

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
            return Image.new("1", (max_width, max_height), 255)

        doc = fitz.open(book["path"])
        page = doc.load_page(page_index)
        rect = page.rect

        margin_x = rect.width * 0.05
        margin_y = rect.height * 0.035

        crop_rect = fitz.Rect(
            rect.x0 + margin_x,
            rect.y0 + margin_y,
            rect.x1 - margin_x,
            rect.y1 - margin_y,
        )

        zoom = min(max_width / crop_rect.width, max_height / crop_rect.height) * 1.9
        matrix = fitz.Matrix(zoom, zoom)

        pix = page.get_pixmap(
            matrix=matrix,
            colorspace=fitz.csGRAY,
            alpha=False,
            clip=crop_rect,
        )

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

        if self.screen == "read_actions":
            return self.render_read_actions()

        if self.screen == "bookmarks":
            return self.render_bookmarks()

        if self.screen == "bookmark_actions":
            return self.render_bookmark_actions()

        if self.screen == "reader":
            return self.render_reader()

        if self.screen == "edit books":
            return self.render_edit_books()

        if self.screen == "usb_import":
            return self.render_usb_import()

        return self.render_edit_placeholder()

    def get_home_art_path(self):
        assets_dir = Path(__file__).resolve().parents[1] / "assets"

        possible_images = [
            assets_dir / "home_screen.png",
            assets_dir / "home_image.png",
            assets_dir / "home_image.jpg",
            assets_dir / "home_image.jpeg",
        ]

        for image_path in possible_images:
            if image_path.exists():
                return image_path

        return None

    def paste_home_art(self, image, draw):
        image_bottom = 690
        home_image_path = self.get_home_art_path()

        if home_image_path is not None:
            plush = Image.open(home_image_path).convert("L")
            plush = ImageOps.autocontrast(plush)
            plush.thumbnail((250, 220))
            plush = plush.point(lambda p: 0 if p < 190 else 255, mode="1")

            x = (PORTRAIT_WIDTH - plush.width) // 2
            y = 500
            image.paste(plush, (x, y))
            image_bottom = y + plush.height

        love_font = self.load_font(13)
        love_text = "i <3 u"
        text_box = draw.textbbox((0, 0), love_text, font=love_font)
        text_width = text_box[2] - text_box[0]
        text_x = (PORTRAIT_WIDTH - text_width) // 2
        text_y = image_bottom + 10
        draw.text((text_x, text_y), love_text, font=love_font, fill=0)

    def render_sleep_screen(self):
        image = Image.new("1", (PORTRAIT_WIDTH, PORTRAIT_HEIGHT), 255)
        draw = ImageDraw.Draw(image)

        z_big_font = self.load_font(28)
        z_mid_font = self.load_font(22)
        z_small_font = self.load_font(17)

        draw.text((132, 368), "Z", font=z_big_font, fill=0)
        draw.text((160, 418), "z", font=z_mid_font, fill=0)
        draw.text((192, 451), "z", font=z_small_font, fill=0)

        self.paste_home_art(image, draw)
        return image

    def render_home(self):
        image = Image.new("1", (PORTRAIT_WIDTH, PORTRAIT_HEIGHT), 255)
        draw = ImageDraw.Draw(image)

        title_font = self.load_font(34)
        subtitle_font = self.load_font(16)
        menu_font = self.load_font(22)

        draw.text((42, 70), "dillykindle", font=title_font, fill=0)
        draw.text((42, 120), "for when diya wants to read", font=subtitle_font, fill=0)

        y_positions = [250, 302, 354]

        for i, option in enumerate(HOME_OPTIONS):
            menu_text = f"> {option} <" if i == self.home_index else option
            text_box = draw.textbbox((0, 0), menu_text, font=menu_font)
            text_width = text_box[2] - text_box[0]
            text_x = (PORTRAIT_WIDTH - text_width) // 2
            draw.text((text_x, y_positions[i]), menu_text, font=menu_font, fill=0)

        self.paste_home_art(image, draw)

        return image

    def render_read(self):
        image = Image.new("1", (PORTRAIT_WIDTH, PORTRAIT_HEIGHT), 255)
        draw = ImageDraw.Draw(image)

        title_font = self.load_font(30)
        item_font = self.load_font(17)
        small_font = self.load_font(12)
        action_font = self.load_font(14)

        draw.text((42, 54), "read", font=title_font, fill=0)

        books = get_books()

        if not books:
            draw.text((42, 180), "no books imported yet", font=item_font, fill=0)
            draw.text((42, 220), "press q to go home", font=item_font, fill=0)
            return image

        max_visible = 7
        start = max(0, self.list_index - max_visible // 2)
        end = min(len(books), start + max_visible)

        if end - start < max_visible:
            start = max(0, end - max_visible)

        y = 118

        for i in range(start, end):
            book = books[i]
            selected = i == self.list_index and self.read_focus == "list"

            title = self.clip_text(book["title"], 34)
            line = f"> {title}" if selected else title

            draw.text((42, y), line, font=item_font, fill=0)

            saved_page = progress_manager.get_page(book["id"]) + 1
            recent = self.get_recent_bookmark_for_book(book["id"])

            if recent is None:
                subline = f"last read: page {saved_page}"
            else:
                subline = f"last read: {saved_page} | recent mark: {recent['page'] + 1}"

            draw.text((62, y + 23), subline, font=small_font, fill=0)

            y += 68

        book = books[self.list_index]
        continue_page = progress_manager.get_page(book["id"]) + 1

        continue_label = f"continue reading pg {continue_page}"
        start_label = "start book"

        if self.read_focus == "actions" and self.action_index == 0:
            continue_label = f"> {continue_label} <"

        if self.read_focus == "actions" and self.action_index == 1:
            start_label = f"> {start_label} <"

        draw.line((28, 688, 452, 688), fill=0, width=1)
        draw.text((40, 708), continue_label, font=action_font, fill=0)
        draw.text((40, 736), start_label, font=action_font, fill=0)

        if self.read_focus == "list":
            draw.text((300, 736), "select book", font=small_font, fill=0)
        else:
            draw.text((300, 736), "select action", font=small_font, fill=0)

        return image

    def get_read_actions(self):
        books = get_books()

        if not books:
            return []

        book = books[self.list_index]
        book_id = book["id"]

        actions = [
            {
                "label": f"continue page {progress_manager.get_page(book_id) + 1}",
                "page": progress_manager.get_page(book_id),
            }
        ]

        recent = self.get_recent_bookmark_for_book(book_id)

        if recent is not None:
            actions.append(
                {
                    "label": f"recent bookmark page {recent['page'] + 1}",
                    "page": recent["page"],
                }
            )

        actions.append(
            {
                "label": "start from beginning",
                "page": 0,
            }
        )

        return actions

    def render_read_actions(self):
        image = Image.new("1", (PORTRAIT_WIDTH, PORTRAIT_HEIGHT), 255)
        draw = ImageDraw.Draw(image)

        title_font = self.load_font(26)
        item_font = self.load_font(20)
        small_font = self.load_font(13)

        books = get_books()

        if not books:
            draw.text((42, 120), "no book selected", font=item_font, fill=0)
            return image

        book = books[self.list_index]

        draw.text((42, 54), "open book", font=title_font, fill=0)
        draw.text((42, 110), self.clip_text(book["title"], 36), font=small_font, fill=0)

        actions = self.get_read_actions()

        y = 210

        for i, action in enumerate(actions):
            text = f"> {action['label']}" if i == self.action_index else action["label"]
            draw.text((60, y), text, font=item_font, fill=0)
            y += 60

        draw.text((42, 740), "select opens | back returns", font=small_font, fill=0)

        return image

    def render_bookmarks(self):
        image = Image.new("1", (PORTRAIT_WIDTH, PORTRAIT_HEIGHT), 255)
        draw = ImageDraw.Draw(image)

        title_font = self.load_font(30)
        item_font = self.load_font(16)
        small_font = self.load_font(12)
        action_font = self.load_font(14)

        draw.text((42, 54), "bookmarks", font=title_font, fill=0)

        bookmarks = self.get_bookmarks()

        if not bookmarks:
            draw.text((42, 180), "no bookmarks yet", font=item_font, fill=0)
            draw.text((42, 220), "open a book and press select", font=item_font, fill=0)
            return image

        max_visible = 7
        start = max(0, self.list_index - max_visible // 2)
        end = min(len(bookmarks), start + max_visible)

        if end - start < max_visible:
            start = max(0, end - max_visible)

        y = 118

        for i in range(start, end):
            bookmark = bookmarks[i]
            selected = i == self.list_index and self.bookmark_focus == "list"

            title = self.clip_text(bookmark["book_title"], 36)
            line = f"> {title}" if selected else title

            draw.text((42, y), line, font=item_font, fill=0)
            draw.text((62, y + 23), f"page {bookmark['page'] + 1}", font=small_font, fill=0)

            y += 68

        open_label = "open bookmark"
        delete_label = "delete bookmark"

        if self.bookmark_focus == "actions" and self.action_index == 0:
            open_label = f"> {open_label} <"

        if self.bookmark_focus == "actions" and self.action_index == 1:
            delete_label = f"> {delete_label} <"

        draw.line((28, 688, 452, 688), fill=0, width=1)
        draw.text((40, 708), open_label, font=action_font, fill=0)
        draw.text((40, 736), delete_label, font=action_font, fill=0)

        if self.bookmark_focus == "list":
            draw.text((300, 736), "select mark", font=small_font, fill=0)
        else:
            draw.text((300, 736), "select action", font=small_font, fill=0)

        return image

    def get_bookmark_actions(self):
        return [
            {
                "label": "open bookmark",
                "type": "open",
            },
            {
                "label": "delete bookmark",
                "type": "delete",
            },
        ]

    def render_bookmark_actions(self):
        image = Image.new("1", (PORTRAIT_WIDTH, PORTRAIT_HEIGHT), 255)
        draw = ImageDraw.Draw(image)

        title_font = self.load_font(26)
        item_font = self.load_font(20)
        small_font = self.load_font(13)

        bookmarks = self.get_bookmarks()

        if not bookmarks:
            draw.text((42, 120), "no bookmark selected", font=item_font, fill=0)
            return image

        bookmark = bookmarks[self.list_index]

        draw.text((42, 54), "bookmark", font=title_font, fill=0)
        draw.text((42, 110), self.clip_text(bookmark["book_title"], 36), font=small_font, fill=0)
        draw.text((42, 135), f"page {bookmark['page'] + 1}", font=small_font, fill=0)

        actions = self.get_bookmark_actions()

        y = 230

        for i, action in enumerate(actions):
            text = f"> {action['label']}" if i == self.action_index else action["label"]
            draw.text((60, y), text, font=item_font, fill=0)
            y += 60

        draw.text((42, 740), "select acts | back returns", font=small_font, fill=0)

        return image

    def get_usb_roots(self):
        username = Path.home().name

        roots = [
            Path("/media") / username,
            Path("/run/media") / username,
        ]

        usb_roots = []

        for root in roots:
            if not root.exists():
                continue

            for item in sorted(root.iterdir()):
                if item.is_dir():
                    usb_roots.append(item)

        return usb_roots

    def get_usb_book_pdfs(self):
        pdfs = []

        for usb_root in self.get_usb_roots():
            book_folder = usb_root / "e-reader_books"

            if not book_folder.exists() or not book_folder.is_dir():
                continue

            for file in sorted(book_folder.glob("*.pdf")):
                pdfs.append(file)

            for file in sorted(book_folder.glob("*.PDF")):
                pdfs.append(file)

        unique = []
        seen = set()

        for pdf in pdfs:
            resolved = str(pdf.resolve())
            if resolved not in seen:
                unique.append(pdf)
                seen.add(resolved)

        return unique

    def get_edit_items(self):
        items = [
            {
                "type": "add",
                "label": "add new book",
            }
        ]

        for book in get_books():
            items.append(
                {
                    "type": "book",
                    "label": book["title"],
                    "book": book,
                }
            )

        return items

    def render_edit_books(self):
        image = Image.new("1", (PORTRAIT_WIDTH, PORTRAIT_HEIGHT), 255)
        draw = ImageDraw.Draw(image)

        title_font = self.load_font(30)
        item_font = self.load_font(17)
        small_font = self.load_font(12)
        action_font = self.load_font(14)

        draw.text((42, 54), "edit books", font=title_font, fill=0)

        items = self.get_edit_items()

        if self.edit_index >= len(items):
            self.edit_index = max(0, len(items) - 1)

        max_visible = 7
        start = max(0, self.edit_index - max_visible // 2)
        end = min(len(items), start + max_visible)

        if end - start < max_visible:
            start = max(0, end - max_visible)

        y = 118

        for i in range(start, end):
            item = items[i]
            selected = i == self.edit_index and self.edit_focus == "list"

            label = self.clip_text(item["label"], 34)
            line = f"> {label}" if selected else label

            draw.text((42, y), line, font=item_font, fill=0)

            if item["type"] == "add":
                draw.text((62, y + 23), "from usb/e-reader_books", font=small_font, fill=0)
            else:
                draw.text((62, y + 23), "imported book", font=small_font, fill=0)

            y += 68

        selected_item = items[self.edit_index]

        draw.line((28, 688, 452, 688), fill=0, width=1)

        if selected_item["type"] == "add":
            action = "add from usb"
            if self.edit_focus == "actions":
                action = f"> {action} <"

            draw.text((40, 718), action, font=action_font, fill=0)

        else:
            action = "remove book"
            if self.edit_focus == "actions":
                action = f"> {action} <"

            draw.text((40, 718), action, font=action_font, fill=0)

        if self.edit_status:
            draw.text((40, 760), self.clip_text(self.edit_status, 42), font=small_font, fill=0)
        elif self.edit_focus == "list":
            draw.text((300, 736), "select item", font=small_font, fill=0)
        else:
            draw.text((300, 736), "select action", font=small_font, fill=0)

        return image

    def render_usb_import(self):
        image = Image.new("1", (PORTRAIT_WIDTH, PORTRAIT_HEIGHT), 255)
        draw = ImageDraw.Draw(image)

        title_font = self.load_font(28)
        item_font = self.load_font(16)
        small_font = self.load_font(12)

        draw.text((42, 54), "add book", font=title_font, fill=0)
        draw.text((42, 96), "usb folder: e-reader_books", font=small_font, fill=0)

        if not self.usb_pdfs:
            draw.text((42, 180), "no pdfs found", font=item_font, fill=0)
            draw.text((42, 220), "put pdfs in usb/e-reader_books", font=item_font, fill=0)
            draw.text((42, 740), "back returns", font=small_font, fill=0)
            return image

        if self.usb_index >= len(self.usb_pdfs):
            self.usb_index = max(0, len(self.usb_pdfs) - 1)

        max_visible = 8
        start = max(0, self.usb_index - max_visible // 2)
        end = min(len(self.usb_pdfs), start + max_visible)

        if end - start < max_visible:
            start = max(0, end - max_visible)

        y = 136

        for i in range(start, end):
            pdf = self.usb_pdfs[i]
            selected = i == self.usb_index

            label = self.clip_text(pdf.name, 38)
            line = f"> {label}" if selected else label

            draw.text((42, y), line, font=item_font, fill=0)
            y += 58

        draw.line((28, 688, 452, 688), fill=0, width=1)
        draw.text((40, 720), "select imports highlighted pdf", font=small_font, fill=0)
        draw.text((40, 746), "back returns", font=small_font, fill=0)

        return image

    def render_reader(self):
        image = Image.new("1", (PORTRAIT_WIDTH, PORTRAIT_HEIGHT), 255)
        draw = ImageDraw.Draw(image)

        if self.current_book_id is None:
            draw.text((42, 100), "no book open", font=self.load_font(22), fill=0)
            return image

        content_x = 8
        content_y = 8
        content_width = 464
        content_height = 748

        page_image = self.get_rendered_page(
            self.current_book_id,
            self.current_page,
            content_width,
            content_height,
        )

        paste_x = content_x + (content_width - page_image.width) // 2
        paste_y = content_y + (content_height - page_image.height) // 2

        image.paste(page_image, (paste_x, paste_y))

        small_font = self.load_font(13)

        total_pages = self.get_total_pages(self.current_book_id)
        footer = f"{self.current_page + 1} / {total_pages}"
        draw.text((18, 770), footer, font=small_font, fill=0)

        if self.reader_message:
            draw.text((332, 770), self.reader_message, font=small_font, fill=0)

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
            if not books:
                return

            if self.read_focus == "list":
                self.list_index = (self.list_index - 1) % len(books)
            else:
                self.action_index = (self.action_index - 1) % 2

            self.show_current("partial")
            return

        if self.screen == "bookmarks":
            bookmarks = self.get_bookmarks()
            if not bookmarks:
                return

            if self.bookmark_focus == "list":
                self.list_index = (self.list_index - 1) % len(bookmarks)
            else:
                self.action_index = (self.action_index - 1) % 2

            self.show_current("partial")
            return

        if self.screen == "edit books":
            items = self.get_edit_items()
            if not items:
                return

            if self.edit_focus == "list":
                self.edit_index = (self.edit_index - 1) % len(items)

            self.show_current("partial")
            return

        if self.screen == "usb_import":
            if self.usb_pdfs:
                self.usb_index = (self.usb_index - 1) % len(self.usb_pdfs)
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
            if not books:
                return

            if self.read_focus == "list":
                self.list_index = (self.list_index + 1) % len(books)
            else:
                self.action_index = (self.action_index + 1) % 2

            self.show_current("partial")
            return

        if self.screen == "bookmarks":
            bookmarks = self.get_bookmarks()
            if not bookmarks:
                return

            if self.bookmark_focus == "list":
                self.list_index = (self.list_index + 1) % len(bookmarks)
            else:
                self.action_index = (self.action_index + 1) % 2

            self.show_current("partial")
            return

        if self.screen == "edit books":
            items = self.get_edit_items()
            if not items:
                return

            if self.edit_focus == "list":
                self.edit_index = (self.edit_index + 1) % len(items)

            self.show_current("partial")
            return

        if self.screen == "usb_import":
            if self.usb_pdfs:
                self.usb_index = (self.usb_index + 1) % len(self.usb_pdfs)
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
                self.action_index = 0
                self.read_focus = "list"
                self.show_current("partial")
                return

            if choice == "bookmarks":
                self.screen = "bookmarks"
                self.list_index = 0
                self.action_index = 0
                self.bookmark_focus = "list"
                self.show_current("partial")
                return

            if choice == "edit books":
                self.screen = "edit books"
                self.edit_index = 0
                self.edit_focus = "list"
                self.edit_status = ""
                self.show_current("partial")
                return

        if self.screen == "read":
            books = get_books()
            if not books:
                return

            if self.read_focus == "list":
                self.read_focus = "actions"
                self.action_index = 0
                self.show_current("partial")
                return

            book = books[self.list_index]

            if self.action_index == 0:
                page = progress_manager.get_page(book["id"])
            else:
                page = 0

            self.enter_reader(book["id"], page)
            return

        if self.screen == "bookmarks":
            bookmarks = self.get_bookmarks()
            if not bookmarks:
                return

            if self.bookmark_focus == "list":
                self.bookmark_focus = "actions"
                self.action_index = 0
                self.show_current("partial")
                return

            bookmark = bookmarks[self.list_index]

            if self.action_index == 0:
                self.enter_reader(bookmark["book_id"], bookmark["page"])
                return

            if self.action_index == 1:
                self.remove_bookmark(bookmark["id"])
                self.bookmark_focus = "list"
                self.action_index = 0

                updated = self.get_bookmarks()
                if self.list_index >= len(updated):
                    self.list_index = max(0, len(updated) - 1)

                self.show_current("partial")
                return

        if self.screen == "edit books":
            items = self.get_edit_items()
            if not items:
                return

            item = items[self.edit_index]

            if self.edit_focus == "list":
                if item["type"] == "add":
                    self.usb_pdfs = self.get_usb_book_pdfs()
                    self.usb_index = 0
                    self.screen = "usb_import"
                    self.edit_focus = "list"
                    self.show_current("partial")
                    return

                if item["type"] == "book":
                    self.edit_focus = "actions"
                    self.show_current("partial")
                    return

            if item["type"] == "book":
                title = item["book"]["title"]
                remove_book(item["book"]["id"], delete_file=True)
                self.edit_status = f"removed: {title}"
                self.edit_focus = "list"

                updated_items = self.get_edit_items()
                if self.edit_index >= len(updated_items):
                    self.edit_index = max(0, len(updated_items) - 1)

                self.show_current("partial")
                return

        if self.screen == "usb_import":
            if not self.usb_pdfs:
                return

            pdf = self.usb_pdfs[self.usb_index]

            try:
                book = add_book(pdf)
                self.edit_status = f"added: {book['title']}"
            except Exception as error:
                self.edit_status = f"add failed: {error}"

            self.screen = "edit books"
            self.edit_focus = "list"
            self.edit_index = 0
            self.show_current("partial")
            return

        if self.screen == "reader":
            self.add_bookmark(self.current_book_id, self.current_page)
            self.reader_message = "bookmarked"
            self.show_current("partial")
            return

    def handle_back(self):
        if self.screen == "home":
            return

        if self.screen == "read":
            if self.read_focus == "actions":
                self.read_focus = "list"
                self.action_index = 0
                self.show_current("partial")
                return

            self.screen = "home"
            self.show_current("partial")
            return

        if self.screen == "bookmarks":
            if self.bookmark_focus == "actions":
                self.bookmark_focus = "list"
                self.action_index = 0
                self.show_current("partial")
                return

            self.screen = "home"
            self.show_current("partial")
            return

        if self.screen == "edit books":
            if self.edit_focus == "actions":
                self.edit_focus = "list"
                self.show_current("partial")
                return

            self.screen = "home"
            self.show_current("partial")
            return

        if self.screen == "usb_import":
            self.screen = "edit books"
            self.edit_focus = "list"
            self.show_current("partial")
            return

        if self.screen == "reader":
            self.reader_message = ""
            self.screen = "read"
            self.read_focus = "list"
            self.show_current("full")
            return

        self.screen = "home"
        self.show_current("partial")

    def run(self):
        self.show_current("startup")

        try:
            while True:
                command = input("Command (w/s/e/q/f/x): ").strip().lower()

                if command == "w":
                    self.handle_up()
                elif command == "s":
                    self.handle_down()
                elif command == "e":
                    self.handle_select()
                elif command == "q":
                    self.handle_back()
                elif command == "f":
                    self.show_current("full")
                elif command == "x":
                    sleep_image = self.render_sleep_screen()
                    self.display.full_refresh(sleep_image)
                    break

        finally:
            self.display.sleep()


if __name__ == "__main__":
    app = EPaperApp()
    app.run()
