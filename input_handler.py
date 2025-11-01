from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtGui import QKeyEvent, QMouseEvent

class InputHandler(QObject):
    # Sinyaller aynı kalıyor
    next_page_triggered = Signal()
    prev_page_triggered = Signal()
    increase_level_triggered = Signal()
    decrease_level_triggered = Signal()
    add_item_triggered = Signal(QMouseEvent)

    def __init__(self, parent=None):
        super().__init__(parent)

    def handle_key_press(self, event: QKeyEvent):
        """Klavye tuşlarını yorumlar ve uygun sinyali yayınlar."""
        key = event.key()
        if key == Qt.Key.Key_Right:
            self.next_page_triggered.emit()
        elif key == Qt.Key.Key_Left:
            self.prev_page_triggered.emit()
        elif key == Qt.Key.Key_Up:
            self.decrease_level_triggered.emit()
        elif key == Qt.Key.Key_Down:
            self.increase_level_triggered.emit()

    def handle_mouse_press(self, event: QMouseEvent):
        """Fare tıklamasını yorumlar ve SADECE sol tuşa basıldıysa sinyal yayınlar."""
        if event.button() == Qt.LeftButton:
            self.add_item_triggered.emit(event)