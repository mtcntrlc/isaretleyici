from PySide6.QtCore import QObject, Qt
from PySide6.QtGui import QAction, QKeySequence


class ShortcutController(QObject):
    def __init__(self, parent=None, pdf_processor=None, itemizer=None):
        super().__init__(parent)
        self.parent = parent
        self.pdf_processor = pdf_processor
        self.itemizer = itemizer

        self.reset_action = QAction("Reset", self.parent)
        self.reset_action.setShortcut(QKeySequence("Ctrl+R"))
        self.reset_action.triggered.connect(self.perform_reset)
        self.parent.addAction(self.reset_action)

    def perform_reset(self):
        if self.itemizer:
            self.itemizer.reset_items()
        if self.pdf_processor:
            self.pdf_processor.reset_items()
        print("Sıfırlama işlemi tamamlandı.")
        self.parent.show_pages()  # Arayüzü de yenileyelim

    def perform_undo(self):
        try:
            print("Undo kısayolu çalıştı.")
            if self.pdf_processor and self.itemizer:
                # 1. PDF üzerindeki işlemi geri al ve eski itemizer durumunu al
                previous_itemizer_state = self.pdf_processor.undo_last_item()

                # 2. Eğer işlem başarılı olduysa (durum döndüyse), itemizer'ı bu duruma geri yükle
                if previous_itemizer_state:
                    self.itemizer.restore_state(previous_itemizer_state)

                # 3. Arayüzü yenile
                self.parent.show_pages()
                print("Undo işlemi ve sayaç senkronizasyonu tamamlandı.")
        except Exception as e:
            print(f"Undo sırasında bir hata oluştu: {e}")