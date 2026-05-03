from pathlib import Path

import fitz
from PIL import Image


class PDFReader:
    def __init__(self, path):
        self.path = Path(path)
        self.document = fitz.open(self.path)
        self.page_count = len(self.document)

    def close(self):
        if self.document is not None:
            self.document.close()
            self.document = None

    def render_page(self, page_number, target_width, target_height):
        if page_number < 0:
            page_number = 0

        if page_number >= self.page_count:
            page_number = self.page_count - 1

        page = self.document.load_page(page_number)
        rect = page.rect

        width_scale = target_width / rect.width
        height_scale = target_height / rect.height
        scale = min(width_scale, height_scale)

        render_scale = max(scale * 1.25, 1.0)

        matrix = fitz.Matrix(render_scale, render_scale)
        pixmap = page.get_pixmap(matrix=matrix, alpha=False)

        image = Image.frombytes(
            "RGB",
            [pixmap.width, pixmap.height],
            pixmap.samples
        )

        final_width = int(rect.width * scale)
        final_height = int(rect.height * scale)

        image = image.resize((final_width, final_height), Image.Resampling.LANCZOS)

        return image
