from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QFileDialog
from PySide6.QtGui import QPixmap, QMouseEvent, QKeyEvent, QAction, QShortcut, QKeySequence
from PySide6.QtCore import Qt, QEvent
from pdf_processor import PDFProcessor
from itemizer import Itemizer
from navigator import Navigator
from color_selector import ColorSelector
from previewer import Previewer
from controller import ShortcutController


class MainGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pdf_processor = None
        self.itemizer = Itemizer()
        self.previewer = None
        self.init_ui()
        self.init_menu()

        # Kısayol kontrolcüsünü başlatma ve modülleri bağlama
        self.shortcut_controller = ShortcutController(self, self.pdf_processor, self.itemizer)

    def init_ui(self):
        self.setWindowTitle("PDF İşaretleyici")
        self.setGeometry(100, 100, 1200, 800)

        self.select_pdf_button = QPushButton("PDF Seç", self)
        self.select_pdf_button.clicked.connect(self.select_pdf)
        self.select_pdf_button.move(50, 50)

        self.left_page_label = QLabel(self)
        self.left_page_label.setGeometry(50, 100, 550, 600)
        self.left_page_label.mousePressEvent = lambda event: self.add_item_and_refresh(event)

        self.right_page_label = QLabel(self)
        self.right_page_label.setGeometry(600, 100, 550, 600)

    def init_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        save_action = QAction("PDF'yi Kaydet", self)
        save_action.triggered.connect(self.save_pdf)
        file_menu.addAction(save_action)

    def reset_items(self):
        if self.itemizer:
            self.itemizer.reset_items()
        if self.pdf_processor:
            self.pdf_processor.reset_items()
        print("MainGUI üzerinde sıfırlama işlemi tamamlandı.")

    def select_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "PDF Dosyası Seç", "", "PDF Files (*.pdf)")
        if file_path:
            self.select_pdf_button.hide()
            self.expand_labels()
            self.load_pdf(file_path)

    def expand_labels(self):
        self.left_page_label.setGeometry(20, 20, 580, 750)
        self.right_page_label.setGeometry(600, 20, 580, 750)
        self.left_page_label.setScaledContents(True)
        self.right_page_label.setScaledContents(True)

    def load_pdf(self, file_path):
        try:
            self.pdf_processor = PDFProcessor(file_path)
            self.previewer = Previewer(self.pdf_processor)
            # ShortcutController'a pdf_processor'ı yükledikten sonra tekrar ver
            self.shortcut_controller.pdf_processor = self.pdf_processor
            print("PDF yüklendi ve işlenmeye hazır.")
            self.show_pages()
        except Exception as e:
            print(f"PDF yüklenirken bir hata oluştu: {e}")

    def show_pages(self):
        if not self.pdf_processor:
            return

        # Sol sayfa
        left_pix = self.previewer.show_preview(self.pdf_processor.get_current_page())
        if not left_pix.isNull():
            self.left_page_label.setPixmap(left_pix)
        else:
            self.left_page_label.clear()  # Sayfa yoksa temizle

        # Sağ sayfa
        if self.pdf_processor.get_current_page() < self.pdf_processor.get_page_count() - 1:
            right_pix = self.previewer.show_preview(self.pdf_processor.get_current_page() + 1)
            if not right_pix.isNull():
                self.right_page_label.setPixmap(right_pix)
            else:
                self.right_page_label.clear()  # Sayfa yoksa temizle
        else:
            self.right_page_label.clear()  # Son sayfada sağ tarafı temizle

    def add_item_and_refresh(self, event):
        if not self.pdf_processor:
            return
        label_width = self.left_page_label.width()
        label_height = self.left_page_label.height()
        print(f"Tıklanan konum: ({event.x()}, {event.y()})")
        self.pdf_processor.add_item_on_click(event, self.itemizer, label_width, label_height)
        self.show_pages()
        print("Sayfa güncelleniyor.")

    def undo_last_action(self):
        """Son işlemi geri alır."""
        self.shortcut_controller.perform_undo()
        print("Undo işlemi MainGUI üzerinden tetiklendi.")

    def next_page(self):
        if self.pdf_processor and self.pdf_processor.get_current_page() < self.pdf_processor.get_page_count() - 2:
            self.pdf_processor.current_page += 2  # İki sayfa ileri git
            self.show_pages()

    def previous_page(self):
        if self.pdf_processor and self.pdf_processor.get_current_page() > 1:
            self.pdf_processor.current_page -= 2  # İki sayfa geri git
            self.show_pages()

    def save_pdf(self):
        if self.pdf_processor:
            output_path, _ = QFileDialog.getSaveFileName(self, "PDF Kaydet", "", "PDF Files (*.pdf)")
            if output_path:
                self.pdf_processor.save_pdf(output_path)
                print(f"PDF '{output_path}' olarak kaydedildi.")

    # --- BİRLEŞTİRİLMİŞ keyPressEvent FONKSİYONU ---
    def keyPressEvent(self, event: QKeyEvent):
        # Ctrl+Z kısayolunu kontrol et
        if event.matches(QKeySequence.Undo):
            self.undo_last_action()
            return  # Olay işlendi, devam etme

        # PDF yüklü değilse diğer tuşlar çalışmasın
        if not self.pdf_processor:
            super().keyPressEvent(event)
            return

        key = event.key()
        # Sayfa geçişleri
        if key == Qt.Key.Key_Right:
            self.next_page()
        elif key == Qt.Key.Key_Left:
            self.previous_page()
        # Madde seviyesi
        elif key == Qt.Key.Key_Up:
            self.itemizer.decrease_level()
        elif key == Qt.Key.Key_Down:
            self.itemizer.increase_level()
        # Diğer tuş vuruşları için varsayılan davranışı çağır
        else:
            super().keyPressEvent(event)