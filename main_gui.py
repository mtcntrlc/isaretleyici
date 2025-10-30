from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, QMessageBox, QColorDialog
from PySide6.QtGui import QKeyEvent, QKeySequence, QAction
from PySide6.QtCore import Qt
from pdf_processor import PDFProcessor
from itemizer import Itemizer
from navigator import Navigator
from previewer import Previewer
from controller import ShortcutController
import settings


class MainGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pdf_processor = None
        self.itemizer = Itemizer()
        self.previewer = None
        self.navigator = None
        self.init_ui()
        self.init_menu()
        self.shortcut_controller = ShortcutController(self, self.pdf_processor, self.itemizer)
        self.statusBar().showMessage("Lütfen bir PDF dosyası seçin.")

        self.setMouseTracking(True)
        self.left_page_label.setMouseTracking(True)
        self.right_page_label.setMouseTracking(True)

    def init_ui(self):
        self.setWindowTitle("PDF İşaretleyici")
        self.setGeometry(100, 100, 1200, 800)
        self.select_pdf_button = QPushButton("PDF Seç", self)
        self.select_pdf_button.clicked.connect(self.select_pdf)
        self.select_pdf_button.move(50, 50)
        self.select_color_button = QPushButton("Renk Seç", self)
        self.select_color_button.clicked.connect(self.select_color)
        self.select_color_button.move(150, 50)
        self.left_page_label = QLabel(self)
        self.left_page_label.setGeometry(50, 100, 550, 600)
        self.left_page_label.mousePressEvent = lambda event: self.add_item_and_refresh(event)
        self.right_page_label = QLabel(self)
        self.right_page_label.setGeometry(600, 100, 550, 600)

    # ... (init_menu, select_color, select_pdf, expand_labels, load_pdf, show_pages, add_item_and_refresh, undo_last_action, save_pdf fonksiyonları aynı kalıyor) ...
    def init_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        save_action = QAction("PDF'yi Kaydet", self)
        save_action.triggered.connect(self.save_pdf)
        file_menu.addAction(save_action)

    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            settings.DEFAULT_BACKGROUND_COLOR = (color.redF(), color.greenF(), color.blueF())
            self.statusBar().showMessage(f"Yeni renk seçildi: RGB({color.red()}, {color.green()}, {color.blue()})")

            if self.navigator:
                self.navigator.update_style()

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
            self.navigator = Navigator(self, self.pdf_processor, self.itemizer)
            self.shortcut_controller.pdf_processor = self.pdf_processor
            self.statusBar().showMessage(f"PDF yüklendi: {file_path}")
            self.show_pages()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"PDF yüklenirken bir hata oluştu:\n{e}")
            self.statusBar().showMessage("PDF yüklenemedi.")

    def show_pages(self):
        if not self.pdf_processor:
            return
        left_pix = self.previewer.show_preview(self.pdf_processor.get_current_page())
        self.left_page_label.setPixmap(left_pix if not left_pix.isNull() else None)
        if self.pdf_processor.get_current_page() < self.pdf_processor.get_page_count() - 1:
            right_pix = self.previewer.show_preview(self.pdf_processor.get_current_page() + 1)
            self.right_page_label.setPixmap(right_pix if not right_pix.isNull() else None)
        else:
            self.right_page_label.clear()
        self.statusBar().showMessage(
            f"Sayfa {self.pdf_processor.get_current_page() + 1} gösteriliyor. Sıradaki madde: {self.itemizer.get_current_item_display()}")

    def add_item_and_refresh(self, event):
        if not self.pdf_processor:
            return
        if self.navigator:
            self.navigator.clear_preview()
        label_width = self.left_page_label.width()
        label_height = self.left_page_label.height()
        self.pdf_processor.add_item_on_click(event, self.itemizer, label_width, label_height)
        self.show_pages()

    def undo_last_action(self):
        self.shortcut_controller.perform_undo()
        self.statusBar().showMessage("Son işlem geri alındı.")

    def save_pdf(self):
        if self.pdf_processor:
            output_path, _ = QFileDialog.getSaveFileName(self, "PDF Kaydet", "", "PDF Files (*.pdf)")
            if output_path:
                self.pdf_processor.save_pdf(output_path)
                QMessageBox.information(self, "Başarılı", f"PDF başarıyla kaydedildi:\n{output_path}")
                self.statusBar().showMessage(f"PDF kaydedildi: {output_path}")

    # --- DEĞİŞİKLİK BURADA ---
    def mouseMoveEvent(self, event):
        # Navigator varsa ve fare sol PDF alanının üzerindeyse önizlemeyi göster
        if self.navigator and self.left_page_label.underMouse():
            # Karmaşık dönüşümler yerine, doğrudan ana penceredeki fare pozisyonunu gönder
            self.navigator.show_preview(event.pos())
        elif self.navigator:
            # Fare başka bir yerdeyse önizlemeyi gizle
            self.navigator.clear_preview()
        super().mouseMoveEvent(event)

    # --- DEĞİŞİKLİK BİTTİ ---

    def keyPressEvent(self, event: QKeyEvent):
        # ... (Bu fonksiyon aynı kalıyor) ...
        if event.matches(QKeySequence.Undo):
            self.undo_last_action()
            return
        if not self.navigator:
            super().keyPressEvent(event)
            return
        key = event.key()
        if key == Qt.Key.Key_Right:
            self.navigator.next_page()
        elif key == Qt.Key.Key_Left:
            self.navigator.previous_page()
        elif key == Qt.Key.Key_Up:
            self.itemizer.decrease_level()
        elif key == Qt.Key.Key_Down:
            self.itemizer.increase_level()
        else:
            super().keyPressEvent(event)