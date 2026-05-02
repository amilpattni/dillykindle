import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog, messagebox

from app.core.book_manager import add_book, get_books, remove_book
from app.ui.style import BG, SURFACE, SURFACE_ALT, BORDER, TEXT, TEXT_MUTED, TextButton, title_font, body_font


def get_usb_locations():
    username = Path.home().name

    possible_roots = [
        Path("/media") / username,
        Path("/run/media") / username,
    ]

    locations = []

    for root in possible_roots:
        if not root.exists():
            continue

        for item in sorted(root.iterdir()):
            if item.is_dir():
                locations.append(item)

    return locations


def get_usb_start_directory():
    usb_locations = get_usb_locations()

    if usb_locations:
        return usb_locations[0]

    username = Path.home().name
    media_root = Path("/media") / username

    if media_root.exists():
        return media_root

    return Path.home()


def get_usb_pdfs():
    files = []

    for location in get_usb_locations():
        try:
            for file in sorted(location.glob("*.pdf")):
                files.append(file)

            for file in sorted(location.glob("*.PDF")):
                files.append(file)

            for folder in sorted(location.iterdir()):
                if folder.is_dir():
                    for file in sorted(folder.glob("*.pdf")):
                        files.append(file)

                    for file in sorted(folder.glob("*.PDF")):
                        files.append(file)

        except PermissionError:
            continue
        except FileNotFoundError:
            continue

    unique = []
    seen = set()

    for file in files:
        resolved = str(file.resolve())
        if resolved not in seen:
            unique.append(file)
            seen.add(resolved)

    return unique


class EditBooksScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=0, fg_color=BG)
        self.controller = controller
        self.mode = "main"
        self.selected_index = 0
        self.selected_action_index = 0
        self.usb_pdfs = []
        self.status_text = ""

        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(fill="x", padx=24, pady=(24, 0))

        home_button = TextButton(
            nav_frame,
            text="home",
            command=controller.show_home,
            size=14
        )
        home_button.pack(side="left")

        self.title = ctk.CTkLabel(
            self,
            text="edit books",
            text_color=TEXT,
            font=title_font(30)
        )
        self.title.pack(pady=(34, 22))

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

    def get_main_items(self):
        items = [
            {
                "type": "import_files",
                "label": "import from files"
            },
            {
                "type": "import_usb",
                "label": "import from usb"
            }
        ]

        for book in get_books():
            items.append(
                {
                    "type": "book",
                    "label": book["title"],
                    "book": book
                }
            )

        return items

    def refresh(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        for widget in self.action_frame.winfo_children():
            widget.destroy()

        if self.mode == "main":
            self.render_main()
        elif self.mode == "usb":
            self.render_usb()
        elif self.mode == "book_actions":
            self.render_book_actions()
        elif self.mode == "confirm_delete":
            self.render_confirm_delete()

    def render_main(self):
        self.title.configure(text="edit books")
        items = self.get_main_items()

        if self.selected_index >= len(items):
            self.selected_index = max(0, len(items) - 1)

        for index, item in enumerate(items):
            selected = index == self.selected_index

            row = ctk.CTkFrame(
                self.list_frame,
                fg_color=SURFACE_ALT if selected else SURFACE,
                corner_radius=6,
                border_width=1,
                border_color=TEXT if selected else BORDER
            )
            row.pack(fill="x", pady=6, padx=3)

            prefix = "> " if selected else ""

            label = ctk.CTkLabel(
                row,
                text=f"{prefix}{item['label']}",
                text_color=TEXT if selected else TEXT_MUTED,
                anchor="w",
                font=body_font(14),
                cursor="hand2"
            )
            label.pack(fill="x", padx=14, pady=13)

            row.bind("<Button-1>", lambda event, i=index: self.select_main_with_mouse(i))
            label.bind("<Button-1>", lambda event, i=index: self.select_main_with_mouse(i))

        note_text = self.status_text or "select import or choose a book"
        note = ctk.CTkLabel(
            self.action_frame,
            text=note_text,
            text_color=TEXT_MUTED,
            font=body_font(12),
            justify="center"
        )
        note.pack(pady=14)

    def render_usb(self):
        self.title.configure(text="usb pdfs")

        if not self.usb_pdfs:
            label = ctk.CTkLabel(
                self.list_frame,
                text="no pdfs found on usb\n\nplug in usb and try again",
                text_color=TEXT_MUTED,
                font=body_font(15),
                justify="center"
            )
            label.pack(pady=80)
        else:
            if self.selected_index >= len(self.usb_pdfs):
                self.selected_index = max(0, len(self.usb_pdfs) - 1)

            for index, pdf in enumerate(self.usb_pdfs):
                selected = index == self.selected_index

                row = ctk.CTkFrame(
                    self.list_frame,
                    fg_color=SURFACE_ALT if selected else SURFACE,
                    corner_radius=6,
                    border_width=1,
                    border_color=TEXT if selected else BORDER
                )
                row.pack(fill="x", pady=6, padx=3)

                prefix = "> " if selected else ""

                label = ctk.CTkLabel(
                    row,
                    text=f"{prefix}{pdf.name}",
                    text_color=TEXT if selected else TEXT_MUTED,
                    anchor="w",
                    font=body_font(13),
                    cursor="hand2"
                )
                label.pack(fill="x", padx=14, pady=13)

                row.bind("<Button-1>", lambda event, i=index: self.select_usb_with_mouse(i))
                label.bind("<Button-1>", lambda event, i=index: self.select_usb_with_mouse(i))

        note = ctk.CTkLabel(
            self.action_frame,
            text="select imports pdf\nback cancels",
            text_color=TEXT_MUTED,
            font=body_font(12),
            justify="center"
        )
        note.pack(pady=14)

    def render_book_actions(self):
        self.title.configure(text="book actions")
        item = self.get_main_items()[self.selected_index]
        book = item["book"]

        label = ctk.CTkLabel(
            self.list_frame,
            text=book["title"],
            text_color=TEXT,
            font=body_font(15),
            justify="center"
        )
        label.pack(pady=70)

        actions = [
            {
                "label": "delete book",
                "danger": True
            },
            {
                "label": "cancel",
                "danger": False
            }
        ]

        row = ctk.CTkFrame(self.action_frame, fg_color="transparent")
        row.pack(pady=14)

        for index, action in enumerate(actions):
            selected = index == self.selected_action_index
            text = f"> {action['label']} <" if selected else action["label"]

            button = TextButton(
                row,
                text=text,
                command=lambda i=index: self.activate_book_action(i),
                size=12,
                danger=action["danger"],
                color=TEXT if selected else TEXT_MUTED
            )
            button.pack(side="left", padx=16)

    def render_confirm_delete(self):
        self.title.configure(text="confirm delete")
        item = self.get_main_items()[self.selected_index]
        book = item["book"]

        label = ctk.CTkLabel(
            self.list_frame,
            text=f"delete this book?\n\n{book['title']}",
            text_color=TEXT,
            font=body_font(15),
            justify="center"
        )
        label.pack(pady=70)

        actions = [
            {
                "label": "yes delete",
                "danger": True
            },
            {
                "label": "cancel",
                "danger": False
            }
        ]

        row = ctk.CTkFrame(self.action_frame, fg_color="transparent")
        row.pack(pady=14)

        for index, action in enumerate(actions):
            selected = index == self.selected_action_index
            text = f"> {action['label']} <" if selected else action["label"]

            button = TextButton(
                row,
                text=text,
                command=lambda i=index: self.activate_confirm_delete(i),
                size=12,
                danger=action["danger"],
                color=TEXT if selected else TEXT_MUTED
            )
            button.pack(side="left", padx=16)

    def select_main_with_mouse(self, index):
        self.selected_index = index
        self.activate_main_item()

    def select_usb_with_mouse(self, index):
        self.selected_index = index
        self.import_selected_usb_pdf()

    def handle_import_book(self):
        self.import_from_directory(Path.home())

    def handle_import_from_usb(self):
        self.usb_pdfs = get_usb_pdfs()
        self.mode = "usb"
        self.selected_index = 0
        self.refresh()

    def import_from_directory(self, start_directory):
        file_path = filedialog.askopenfilename(
            title="Import a PDF book",
            initialdir=str(start_directory),
            filetypes=[("PDF Books", "*.pdf")]
        )

        if not file_path:
            return

        try:
            book = add_book(file_path)
            self.status_text = f"imported: {book['title']}"
            self.mode = "main"
            self.refresh()
        except Exception as error:
            messagebox.showerror("Import Book Failed", str(error))

    def activate_main_item(self):
        items = self.get_main_items()

        if not items:
            return

        item = items[self.selected_index]

        if item["type"] == "import_files":
            self.import_from_directory(Path.home())
            return

        if item["type"] == "import_usb":
            self.usb_pdfs = get_usb_pdfs()
            self.mode = "usb"
            self.selected_index = 0
            self.refresh()
            return

        if item["type"] == "book":
            self.mode = "book_actions"
            self.selected_action_index = 0
            self.refresh()

    def import_selected_usb_pdf(self):
        if not self.usb_pdfs:
            return

        try:
            book = add_book(self.usb_pdfs[self.selected_index])
            self.status_text = f"imported: {book['title']}"
            self.mode = "main"
            self.selected_index = 0
            self.refresh()
        except Exception as error:
            self.status_text = f"import failed: {error}"
            self.mode = "main"
            self.refresh()

    def activate_book_action(self, index):
        if index == 0:
            self.mode = "confirm_delete"
            self.selected_action_index = 0
            self.refresh()
        else:
            self.mode = "main"
            self.refresh()

    def activate_confirm_delete(self, index):
        if index == 0:
            item = self.get_main_items()[self.selected_index]
            title = item["book"]["title"]
            remove_book(item["book"]["id"], delete_file=True)
            self.status_text = f"deleted: {title}"
            self.mode = "main"
            self.selected_index = 0
            self.selected_action_index = 0
            self.refresh()
        else:
            self.mode = "book_actions"
            self.selected_action_index = 0
            self.refresh()

    def handle_up(self):
        if self.mode == "main":
            items = self.get_main_items()
            if items:
                self.selected_index = (self.selected_index - 1) % len(items)

        elif self.mode == "usb":
            if self.usb_pdfs:
                self.selected_index = (self.selected_index - 1) % len(self.usb_pdfs)

        elif self.mode in ["book_actions", "confirm_delete"]:
            self.selected_action_index = (self.selected_action_index - 1) % 2

        self.refresh()

    def handle_down(self):
        if self.mode == "main":
            items = self.get_main_items()
            if items:
                self.selected_index = (self.selected_index + 1) % len(items)

        elif self.mode == "usb":
            if self.usb_pdfs:
                self.selected_index = (self.selected_index + 1) % len(self.usb_pdfs)

        elif self.mode in ["book_actions", "confirm_delete"]:
            self.selected_action_index = (self.selected_action_index + 1) % 2

        self.refresh()

    def handle_select(self):
        if self.mode == "main":
            self.activate_main_item()
        elif self.mode == "usb":
            self.import_selected_usb_pdf()
        elif self.mode == "book_actions":
            self.activate_book_action(self.selected_action_index)
        elif self.mode == "confirm_delete":
            self.activate_confirm_delete(self.selected_action_index)

    def handle_back(self):
        if self.mode == "main":
            self.controller.show_home()
        elif self.mode == "usb":
            self.mode = "main"
            self.selected_index = 0
            self.refresh()
        elif self.mode == "book_actions":
            self.mode = "main"
            self.refresh()
        elif self.mode == "confirm_delete":
            self.mode = "book_actions"
            self.selected_action_index = 0
            self.refresh()

    def handle_delete_book(self):
        items = self.get_main_items()

        if not items:
            return

        item = items[self.selected_index]

        if item["type"] == "book":
            self.mode = "confirm_delete"
            self.selected_action_index = 0
            self.refresh()
