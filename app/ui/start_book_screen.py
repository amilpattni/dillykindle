import customtkinter as ctk

from app.core.book_manager import get_books
from app.core.bookmark_manager import get_bookmarks
from app.core.progress_manager import get_page
from app.ui.style import BG, SURFACE, SURFACE_ALT, BORDER, TEXT, TEXT_MUTED, TextButton, title_font, body_font, bold_font


class StartBookScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=0, fg_color=BG)
        self.controller = controller
        self.selected_book_id = None
        self.book_rows = {}
        self.selected_book = None
        self.selected_furthest_bookmark_page = None

        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(fill="x", padx=24, pady=(24, 0))

        home_button = TextButton(
            nav_frame,
            text="home",
            command=controller.show_home,
            size=14
        )
        home_button.pack(side="left")

        title = ctk.CTkLabel(
            self,
            text="read",
            text_color=TEXT,
            font=title_font(30)
        )
        title.pack(pady=(34, 20))

        self.list_frame = ctk.CTkScrollableFrame(
            self,
            width=420,
            height=430,
            fg_color=BG,
            border_width=0
        )
        self.list_frame.pack(pady=10, fill="both", expand=True, padx=28)

        self.action_frame = ctk.CTkFrame(
            self,
            fg_color=SURFACE,
            corner_radius=6,
            border_width=1,
            border_color=BORDER
        )
        self.action_frame.pack(fill="x", padx=31, pady=(4, 22))

        self.action_title = ctk.CTkLabel(
            self.action_frame,
            text="select a book",
            text_color=TEXT_MUTED,
            font=body_font(13)
        )
        self.action_title.pack(pady=(12, 6))

        button_row = ctk.CTkFrame(self.action_frame, fg_color="transparent")
        button_row.pack(pady=(4, 12))

        self.start_button = TextButton(
            button_row,
            text="start from beginning",
            command=self.start_from_beginning,
            size=12
        )
        self.start_button.pack(side="left", padx=14)

        self.continue_button = TextButton(
            button_row,
            text="continue from furthest bookmark",
            command=self.continue_from_furthest_bookmark,
            size=12
        )
        self.continue_button.pack(side="left", padx=14)

        self.refresh_books()
        self.update_action_panel()

    def refresh_books(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        self.book_rows = {}
        books = get_books()

        if not books:
            empty_label = ctk.CTkLabel(
                self.list_frame,
                text="no books imported yet\n\nuse edit books first",
                text_color=TEXT_MUTED,
                font=body_font(15),
                justify="center"
            )
            empty_label.pack(pady=80)
            return

        for book in books:
            row = ctk.CTkFrame(
                self.list_frame,
                fg_color=SURFACE,
                corner_radius=6,
                border_width=1,
                border_color=BORDER,
                cursor="hand2"
            )
            row.pack(fill="x", pady=7, padx=3)

            text_frame = ctk.CTkFrame(row, fg_color="transparent", cursor="hand2")
            text_frame.pack(side="left", fill="both", expand=True, padx=14, pady=12)

            title = ctk.CTkLabel(
                text_frame,
                text=book["title"],
                text_color=TEXT,
                anchor="w",
                font=bold_font(15),
                cursor="hand2"
            )
            title.pack(fill="x")

            furthest_bookmark = self.get_furthest_bookmark_page(book["id"])
            last_page = get_page(book["id"])

            if furthest_bookmark is None:
                subtitle_text = f"last read: page {last_page + 1} | no bookmarks"
            else:
                subtitle_text = f"last read: page {last_page + 1} | furthest mark: page {furthest_bookmark + 1}"

            subtitle = ctk.CTkLabel(
                text_frame,
                text=subtitle_text,
                text_color=TEXT_MUTED,
                anchor="w",
                font=body_font(11),
                cursor="hand2"
            )
            subtitle.pack(fill="x", pady=(4, 0))

            row.bind("<Button-1>", lambda event, b=book: self.select_book(b))
            text_frame.bind("<Button-1>", lambda event, b=book: self.select_book(b))
            title.bind("<Button-1>", lambda event, b=book: self.select_book(b))
            subtitle.bind("<Button-1>", lambda event, b=book: self.select_book(b))

            self.book_rows[book["id"]] = {
                "frame": row,
                "book": book
            }

        self.update_selection_styles()

    def select_book(self, book):
        self.selected_book = book
        self.selected_book_id = book["id"]
        self.selected_furthest_bookmark_page = self.get_furthest_bookmark_page(book["id"])
        self.update_selection_styles()
        self.update_action_panel()

    def update_selection_styles(self):
        for book_id, row_data in self.book_rows.items():
            frame = row_data["frame"]

            if book_id == self.selected_book_id:
                frame.configure(fg_color=SURFACE_ALT, border_color=TEXT)
            else:
                frame.configure(fg_color=SURFACE, border_color=BORDER)

    def update_action_panel(self):
        if self.selected_book is None:
            self.action_title.configure(text="select a book")
            self.start_button.configure(text_color=TEXT_MUTED)
            self.continue_button.configure(text_color=TEXT_MUTED)
            return

        if self.selected_furthest_bookmark_page is None:
            self.action_title.configure(
                text=f"{self.selected_book['title']}\nno bookmarks saved"
            )
        else:
            self.action_title.configure(
                text=f"{self.selected_book['title']}\nfurthest bookmark: page {self.selected_furthest_bookmark_page + 1}"
            )

    def get_furthest_bookmark_page(self, book_id):
        pages = [
            bookmark["page"]
            for bookmark in get_bookmarks()
            if bookmark["book_id"] == book_id
        ]

        if not pages:
            return None

        return max(pages)

    def start_from_beginning(self):
        if self.selected_book is None:
            return

        self.controller.show_reader(
            self.selected_book["id"],
            start_page=0
        )

    def continue_from_furthest_bookmark(self):
        if self.selected_book is None:
            return

        if self.selected_furthest_bookmark_page is None:
            return

        self.controller.show_reader(
            self.selected_book["id"],
            start_page=self.selected_furthest_bookmark_page
        )
