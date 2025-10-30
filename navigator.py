from PySide6.QtWidgets import QLabel, QMainWindow
from PySide6.QtCore import Qt, QPoint
from itemizer import Itemizer
from pdf_processor import PDFProcessor
import settings


class Navigator:
    def __init__(self, main_window: QMainWindow, pdf_processor: PDFProcessor, itemizer: Itemizer):
        self.main_window = main_window
        self.pdf_processor = pdf_processor
        self.itemizer = itemizer

        self.preview_label = QLabel(self.main_window)
        self.update_style()  # Başlangıç stilini ayarla
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.hide()
        self.preview_active = True

    def update_style(self):
        """Önizleme etiketinin stilini `settings` dosyasındaki güncel renge göre ayarlar."""
        r = int(settings.DEFAULT_BACKGROUND_COLOR[0] * 255)
        g = int(settings.DEFAULT_BACKGROUND_COLOR[1] * 255)
        b = int(settings.DEFAULT_BACKGROUND_COLOR[2] * 255)

        style = f"background-color: rgb({r}, {g}, {b}); color: black; font-size: 12px; border: 1px solid black; padding: 2px;"
        self.preview_label.setStyleSheet(style)

    def next_page(self):
        """Bir sonraki sayfa setine geçer ve ayarlara göre sayacı sıfırlar."""
        if self.pdf_processor and self.pdf_processor.get_current_page() < self.pdf_processor.get_page_count() - 2:
            self.pdf_processor.current_page += 2
            if settings.DEFAULT_NUMBERING_MODE == settings.NumberingMode.PER_PAGE:
                self.itemizer.reset_items()
                print("Yeni sayfaya geçildi, sayaç sıfırlandı.")
            self.main_window.show_pages()

    def previous_page(self):
        """Bir önceki sayfa setine geçer ve ayarlara göre sayacı sıfırlar."""
        if self.pdf_processor and self.pdf_processor.get_current_page() > 1:
            self.pdf_processor.current_page -= 2
            if settings.DEFAULT_NUMBERING_MODE == settings.NumberingMode.PER_PAGE:
                self.itemizer.reset_items()
                print("Önceki sayfaya geçildi, sayaç sıfırlandı.")
            self.main_window.show_pages()

    def show_preview(self, window_pos):
        """Sıradaki maddeyi fare imlecinin yanında gösterir."""
        if not self.preview_active:
            return

        preview_text = str(self.itemizer.get_current_item_display())
        self.preview_label.setText(preview_text)
        self.preview_label.adjustSize()
        label_offset = QPoint(15, 15)

        self.preview_label.move(window_pos + label_offset)
        self.preview_label.show()

    def toggle_preview(self):
        """Önizleme görünürlüğünü açıp kapatır."""
        self.preview_active = not self.preview_active
        if not self.preview_active:
            self.preview_label.hide()

    def clear_preview(self):
        """Önizlemeyi temizler/gizler."""
        self.preview_label.hide()