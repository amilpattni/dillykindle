import customtkinter as ctk

BG = "#f7f5ef"
SURFACE = "#ffffff"
SURFACE_ALT = "#eeeae0"
TEXT = "#111111"
TEXT_MUTED = "#555555"
TEXT_HOVER = "#666666"
DANGER = "#8a1f1f"
DANGER_HOVER = "#b33333"
BORDER = "#d8d2c4"

FONT = "DejaVu Sans Mono"


def title_font(size=40):
    return ctk.CTkFont(family=FONT, size=size, weight="bold")


def body_font(size=16):
    return ctk.CTkFont(family=FONT, size=size)


def bold_font(size=16):
    return ctk.CTkFont(family=FONT, size=size, weight="bold")


class TextButton(ctk.CTkLabel):
    def __init__(
        self,
        parent,
        text,
        command,
        size=18,
        color=TEXT,
        hover_color=TEXT_HOVER,
        danger=False,
        **kwargs
    ):
        if danger:
            color = DANGER
            hover_color = DANGER_HOVER

        super().__init__(
            parent,
            text=text,
            text_color=color,
            font=body_font(size),
            cursor="hand2",
            **kwargs
        )

        self.command = command
        self.normal_color = color
        self.hover_text_color = hover_color

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)

    def on_enter(self, event=None):
        self.configure(text_color=self.hover_text_color)

    def on_leave(self, event=None):
        self.configure(text_color=self.normal_color)

    def on_click(self, event=None):
        if self.command is not None:
            self.command()
