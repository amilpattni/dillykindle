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
        Path("/mnt"),
    ]

    locations = []

    for root in possible_roots:
        if root.exists():
            for item in root.iterdir():
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


class EditBooksScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=0, fg_color=BG)
        self.controller = controller
        self.selected_book_id = None
        self.book_rows = {}

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
            text="edit books",
            text_color=TEXT,
            font=title_font(30)
        )
        title.pack(pady=(34, 22))

        top_buttons = ctk.CTkFrame(self, fg_color="transparent")
        top_buttons.pack(pady=8)

        import_file_button = TextButton(
            top_buttons,
            text="import from files",
            command=self.handle_import_book,
            size=15
        )
        import_file_button.pack(side="left", padx=12)

        import_usb_button = TextButton(
            top_buttons,
            text="import from usb",
            command=self.handle_import_from_usb,
            size=15
        )
        import_usb_button.pack(side="left", padx=12)

        delete_row = ctk.CTkFrame(self, fg_color="transparent")
        delete_row.pack(pady=(10, 0))

        delete_button = TextButton(
            delete_row,
            text="delete selected book",
            command=self.handle_delete_book,
            size=15,
            danger=True
        )
        delete_button.pack()

        self.list_frame = ctk.CTkScrollableFrame(
            self,
            width=420,
            height=390,
            fg_color=BG,
            border_width=0
        )
        self.list_frame.pack(pady=20, fill="both", expand=True, padx=28)

        self.selection_label = ctk.CTkLabel(
            self,
            text="no book selected",
            text_color=TEXT_MUTED,
            font=body_font(13)
        )
        self.selection_label.pack(pady=(0, 8))

        note = ctk.CTkLabel(
            self,
            text="import copies a pdf into dillykindle\ndelete removes it from this device",
            text_color=TEXT_MUTED,
            font=body_font(11),
            justify="center"
        )
        note.pack(pady=(0, 22))

        self.refresh_books()

    def refresh_books(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        self.book_rows = {}

        books = get_books()

        if not books:
            empty_label = ctk.CTkLabel(
                self.list_frame,
                text="no books imported yet",
                text_color=TEXT_MUTED,
                font=body_font(15)
            )
            empty_label.pack(pady=80)
            self.selection_label.configure(text="no book selected")
            return

        for book in books:
            row = ctk.CTkFrame(
                self.list_frame,
                fg_color=SURFACE,
                corner_radius=6,
                border_width=1,
                border_color=BORDER
            )
            row.pack(fill="x", pady=6, padx=3)

            label = ctk.CTkLabel(
                row,
                text=book["title"],
                text_color=TEXT,
                anchor="w",
                font=body_font(14),
                cursor="hand2"
            )
            label.pack(fill="x", padx=14, pady=13)

            row.bind("<Button-1>", lambda event, book_id=book["id"]: self.select_book(book_id))
            label.bind("<Button-1>", lambda event, book_id=book["id"]: self.select_book(book_id))

            self.book_rows[book["id"]] = {
                "frame": row,
                "label": label,
                "title": book["title"]
            }

        self.update_selection_styles()

    def select_book(self, book_id):
        self.selected_book_id = book_id
        self.update_selection_styles()

    def update_selection_styles(self):
        if not self.book_rows:
            return

        selected_title = None

        for book_id, row_data in self.book_rows.items():
            frame = row_data["frame"]

            if book_id == self.selected_book_id:
                frame.configure(fg_color=SURFACE_ALT, border_color=TEXT)
                selected_title = row_data["title"]
            else:
                frame.configure(fg_color=SURFACE, border_color=BORDER)

        if selected_title:
            self.selection_label.configure(text=f"selected: {selected_title}")
        else:
            self.selection_label.configure(text="no book selected")

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
            self.selected_book_id = book["id"]
            self.refresh_books()
        except Exception as error:
            messagebox.showerror("Import Book Failed", str(error))


    def move_selection(self, delta):
        books = get_books()

        if not books:
            return

        ids = [book["id"] for book in books]

        if self.selected_book_id in ids:
            index = ids.index(self.selected_book_id)
        else:
            index = 0

        index = (index + delta) % len(ids)
        self.select_book(ids[index])

    def handle_up(self):
        self.move_selection(-1)

    def handle_down(self):
        self.move_selection(1)

    def handle_select(self):
        if self.selected_book_id is None:
            self.move_selection(0)

    def handle_back(self):
        self.controller.show_home()

    def handle_import_book(self):
        self.import_from_directory(Path.home())

    def handle_import_from_usb(self):
        usb_locations = get_usb_locations()

        if not usb_locations:
            messagebox.showinfo(
                "No USB Found",
                "No USB drive was found.\n\nOn Raspberry Pi, USB drives usually appear under /media/amil/ after they are mounted."
            )

        self.import_from_directory(get_usb_start_directory())

    def handle_delete_book(self):
        if self.selected_book_id is None:
            messagebox.showinfo("No Book Selected", "Select a book first.")
            return

        selected_title = self.book_rows[self.selected_book_id]["title"]

        confirmed = messagebox.askyesno(
            "Delete Book",
            f"Delete '{selected_title}' from this device?\n\nThis will remove the PDF from dillykindle, plus its progress and bookmarks."
        )

        if not confirmed:
            return

        try:
            remove_book(self.selected_book_id, delete_file=True)
            self.selected_book_id = None
            self.refresh_books()
        except Exception as error:
            messagebox.showerror("Delete Book Failed", str(error))
