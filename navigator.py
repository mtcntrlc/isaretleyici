from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt, QPoint
import settings


class Navigator:
    def __init__(self, main_window, document_manager, itemizer):
        self.main_window = main_window
        self.document_manager = document_manager
        self.itemizer = itemizer
        self.preview_label = QLabel(self.main_window)
        self.update_style()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.hide()
        self.preview_active = True

    def update_style(self):
        r = int(settings.DEFAULT_BACKGROUND_COLOR[0] * 255)
        g = int(settings.DEFAULT_BACKGROUND_COLOR[1] * 255)
        b = int(settings.DEFAULT_BACKGROUND_COLOR[2] * 255)
        style = f"background-color: rgb({r}, {g}, {b}); color: black; font-size: 12px; border: 1px solid black; padding: 2px;"
        self.preview_label.setStyleSheet(style)

    def next_page(self):
        if self.document_manager and self.document_manager.current_page_index < self.document_manager.get_page_count() - 2:
            self.document_manager.current_page_index += 2
            if settings.DEFAULT_NUMBERING_MODE == settings.NumberingMode.PER_PAGE:
                self.itemizer.reset_items()
            self.main_window.show_pages()

    def previous_page(self):
        if self.document_manager and self.document_manager.current_page_index > 1:
            self.document_manager.current_page_index -= 2
            if settings.DEFAULT_NUMBERING_MODE == settings.NumberingMode.PER_PAGE:
                self.itemizer.reset_items()
            self.main_window.show_pages()

    def show_preview(self, window_pos):
        if not self.preview_active: return
        preview_text = str(self.itemizer.get_current_item_display())
        self.preview_label.setText(preview_text)
        self.preview_label.adjustSize()
        self.preview_label.move(window_pos + QPoint(15, 15))
        self.preview_label.show()

    def clear_preview(self):
        self.preview_label.hide()