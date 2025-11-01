from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, QMessageBox, QColorDialog
from PySide6.QtGui import QKeyEvent, QKeySequence, QAction
from PySide6.QtCore import Qt
from document_manager import DocumentManager
from pdf_processor import PDFProcessor
from itemizer import Itemizer
from navigator import Navigator
from previewer import Previewer
from undo_manager import UndoManager
import settings


class MainGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.document_manager = None
        self.pdf_processor = PDFProcessor()
        self.itemizer = Itemizer()
        self.previewer = None
        self.navigator = None
        self.undo_manager = None
        self.current_save_path = None
        self.init_ui()
        self.init_menu()
        self.statusBar().showMessage("Lütfen bir PDF dosyası seçin.")
        self.setMouseTracking(True)

    def init_ui(self):
        self.setWindowTitle("PDF İşaretleyici")
        self.setGeometry(100, 100, 1200, 800)
        self.open_pdf_button = QPushButton("PDF Aç", self)
        self.open_pdf_button.clicked.connect(self.open_pdf)
        self.open_pdf_button.move(50, 50)
        self.select_color_button = QPushButton("Renk Seç", self)
        self.select_color_button.clicked.connect(self.select_color)
        self.select_color_button.move(150, 50)
        self.left_page_label = QLabel(self)
        self.left_page_label.setGeometry(50, 100, 550, 600)
        self.left_page_label.mousePressEvent = lambda event: self.add_item_and_refresh(event)
        self.left_page_label.setMouseTracking(True)
        self.right_page_label = QLabel(self)
        self.right_page_label.setGeometry(600, 100, 550, 600)
        self.right_page_label.setMouseTracking(True)

    def init_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        open_action = QAction("Open...", self);
        open_action.setShortcut(QKeySequence.Open);
        open_action.triggered.connect(self.open_pdf);
        file_menu.addAction(open_action)
        self.save_action = QAction("Save", self);
        self.save_action.setShortcut(QKeySequence.Save);
        self.save_action.triggered.connect(self.save_pdf);
        self.save_action.setEnabled(False);
        file_menu.addAction(self.save_action)
        save_as_action = QAction("Save As...", self);
        save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"));
        save_as_action.triggered.connect(self.save_pdf_as);
        file_menu.addAction(save_as_action)
        file_menu.addSeparator()
        quit_action = QAction("Quit", self);
        quit_action.setShortcut(QKeySequence.Quit);
        quit_action.triggered.connect(self.close);
        file_menu.addAction(quit_action)

    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            settings.DEFAULT_BACKGROUND_COLOR = (color.redF(), color.greenF(), color.blueF())
            self.statusBar().showMessage(f"Yeni renk seçildi.")
            if self.navigator: self.navigator.update_style()

    def open_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "PDF Dosyası Seç", "", "PDF Files (*.pdf)")
        if file_path:
            self.open_pdf_button.hide()
            self.expand_labels()
            self.load_pdf(file_path)
            self.current_save_path = None
            self.save_action.setEnabled(False)

    def load_pdf(self, file_path):
        try:
            self.document_manager = DocumentManager(file_path)
            self.previewer = Previewer(self.document_manager)
            self.navigator = Navigator(self, self.document_manager, self.itemizer)
            self.undo_manager = UndoManager(self.document_manager, self.pdf_processor, self.itemizer)
            self.statusBar().showMessage(f"PDF yüklendi: {file_path}")
            self.show_pages()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"PDF yüklenirken bir hata oluştu: {e}")

    def add_item_and_refresh(self, event):
        if not self.document_manager: return
        if self.navigator: self.navigator.clear_preview()

        current_page = self.document_manager.get_current_page()
        if not current_page: return

        command = self.pdf_processor.add_item_on_click(current_page, event, self.itemizer, self.left_page_label.width(),
                                                       self.left_page_label.height())

        if command and self.undo_manager:
            self.undo_manager.register_action(command)

        self.document_manager.save_temp()
        self.show_pages()

    def undo_last_action(self):
        if self.undo_manager and self.undo_manager.undo():
            self.document_manager.save_temp()
            self.show_pages()
            self.statusBar().showMessage("Son işlem geri alındı.")

    def save_pdf(self):
        if not self.document_manager: return
        if self.current_save_path:
            if self.document_manager.save(self.current_save_path):
                QMessageBox.information(self, "Başarılı", f"Değişiklikler kaydedildi.")
        else:
            self.save_pdf_as()

    def save_pdf_as(self):
        if not self.document_manager: return
        output_path, _ = QFileDialog.getSaveFileName(self, "PDF'i Farklı Kaydet", "", "PDF Files (*.pdf)")
        if output_path:
            if self.document_manager.save(output_path):
                self.current_save_path = output_path
                self.save_action.setEnabled(True)
                QMessageBox.information(self, "Başarılı", f"PDF başarıyla kaydedildi.")

    def show_pages(self):
        if not self.document_manager: return
        left_pix = self.previewer.show_preview(self.document_manager.current_page_index)
        self.left_page_label.setPixmap(left_pix if not left_pix.isNull() else None)
        if self.document_manager.current_page_index < self.document_manager.get_page_count() - 1:
            right_pix = self.previewer.show_preview(self.document_manager.current_page_index + 1)
            self.right_page_label.setPixmap(right_pix if not right_pix.isNull() else None)
        else:
            self.right_page_label.clear()
        self.statusBar().showMessage(
            f"Sayfa {self.document_manager.current_page_index + 1} gösteriliyor. Sıradaki madde: {self.itemizer.get_current_item_display()}")

    # --- DÜZELTME BURADA ---
    def expand_labels(self):
        self.left_page_label.setGeometry(20, 20, 580, 750)
        self.right_page_label.setGeometry(600, 20, 580, 750)
        # Eksik olan ölçekleme komutlarını geri ekliyoruz
        self.left_page_label.setScaledContents(True)
        self.right_page_label.setScaledContents(True)

    # --- DÜZELTME BİTTİ ---

    def mouseMoveEvent(self, event):
        if self.navigator and self.left_page_label.underMouse():
            self.navigator.show_preview(event.pos())
        elif self.navigator:
            self.navigator.clear_preview()
        super().mouseMoveEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
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