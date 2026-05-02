import customtkinter as ctk

from app.core.book_manager import get_books
from app.core.bookmark_manager import get_bookmarks
from app.core.progress_manager import get_page
from app.ui.style import BG, SURFACE, SURFACE_ALT, BORDER, TEXT, TEXT_MUTED, TextButton, title_font, body_font, bold_font


class StartBookScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=0, fg_color=BG)
        self.controller = controller
        self.books = get_books()
        self.selected_book_index = 0
        self.selected_action_index = 0
        self.mode = "books"

        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(fill="x", padx=24, pady=(24, 0))

        TextButton(
            nav_frame,
            text="home",
            command=controller.show_home,
            size=14
        ).pack(side="left")

        ctk.CTkLabel(
            self,
            text="read",
            text_color=TEXT,
            font=title_font(30)
        ).pack(pady=(34, 20))

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

        self.refresh()

    def refresh(self):
        self.books = get_books()

        if self.selected_book_index >= len(self.books):
            self.selected_book_index = max(0, len(self.books) - 1)

        self.render_books()
        self.render_actions()

    def render_books(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        if not self.books:
            ctk.CTkLabel(
                self.list_frame,
                text="no books imported yet\n\nuse edit books first",
                text_color=TEXT_MUTED,
                font=body_font(15),
                justify="center"
            ).pack(pady=80)
            return

        for index, book in enumerate(self.books):
            selected = self.mode == "books" and index == self.selected_book_index

            row = ctk.CTkFrame(
                self.list_frame,
                fg_color=SURFACE_ALT if selected else SURFACE,
                corner_radius=6,
                border_width=1,
                border_color=TEXT if selected else BORDER
            )
            row.pack(fill="x", pady=7, padx=3)

            text_frame = ctk.CTkFrame(row, fg_color="transparent")
            text_frame.pack(fill="both", expand=True, padx=14, pady=12)

            prefix = "> " if selected else ""

            ctk.CTkLabel(
                text_frame,
                text=f"{prefix}{book['title']}",
                text_color=TEXT if selected else TEXT_MUTED,
                anchor="w",
                font=bold_font(15)
            ).pack(fill="x")

            furthest = self.get_furthest_bookmark_page(book["id"])
            last_page = get_page(book["id"])

            if furthest is None:
                subtitle = f"last read: page {last_page + 1} | no bookmarks"
            else:
                subtitle = f"last read: page {last_page + 1} | furthest mark: page {furthest + 1}"

            ctk.CTkLabel(
                text_frame,
                text=subtitle,
                text_color=TEXT_MUTED,
                anchor="w",
                font=body_font(11)
            ).pack(fill="x", pady=(4, 0))

            row.bind("<Button-1>", lambda event, i=index: self.mouse_select_book(i))
            text_frame.bind("<Button-1>", lambda event, i=index: self.mouse_select_book(i))

    def render_actions(self):
        for widget in self.action_frame.winfo_children():
            widget.destroy()

        if not self.books:
            ctk.CTkLabel(
                self.action_frame,
                text="no books available",
                text_color=TEXT_MUTED,
                font=body_font(12)
            ).pack(pady=14)
            return

        book = self.books[self.selected_book_index]

        title_text = book["title"] if self.mode == "actions" else "select a book"

        ctk.CTkLabel(
            self.action_frame,
            text=title_text,
            text_color=TEXT if self.mode == "actions" else TEXT_MUTED,
            font=body_font(12),
            justify="center"
        ).pack(pady=(12, 6))

        row = ctk.CTkFrame(self.action_frame, fg_color="transparent")
        row.pack(pady=(4, 12))

        actions = self.get_actions_for_book(book)

        for index, action in enumerate(actions):
            selected = self.mode == "actions" and index == self.selected_action_index
            label = f"> {action['label']} <" if selected else action["label"]

            TextButton(
                row,
                text=label,
                command=action["command"],
                size=12,
                color=TEXT if selected else TEXT_MUTED
            ).pack(side="left", padx=10)

    def get_actions_for_book(self, book):
        actions = [
            {
                "label": "start",
                "command": lambda: self.controller.show_reader(book["id"], start_page=0)
            }
        ]

        furthest = self.get_furthest_bookmark_page(book["id"])

        if furthest is not None:
            actions.append(
                {
                    "label": "furthest mark",
                    "command": lambda page=furthest: self.controller.show_reader(book["id"], start_page=page)
                }
            )

        return actions

    def get_furthest_bookmark_page(self, book_id):
        pages = [
            bookmark["page"]
            for bookmark in get_bookmarks()
            if bookmark["book_id"] == book_id
        ]

        if not pages:
            return None

        return max(pages)

    def mouse_select_book(self, index):
        self.selected_book_index = index
        self.selected_action_index = 0
        self.mode = "actions"
        self.refresh()

    def handle_up(self):
        if not self.books:
            return

        if self.mode == "books":
            self.selected_book_index = (self.selected_book_index - 1) % len(self.books)
        else:
            actions = self.get_actions_for_book(self.books[self.selected_book_index])
            self.selected_action_index = (self.selected_action_index - 1) % len(actions)

        self.refresh()

    def handle_down(self):
        if not self.books:
            return

        if self.mode == "books":
            self.selected_book_index = (self.selected_book_index + 1) % len(self.books)
        else:
            actions = self.get_actions_for_book(self.books[self.selected_book_index])
            self.selected_action_index = (self.selected_action_index + 1) % len(actions)

        self.refresh()

    def handle_select(self):
        if not self.books:
            return

        if self.mode == "books":
            self.mode = "actions"
            self.selected_action_index = 0
            self.refresh()
            return

        actions = self.get_actions_for_book(self.books[self.selected_book_index])
        actions[self.selected_action_index]["command"]()

    def handle_back(self):
        if self.mode == "actions":
            self.mode = "books"
            self.refresh()
            return

        self.controller.show_home()
