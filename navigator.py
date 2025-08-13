from PySide6.QtWidgets import QLabel, QMainWindow
from PySide6.QtCore import Qt, QPoint, QTimer
from PySide6.QtGui import QPainter, QPen, QColor
from itemizer import Itemizer  # Itemizer'ı projenizde mevcut olduğuna göre ekliyorum
from pdf_processor import PDFProcessor  # PDFProcessor'ı da mevcut modül olarak ekliyorum


class Navigator:
    def __init__(self, main_window: QMainWindow, pdf_processor: PDFProcessor, itemizer: Itemizer):
        self.main_window = main_window
        self.pdf_processor = pdf_processor
        self.itemizer = itemizer

        # Önizleme etiketini oluşturuyoruz
        self.preview_label = QLabel(self.main_window)
        self.preview_label.setStyleSheet("background-color: #d1c708; color: black; font-size: 12px;")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.hide()  # Başlangıçta gizlenmiş olarak ayarlanıyor

        # Önizlemenin aktif olup olmadığını kontrol eden bayrak
        self.preview_active = True

    # Önizlemeyi sürekli fareyle hareket ettirmek için güncelleme fonksiyonu
    def show_preview(self, mouse_pos):
        # Sıradaki maddeyi çekiyoruz
        preview_text = str(self.itemizer.get_next_item())

        # Önizleme label'ına bu maddeyi yerleştiriyoruz
        self.preview_label.setText(preview_text)
        self.preview_label.adjustSize()  # Boyutu içeriğe göre ayarla
        label_offset = QPoint(15, 15)  # İmlecin ucunda biraz sağ-alt
        self.preview_label.move(self.mapToGlobal(mouse_pos) + label_offset)  # Global pozisyona göre ayarla

        # Görseli yarı saydam olarak gösteriyoruz
        self.preview_label.setVisible(True)

    def toggle_preview(self):
        """
        Önizleme görünürlüğünü açıp kapatır.
        """
        self.preview_active = not self.preview_active
        if not self.preview_active:
            self.preview_label.hide()

    def enable_preview_shortcut(self):
        """
        Kısayol tuşuyla önizlemeyi açıp kapatır.
        """
        self.main_window.keyPressEvent = self.handle_key_press

    def handle_key_press(self, event):
        """
        Kısayol tuşu (Ctrl + P) ile önizlemeyi açıp kapatır.
        """
        if event.key() == Qt.Key_P and event.modifiers() & Qt.ControlModifier:
            self.toggle_preview()

    def clear_preview(self):
        """
        Kullanıcı tıklama işlemini gerçekleştirdikten sonra önizlemeyi temizler.
        """
        self.preview_label.hide()

