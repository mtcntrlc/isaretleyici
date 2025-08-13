from PySide6.QtWidgets import QColorDialog

class ColorSelector:
    def __init__(self):
        self.background_color = None
        self.text_color = None

    def select_background_color(self):
        """Arka plan rengi seç."""
        self.background_color = QColorDialog.getColor()

    def select_text_color(self):
        """Yazı rengi seç."""
        self.text_color = QColorDialog.getColor()