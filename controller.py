from PySide6.QtCore import QObject, Qt
from PySide6.QtGui import QAction, QKeySequence

class ShortcutController(QObject):
    def __init__(self, parent=None, pdf_processor=None, itemizer=None):
        super().__init__(parent)
        self.parent = parent
        self.pdf_processor = pdf_processor
        self.itemizer = itemizer

        # Reset işlevi için QAction (Ctrl+R)
        self.reset_action = QAction("Reset", self.parent)
        self.reset_action.setShortcut(QKeySequence("Ctrl+R"))
        self.reset_action.triggered.connect(self.perform_reset)
        self.parent.addAction(self.reset_action)

    def perform_reset(self):
        """Reset işlemini başlatır."""
        if self.itemizer:
            self.itemizer.reset_items()  # Itemizer'da sıfırlama işlemi
        if self.pdf_processor:
            self.pdf_processor.reset_items()  # PDFProcessor'da sıfırlama işlemi
        print("Sıfırlama işlemi tamamlandı.")

    def perform_undo(self):
        try:
            print("Undo kısayolu çalıştı.")
            if self.pdf_processor:
                self.pdf_processor.undo_last_item()
            if self.itemizer:
                self.itemizer.decrement_current_level()
                print(f"Itemizer mevcut madde: {self.itemizer.num_level}")
            self.parent.show_pages()  # Sayfa yenileniyor
            print("Undo işlemi tamamlandı.")
        except Exception as e:
            print(f"Undo sırasında bir hata oluştu: {e}")


