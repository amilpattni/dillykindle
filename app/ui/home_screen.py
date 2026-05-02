import customtkinter as ctk

from app.ui.style import BG, TEXT, TEXT_MUTED, TextButton, title_font, body_font


class HomeScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=0, fg_color=BG)
        self.controller = controller
        self.selected_index = 0

        self.options = [
            ("read", controller.show_start_book),
            ("edit books", controller.show_edit_books),
            ("bookmarks", controller.show_bookmarks),
        ]

        title = ctk.CTkLabel(
            self,
            text="dillykindle",
            text_color=TEXT,
            font=title_font(42)
        )
        title.pack(pady=(110, 8))

        subtitle = ctk.CTkLabel(
            self,
            text="for when diya wants to read",
            text_color=TEXT_MUTED,
            font=body_font(15)
        )
        subtitle.pack(pady=(0, 70))

        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack()

        self.option_labels = []

        for text, command in self.options:
            button = TextButton(
                self.button_frame,
                text=text,
                command=command,
                size=21
            )
            button.pack(pady=13)
            self.option_labels.append(button)

        self.update_selection()

    def update_selection(self):
        for index, label in enumerate(self.option_labels):
            base_text = self.options[index][0]

            if index == self.selected_index:
                label.configure(text=f"> {base_text} <", text_color=TEXT)
            else:
                label.configure(text=base_text, text_color=TEXT_MUTED)

    def handle_up(self):
        self.selected_index = (self.selected_index - 1) % len(self.options)
        self.update_selection()

    def handle_down(self):
        self.selected_index = (self.selected_index + 1) % len(self.options)
        self.update_selection()

    def handle_select(self):
        self.options[self.selected_index][1]()

    def handle_back(self):
        return
