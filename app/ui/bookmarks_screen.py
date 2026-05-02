import customtkinter as ctk

from app.core.bookmark_manager import get_bookmarks, remove_bookmark
from app.core.book_manager import get_book
from app.ui.style import BG, SURFACE, SURFACE_ALT, BORDER, TEXT, TEXT_MUTED, TextButton, title_font, body_font, bold_font


class BookmarksScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=0, fg_color=BG)
        self.controller = controller
        self.bookmarks = []
        self.selected_index = 0
        self.selected_action_index = 0
        self.mode = "list"

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
            text="bookmarks",
            text_color=TEXT,
            font=title_font(30)
        ).pack(pady=(34, 20))

        self.list_frame = ctk.CTkScrollableFrame(
            self,
            width=420,
            height=470,
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
        self.bookmarks = [
            bookmark for bookmark in reversed(get_bookmarks())
            if get_book(bookmark["book_id"]) is not None
        ]

        if self.selected_index >= len(self.bookmarks):
            self.selected_index = max(0, len(self.bookmarks) - 1)

        self.render_list()
        self.render_actions()

    def render_list(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        if not self.bookmarks:
            ctk.CTkLabel(
                self.list_frame,
                text="no bookmarks yet\n\nopen a book and press mark",
                text_color=TEXT_MUTED,
                font=body_font(15),
                justify="center"
            ).pack(pady=80)
            return

        for index, bookmark in enumerate(self.bookmarks):
            selected = self.mode == "list" and index == self.selected_index

            row = ctk.CTkFrame(
                self.list_frame,
                fg_color=SURFACE_ALT if selected else SURFACE,
                corner_radius=6,
                border_width=1,
                border_color=TEXT if selected else BORDER
            )
            row.pack(fill="x", pady=7, padx=3)

            text_frame = ctk.CTkFrame(row, fg_color="transparent")
            text_frame.pack(fill="x", padx=14, pady=12)

            prefix = "> " if selected else ""

            ctk.CTkLabel(
                text_frame,
                text=f"{prefix}{bookmark['book_title']}",
                text_color=TEXT if selected else TEXT_MUTED,
                anchor="w",
                font=bold_font(15)
            ).pack(fill="x")

            ctk.CTkLabel(
                text_frame,
                text=f"page {bookmark['page'] + 1}",
                text_color=TEXT_MUTED,
                anchor="w",
                font=body_font(12)
            ).pack(fill="x", pady=(4, 0))

            row.bind("<Button-1>", lambda event, i=index: self.mouse_select_bookmark(i))
            text_frame.bind("<Button-1>", lambda event, i=index: self.mouse_select_bookmark(i))

    def render_actions(self):
        for widget in self.action_frame.winfo_children():
            widget.destroy()

        if not self.bookmarks:
            ctk.CTkLabel(
                self.action_frame,
                text="no bookmark selected",
                text_color=TEXT_MUTED,
                font=body_font(12)
            ).pack(pady=14)
            return

        bookmark = self.bookmarks[self.selected_index]

        title_text = f"{bookmark['book_title']} | page {bookmark['page'] + 1}" if self.mode == "actions" else "select a bookmark"

        ctk.CTkLabel(
            self.action_frame,
            text=title_text,
            text_color=TEXT if self.mode == "actions" else TEXT_MUTED,
            font=body_font(12),
            justify="center"
        ).pack(pady=(12, 6))

        row = ctk.CTkFrame(self.action_frame, fg_color="transparent")
        row.pack(pady=(4, 12))

        actions = self.get_actions(bookmark)

        for index, action in enumerate(actions):
            selected = self.mode == "actions" and index == self.selected_action_index
            label = f"> {action['label']} <" if selected else action["label"]

            TextButton(
                row,
                text=label,
                command=action["command"],
                size=12,
                color=TEXT if selected else TEXT_MUTED,
                danger=action.get("danger", False)
            ).pack(side="left", padx=16)

    def get_actions(self, bookmark):
        return [
            {
                "label": "open",
                "command": lambda: self.controller.show_reader(bookmark["book_id"], start_page=bookmark["page"])
            },
            {
                "label": "remove",
                "command": self.remove_selected_bookmark,
                "danger": True
            }
        ]

    def mouse_select_bookmark(self, index):
        self.selected_index = index
        self.selected_action_index = 0
        self.mode = "actions"
        self.refresh()

    def remove_selected_bookmark(self):
        if not self.bookmarks:
            return

        remove_bookmark(self.bookmarks[self.selected_index]["id"])
        self.mode = "list"
        self.selected_action_index = 0
        self.refresh()

    def handle_up(self):
        if not self.bookmarks:
            return

        if self.mode == "list":
            self.selected_index = (self.selected_index - 1) % len(self.bookmarks)
        else:
            actions = self.get_actions(self.bookmarks[self.selected_index])
            self.selected_action_index = (self.selected_action_index - 1) % len(actions)

        self.refresh()

    def handle_down(self):
        if not self.bookmarks:
            return

        if self.mode == "list":
            self.selected_index = (self.selected_index + 1) % len(self.bookmarks)
        else:
            actions = self.get_actions(self.bookmarks[self.selected_index])
            self.selected_action_index = (self.selected_action_index + 1) % len(actions)

        self.refresh()

    def handle_select(self):
        if not self.bookmarks:
            return

        if self.mode == "list":
            self.mode = "actions"
            self.selected_action_index = 0
            self.refresh()
            return

        actions = self.get_actions(self.bookmarks[self.selected_index])
        actions[self.selected_action_index]["command"]()

    def handle_back(self):
        if self.mode == "actions":
            self.mode = "list"
            self.refresh()
            return

        self.controller.show_home()
