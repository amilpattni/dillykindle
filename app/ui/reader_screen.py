import customtkinter as ctk
from PIL import ImageTk

from app.core.book_manager import get_book
from app.core.bookmark_manager import add_bookmark
from app.core.pdf_reader import PDFReader
from app.core.progress_manager import get_page, set_page
from app.ui.style import BG, SURFACE, BORDER, TEXT, TEXT_MUTED, TextButton, body_font, bold_font


class ReaderScreen(ctk.CTkFrame):
    def __init__(self, parent, controller, book_id, start_page=None):
        super().__init__(parent, corner_radius=0, fg_color=BG)
        self.controller = controller
        self.book_id = book_id
        self.book = get_book(book_id)
        self.pdf = None
        self.page_image = None
        self.render_after_id = None
        self.status_after_id = None

        if start_page is None:
            self.current_page = get_page(book_id)
        else:
            self.current_page = start_page

        if self.book is not None:
            try:
                self.pdf = PDFReader(self.book["path"])
                if self.current_page >= self.pdf.page_count:
                    self.current_page = max(0, self.pdf.page_count - 1)
            except Exception:
                self.pdf = None

        self.build_top_bar()
        self.build_page_area()
        self.build_bottom_controls()
        self.bind_keys()

        self.after(150, self.render_current_page)

    def build_top_bar(self):
        top_bar = ctk.CTkFrame(self, height=30, corner_radius=0, fg_color=BG)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)

        home_button = TextButton(
            top_bar,
            text="home",
            command=self.go_home,
            size=10
        )
        home_button.pack(side="left", padx=8, pady=6)

        if self.book is None:
            title_text = "book not found"
        else:
            title_text = self.book["title"]

        title = ctk.CTkLabel(
            top_bar,
            text=title_text,
            text_color=TEXT,
            font=bold_font(10),
            anchor="center"
        )
        title.pack(side="left", fill="x", expand=True, padx=4)

        self.page_label = ctk.CTkLabel(
            top_bar,
            text="pg -",
            text_color=TEXT_MUTED,
            font=body_font(9),
            width=64
        )
        self.page_label.pack(side="right", padx=6)

    def build_page_area(self):
        self.page_area = ctk.CTkFrame(self, corner_radius=0, fg_color=BG)
        self.page_area.pack(fill="both", expand=True)

        self.page_container = ctk.CTkFrame(
            self.page_area,
            fg_color=SURFACE,
            corner_radius=2,
            border_width=1,
            border_color=BORDER
        )
        self.page_container.pack(fill="both", expand=True, padx=6, pady=3)

        self.image_label = ctk.CTkLabel(
            self.page_container,
            text="loading page...",
            text_color=TEXT,
            font=body_font(12)
        )
        self.image_label.place(relx=0.5, rely=0.5, anchor="center")

        self.page_container.bind("<Configure>", self.schedule_render)

    def build_bottom_controls(self):
        bottom_bar = ctk.CTkFrame(self, height=40, corner_radius=0, fg_color=BG)
        bottom_bar.pack(fill="x", side="bottom")
        bottom_bar.pack_propagate(False)

        controls = ctk.CTkFrame(bottom_bar, fg_color="transparent")
        controls.pack(pady=(2, 0))

        prev_button = TextButton(
            controls,
            text="back",
            command=self.previous_page,
            size=10
        )
        prev_button.pack(side="left", padx=16)

        bookmark_button = TextButton(
            controls,
            text="mark",
            command=self.bookmark_page,
            size=10
        )
        bookmark_button.pack(side="left", padx=16)

        next_button = TextButton(
            controls,
            text="next",
            command=self.next_page,
            size=10
        )
        next_button.pack(side="left", padx=16)

        self.status_label = ctk.CTkLabel(
            bottom_bar,
            text="",
            text_color=TEXT_MUTED,
            font=body_font(8)
        )
        self.status_label.pack(pady=(0, 1))

    def bind_keys(self):
        self.controller.bind("<Left>", lambda event: self.previous_page())
        self.controller.bind("<Right>", lambda event: self.next_page())
        self.controller.bind("b", lambda event: self.bookmark_page())
        self.controller.bind("B", lambda event: self.bookmark_page())
        self.controller.bind("<Escape>", lambda event: self.go_home())

    def unbind_keys(self):
        self.controller.unbind("<Left>")
        self.controller.unbind("<Right>")
        self.controller.unbind("b")
        self.controller.unbind("B")
        self.controller.unbind("<Escape>")

    def schedule_render(self, event=None):
        if self.render_after_id is not None:
            self.after_cancel(self.render_after_id)

        self.render_after_id = self.after(250, self.render_current_page)

    def render_current_page(self):
        self.render_after_id = None

        if self.pdf is None:
            self.image_label.configure(
                text="could not open this pdf",
                image=None
            )
            self.page_label.configure(text="pg -")
            return

        container_width = self.page_container.winfo_width()
        container_height = self.page_container.winfo_height()

        if container_width < 50 or container_height < 50:
            return

        target_width = container_width - 8
        target_height = container_height - 8

        try:
            pil_image = self.pdf.render_page(
                self.current_page,
                target_width,
                target_height
            )

            self.page_image = ImageTk.PhotoImage(pil_image)

            self.image_label.configure(
                image=self.page_image,
                text=""
            )

            self.page_label.configure(
                text=f"pg {self.current_page + 1}/{self.pdf.page_count}"
            )

            set_page(self.book_id, self.current_page)

        except Exception as error:
            self.image_label.configure(
                text=f"render failed\n{error}",
                image=None
            )

    def previous_page(self):
        if self.pdf is None:
            return

        if self.current_page <= 0:
            return

        self.current_page -= 1
        self.render_current_page()

    def next_page(self):
        if self.pdf is None:
            return

        if self.current_page >= self.pdf.page_count - 1:
            return

        self.current_page += 1
        self.render_current_page()

    def bookmark_page(self):
        if self.book is None:
            return

        add_bookmark(
            self.book_id,
            self.book["title"],
            self.current_page
        )

        self.show_status(f"marked page {self.current_page + 1}")

    def show_status(self, message):
        self.status_label.configure(text=message)

        if self.status_after_id is not None:
            self.after_cancel(self.status_after_id)

        self.status_after_id = self.after(1400, lambda: self.status_label.configure(text=""))

    def go_home(self):
        if self.pdf is not None:
            set_page(self.book_id, self.current_page)
            self.pdf.close()

        self.unbind_keys()
        self.controller.show_home()


    def handle_up(self):
        self.previous_page()

    def handle_down(self):
        self.next_page()

    def handle_select(self):
        self.bookmark_page()

    def handle_back(self):
        self.go_home()

    def destroy(self):
        if self.pdf is not None:
            self.pdf.close()

        self.unbind_keys()
        super().destroy()
