from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, QMessageBox, QColorDialog, \
    QRubberBand
from PySide6.QtGui import QKeyEvent, QKeySequence, QAction, QMouseEvent
from PySide6.QtCore import Qt, QPoint, QRect
from document_manager import DocumentManager
from pdf_processor import PDFProcessor
from itemizer import Itemizer
from navigator import Navigator
from previewer import Previewer
from undo_manager import UndoManager
from actions import (
    OpenFileAction, SaveAction, SaveAsAction, QuitAction,
    UndoAction, RedoAction, ResetAction, GoToPageAction,
    ChangeColorAction, SettingsAction
)
import settings


class MainGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.document_manager = None
        self.pdf_processor = PDFProcessor()
        self.itemizer = Itemizer(settings.DEFAULT_NUMBERING_STRATEGY)
        self.previewer = None
        self.navigator = None
        self.undo_manager = None
        self.current_save_path = None
        self.current_mode = settings.WorkMode.ADD_ITEM
        self.selection_start_pos = None

        self.open_action = OpenFileAction(self)
        self.save_action = SaveAction(self)
        self.save_as_action = SaveAsAction(self)
        self.quit_action = QuitAction(self)
        self.undo_action = UndoAction(self)
        self.redo_action = RedoAction(self)
        self.reset_action = ResetAction(self)
        self.go_to_page_action = GoToPageAction(self)
        self.change_color_action = ChangeColorAction(self)
        self.settings_action = SettingsAction(self)

        self.init_ui()
        self.init_menu()
        self.statusBar().showMessage("Lütfen bir PDF dosyası seçin.")
        self.setMouseTracking(True)

    def init_ui(self):
        self.setWindowTitle("PDF İşaretleyici")
        self.setGeometry(100, 100, 1200, 800)

        self.open_pdf_button = QPushButton("PDF Aç", self)
        self.open_pdf_button.clicked.connect(self.open_action.execute)
        self.open_pdf_button.move(50, 50)

        # "Renk Seç" butonu buradan kaldırıldı.

        self.add_item_mode_button = QPushButton("Madde Ekle", self)
        self.add_item_mode_button.setCheckable(True)
        self.add_item_mode_button.setChecked(True)
        self.add_item_mode_button.clicked.connect(lambda: self.set_mode(settings.WorkMode.ADD_ITEM))
        self.add_item_mode_button.move(150, 50)  # Konumu güncellendi

        self.highlight_mode_button = QPushButton("Vurgula", self)
        self.highlight_mode_button.setCheckable(True)
        self.highlight_mode_button.clicked.connect(lambda: self.set_mode(settings.WorkMode.HIGHLIGHT))
        self.highlight_mode_button.move(250, 50)  # Konumu güncellendi

        self.left_page_label = QLabel(self)
        self.left_page_label.setGeometry(50, 100, 550, 600)
        self.left_page_label.setMouseTracking(True)

        self.right_page_label = QLabel(self)
        self.right_page_label.setGeometry(600, 100, 550, 600)
        self.right_page_label.setMouseTracking(True)

        self.rubber_band = QRubberBand(QRubberBand.Rectangle, self.left_page_label)

    def init_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.quit_action)

        edit_menu = menubar.addMenu("Edit")
        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.reset_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.settings_action)

        tools_menu = menubar.addMenu("Tools")
        tools_menu.addAction(self.change_color_action)

        go_menu = menubar.addMenu("Go")
        go_menu.addAction(self.go_to_page_action)

    def set_mode(self, mode):
        self.current_mode = mode
        self.add_item_mode_button.setChecked(mode == settings.WorkMode.ADD_ITEM)
        self.highlight_mode_button.setChecked(mode == settings.WorkMode.HIGHLIGHT)
        self.statusBar().showMessage(f"Mod değiştirildi: {mode.name}")

    def mousePressEvent(self, event: QMouseEvent):
        if self.left_page_label.underMouse() and event.button() == Qt.LeftButton:
            if self.current_mode == settings.WorkMode.ADD_ITEM:
                self.add_item_and_refresh(event)
            elif self.current_mode == settings.WorkMode.HIGHLIGHT:
                self.selection_start_pos = self.left_page_label.mapFromGlobal(event.globalPos())
                self.rubber_band.setGeometry(QRect(self.selection_start_pos, QPoint(0, 0)))
                self.rubber_band.show()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.current_mode == settings.WorkMode.HIGHLIGHT and self.selection_start_pos is not None and event.buttons() & Qt.LeftButton:
            pos = self.left_page_label.mapFromGlobal(event.globalPos())
            self.rubber_band.setGeometry(QRect(self.selection_start_pos, pos).normalized())

        if self.current_mode == settings.WorkMode.ADD_ITEM and self.navigator and self.left_page_label.underMouse():
            self.navigator.show_preview(event.pos())
        elif self.navigator:
            self.navigator.clear_preview()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self.current_mode == settings.WorkMode.HIGHLIGHT and self.selection_start_pos is not None and event.button() == Qt.LeftButton:
            self.rubber_band.hide()
            selection_rect = self.rubber_band.geometry()
            self.add_highlight_and_refresh(selection_rect)
            self.selection_start_pos = None
        super().mouseReleaseEvent(event)

    def add_highlight_and_refresh(self, selection_rect):
        if not self.document_manager or selection_rect.isEmpty(): return
        current_page = self.document_manager.get_current_page()
        if not current_page: return
        command = self.pdf_processor.add_highlight_in_area(current_page, selection_rect, self.left_page_label.width(),
                                                           self.left_page_label.height())
        if command and self.undo_manager:
            self.undo_manager.register_action(command)
        self.document_manager.save_temp()
        self.show_pages()

    def add_item_and_refresh(self, event):
        if not self.document_manager: return

        relative_event_pos = self.left_page_label.mapFromGlobal(event.globalPos())
        new_event = QMouseEvent(event.type(), relative_event_pos, event.button(), event.buttons(), event.modifiers())

        if self.navigator: self.navigator.clear_preview()
        current_page = self.document_manager.get_current_page()
        if not current_page: return
        command = self.pdf_processor.add_item_on_click(current_page, new_event, self.itemizer,
                                                       self.left_page_label.width(), self.left_page_label.height())
        if command and self.undo_manager: self.undo_manager.register_action(command)
        self.document_manager.save_temp()
        self.show_pages()

    def load_pdf(self, file_path):
        try:
            # Butonları gizle
            self.open_pdf_button.hide()
            self.add_item_mode_button.hide()
            self.highlight_mode_button.hide()

            self.document_manager = DocumentManager(file_path)
            self.previewer = Previewer(self.document_manager)
            self.navigator = Navigator(self, self.document_manager, self.itemizer)
            self.undo_manager = UndoManager(self.document_manager, self.pdf_processor, self.itemizer)
            self.statusBar().showMessage(f"PDF yüklendi: {file_path}")
            self.show_pages()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"PDF yüklenirken bir hata oluştu: {e}")

    def show_pages(self):
        if not self.document_manager: return
        left_pix = self.previewer.show_preview(self.document_manager.current_page_index)
        self.left_page_label.setPixmap(left_pix if not left_pix.isNull() else None)
        if self.document_manager.current_page_index < self.document_manager.get_page_count() - 1:
            right_pix = self.previewer.show_preview(self.document_manager.current_page_index + 1)
            self.right_page_label.setPixmap(right_pix if not right_pix.isNull() else None)
        else:
            self.right_page_label.clear()
        self.statusBar().showMessage(f"Sayfa {self.document_manager.current_page_index + 1} gösteriliyor...")

    def expand_labels(self):
        self.left_page_label.setGeometry(20, 20, 580, 750)
        self.right_page_label.setGeometry(600, 20, 580, 750)
        self.left_page_label.setScaledContents(True)
        self.right_page_label.setScaledContents(True)

    def keyPressEvent(self, event: QKeyEvent):
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