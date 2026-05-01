import customtkinter as ctk

from app.core.bookmark_manager import get_bookmarks, remove_bookmark
from app.core.book_manager import get_book
from app.ui.style import BG, SURFACE, BORDER, TEXT, TEXT_MUTED, TextButton, title_font, body_font, bold_font


class BookmarksScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=0, fg_color=BG)
        self.controller = controller

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
            text="bookmarks",
            text_color=TEXT,
            font=title_font(30)
        )
        title.pack(pady=(34, 20))

        self.list_frame = ctk.CTkScrollableFrame(
            self,
            width=420,
            height=540,
            fg_color=BG,
            border_width=0
        )
        self.list_frame.pack(pady=10, fill="both", expand=True, padx=28)

        self.refresh_bookmarks()

    def refresh_bookmarks(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        bookmarks = list(reversed(get_bookmarks()))

        if not bookmarks:
            empty_label = ctk.CTkLabel(
                self.list_frame,
                text="no bookmarks yet\n\nopen a book and press mark",
                text_color=TEXT_MUTED,
                font=body_font(15),
                justify="center"
            )
            empty_label.pack(pady=80)
            return

        for bookmark in bookmarks:
            book = get_book(bookmark["book_id"])

            if book is None:
                continue

            row = ctk.CTkFrame(
                self.list_frame,
                fg_color=SURFACE,
                corner_radius=6,
                border_width=1,
                border_color=BORDER
            )
            row.pack(fill="x", pady=7, padx=3)

            text_frame = ctk.CTkFrame(row, fg_color="transparent")
            text_frame.pack(fill="x", padx=14, pady=(12, 6))

            title = ctk.CTkLabel(
                text_frame,
                text=bookmark["book_title"],
                text_color=TEXT,
                anchor="w",
                font=bold_font(15)
            )
            title.pack(fill="x")

            page_label = ctk.CTkLabel(
                text_frame,
                text=f"page {bookmark['page'] + 1}",
                text_color=TEXT_MUTED,
                anchor="w",
                font=body_font(12)
            )
            page_label.pack(fill="x", pady=(4, 0))

            action_frame = ctk.CTkFrame(row, fg_color="transparent")
            action_frame.pack(fill="x", padx=14, pady=(2, 12))

            open_button = TextButton(
                action_frame,
                text="open",
                command=lambda b=bookmark: self.open_bookmark(b),
                size=13
            )
            open_button.pack(side="left")

            remove_button = TextButton(
                action_frame,
                text="remove",
                command=lambda bookmark_id=bookmark["id"]: self.delete_bookmark(bookmark_id),
                size=13,
                danger=True
            )
            remove_button.pack(side="right")

    def open_bookmark(self, bookmark):
        self.controller.show_reader(
            bookmark["book_id"],
            start_page=bookmark["page"]
        )

    def delete_bookmark(self, bookmark_id):
        remove_bookmark(bookmark_id)
        self.refresh_bookmarks()
