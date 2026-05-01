import customtkinter as ctk

from app.ui.style import BG, TEXT_MUTED, TextButton, title_font, body_font


class HomeScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=0, fg_color=BG)
        self.controller = controller

        title = ctk.CTkLabel(
            self,
            text="DillyPie",
            text_color="#111111",
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

        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack()

        buttons = [
            ("read", controller.show_start_book),
            ("edit books", controller.show_edit_books),
            ("bookmarks", controller.show_bookmarks),
            ("exit", controller.destroy),
        ]

        for text, command in buttons:
            button = TextButton(
                button_frame,
                text=text,
                command=command,
                size=21
            )
            button.pack(pady=13)
