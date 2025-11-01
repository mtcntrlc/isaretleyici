from PySide6.QtWidgets import QFileDialog, QMessageBox, QColorDialog, QInputDialog
from PySide6.QtGui import QAction, QKeySequence
import settings
# Yeni ayarlar penceremizi import ediyoruz
from settings_window import SettingsWindow

class BaseAction(QAction):
    def __init__(self, text, parent, shortcut=None):
        super().__init__(text, parent)
        self.main_window = parent
        if shortcut:
            self.setShortcut(shortcut)
        self.triggered.connect(self.execute)

    def execute(self):
        raise NotImplementedError

# ... (OpenFileAction, SaveAction, SaveAsAction, QuitAction, UndoAction, RedoAction, ResetAction, GoToPageAction sınıfları aynı kalıyor) ...
class OpenFileAction(BaseAction):
    def __init__(self, parent):
        super().__init__("Open...", parent, QKeySequence.Open)
    def execute(self):
        file_path, _ = QFileDialog.getOpenFileName(self.main_window, "PDF Dosyası Seç", "", "PDF Files (*.pdf)")
        if file_path:
            self.main_window.open_pdf_button.hide()
            self.main_window.add_item_mode_button.show()
            self.main_window.highlight_mode_button.show()
            self.main_window.expand_labels()
            self.main_window.load_pdf(file_path)
            self.main_window.current_save_path = None
            self.main_window.save_action.setEnabled(False)

class SaveAction(BaseAction):
    def __init__(self, parent):
        super().__init__("Save", parent, QKeySequence.Save)
        self.setEnabled(False)
    def execute(self):
        if not self.main_window.document_manager: return
        if self.main_window.current_save_path:
            if self.main_window.document_manager.save(self.main_window.current_save_path):
                QMessageBox.information(self.main_window, "Başarılı", "Değişiklikler kaydedildi.")
        else:
            self.main_window.save_as_action.execute()

class SaveAsAction(BaseAction):
    def __init__(self, parent):
        super().__init__("Save As...", parent, QKeySequence("Ctrl+Shift+S"))
    def execute(self):
        if not self.main_window.document_manager: return
        output_path, _ = QFileDialog.getSaveFileName(self.main_window, "PDF'i Farklı Kaydet", "", "PDF Files (*.pdf)")
        if output_path:
            if self.main_window.document_manager.save(output_path):
                self.main_window.current_save_path = output_path
                self.main_window.save_action.setEnabled(True)
                QMessageBox.information(self.main_window, "Başarılı", f"PDF başarıyla kaydedildi.")

class QuitAction(BaseAction):
    def __init__(self, parent):
        super().__init__("Quit", parent, QKeySequence.Quit)
    def execute(self):
        self.main_window.close()

class UndoAction(BaseAction):
    def __init__(self, parent):
        super().__init__("Undo", parent, QKeySequence.Undo)
    def execute(self):
        if self.main_window.undo_manager and self.main_window.undo_manager.undo():
            self.main_window.document_manager.save_temp()
            self.main_window.show_pages()

class RedoAction(BaseAction):
    def __init__(self, parent):
        super().__init__("Redo", parent, QKeySequence.Redo)
    def execute(self):
        if self.main_window.undo_manager and self.main_window.undo_manager.redo():
            self.main_window.document_manager.save_temp()
            self.main_window.show_pages()

class ResetAction(BaseAction):
    def __init__(self, parent):
        super().__init__("Reset", parent, QKeySequence("Ctrl+R"))
    def execute(self):
        if self.main_window.document_manager:
            self.main_window.document_manager.reset()
            self.main_window.itemizer.reset()
            if self.main_window.undo_manager: self.main_window.undo_manager.reset()
            self.main_window.show_pages()

class GoToPageAction(BaseAction):
    def __init__(self, parent):
        super().__init__("Go to Page...", parent, QKeySequence("Ctrl+G"))
    def execute(self):
        if not self.main_window.document_manager: return
        page_count = self.main_window.document_manager.get_page_count()
        current_page = self.main_window.document_manager.current_page_index + 1
        page_num, ok = QInputDialog.getInt(self.main_window, "Go to Page", f"Sayfa Numarası (1-{page_count}):", current_page, 1, page_count)
        if ok:
            self.main_window.document_manager.current_page_index = page_num - 1
            self.main_window.show_pages()

class ChangeColorAction(BaseAction):
    def __init__(self, parent):
        super().__init__("Change Annotation Color...", parent)

    def execute(self):
        color = QColorDialog.getColor()
        if color.isValid():
            settings.DEFAULT_BACKGROUND_COLOR = (color.redF(), color.greenF(), color.blueF())
            if self.main_window.navigator:
                self.main_window.navigator.update_style()
            self.main_window.statusBar().showMessage("Yeni renk seçildi.")

# --- YENİ AKSİYON SINIFI ---
class SettingsAction(BaseAction):
    def __init__(self, parent):
        # Mac için standart kısayol Ctrl+, (virgül)
        super().__init__("Preferences...", parent, QKeySequence("Ctrl+,"))

    def execute(self):
        settings_dialog = SettingsWindow(self.main_window)
        # exec() pencereyi açar ve kullanıcı kapatana kadar bekler
        result = settings_dialog.exec()

        # Eğer kullanıcı "OK" butonuna bastıysa
        if result:
            self.main_window.statusBar().showMessage("Ayarlar güncellendi.")
            # Renk değişmiş olabileceğinden, navigator'ın stilini güncelle
            if self.main_window.navigator:
                self.main_window.navigator.update_style()
# --- BİTTİ ---