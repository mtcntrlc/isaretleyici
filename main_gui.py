from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, QPushButton
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
        self.itemizer = Itemizer() # Madde yönetimi için
        self.previewer = None
        self.init_ui()
        self.init_menu()
        # Diğer bileşenleriniz burada olmalı...

        # Kısayol kontrolcüsünü başlatma ve PDF ve itemizer modüllerini bağlama
        self.shortcut_controller = ShortcutController(self, self.pdf_processor, self.itemizer)




    def init_ui(self):
        self.setWindowTitle("PDF İşaretleyici")
        self.setGeometry(100, 100, 1200, 800)

        # PDF dosyası seçme butonu
        self.select_pdf_button = QPushButton("PDF Seç", self)
        self.select_pdf_button.clicked.connect(self.select_pdf)  # PDF seçme işlevini butona bağlayın
        self.select_pdf_button.move(50, 50)  # Düğmenin konumunu belirleyin

        self.left_page_label = QLabel(self)
        self.left_page_label.setGeometry(50, 100, 550, 600)  # İlk başta dar bir alan

        # Tıklama ve hareket olaylarını doğrudan modüllerdeki işlevlere yönlendirme
        # Tıklama ile madde ekleme
        self.left_page_label.mousePressEvent = lambda event: self.add_item_and_refresh(event)

        # İlk başta tam ekran kullanılmaz, butonun varlığına göre boyutlandırılır

        self.right_page_label = QLabel(self)
        self.right_page_label.setGeometry(600, 100, 550, 600)  # İlk başta dar bir alan



    def init_menu(self):
        """Üst barda PDF kaydetme menü seçeneğini ekler."""
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")

        # PDF Kaydetme menü seçeneği
        save_action = QAction("PDF'yi Kaydet", self)
        save_action.triggered.connect(self.save_pdf)
        file_menu.addAction(save_action)

    def reset_items(self):
        """PDF ve itemizer üzerinde sıfırlama işlemi."""
        if self.itemizer:
            self.itemizer.reset_items()
        if self.pdf_processor:
            self.pdf_processor.reset_items()
        print("MainGUI üzerinde sıfırlama işlemi tamamlandı.")

    def select_pdf(self):
        # Dosya seçme penceresi aç
        file_path, _ = QFileDialog.getOpenFileName(self, "PDF Dosyası Seç", "", "PDF Files (*.pdf)")
        if file_path:
            print(f"Seçilen dosya yolu: {file_path}")
            self.select_pdf_button.hide()  # PDF seçildikten sonra butonu gizle
            self.expand_labels()  # Boşluğu kullanmak için QLabels boyutlandır
            self.load_pdf(file_path)
        else:
            print("PDF dosyası seçilmedi.")

    def expand_labels(self):
        """PDF seçildikten sonra QLabel'leri genişletmek için çağrılır."""
        self.left_page_label.setGeometry(20, 20, 580, 750)  # Sol QLabel tüm pencereye yayılır
        self.right_page_label.setGeometry(600, 20, 580, 750)  # Sağ QLabel tüm pencereye yayılır
        self.left_page_label.setScaledContents(True)
        self.right_page_label.setScaledContents(True)

    def load_pdf(self, file_path):
        try:
            self.pdf_processor = PDFProcessor(file_path)
            self.previewer = Previewer(self.pdf_processor)
            print("PDF yüklendi ve işlenmeye hazır.")
            self.show_pages()
        except FileNotFoundError:
            print("PDF dosyası bulunamadı.")
        except Exception as e:
            print(f"PDF yüklenirken bir hata oluştu: {e}")

    def show_pages(self):
        """Sol ve sağ PDF sayfalarını gösterir."""
        if self.pdf_processor:
            temp_path = self.pdf_processor.temp_file_path
            # Sol sayfa önizlemesi
            left_pix = self.previewer.show_preview(self.pdf_processor.current_page)
            if left_pix and not left_pix.isNull():
                self.left_page_label.setPixmap(left_pix)  # scaled kaldırıldı

            # Sağ sayfa önizlemesi
            if self.pdf_processor.current_page < self.pdf_processor.get_page_count() - 1:
                right_pix = self.previewer.show_preview(self.pdf_processor.current_page + 1)
                if right_pix and not right_pix.isNull():
                    self.right_page_label.setPixmap(right_pix)  # scaled kaldırıldı

    def add_item_and_refresh(self, event):
        label_width = self.left_page_label.width()
        label_height = self.left_page_label.height()
        print(f"Tıklanan konum: ({event.x()}, {event.y()})")
        self.pdf_processor.add_item_on_click(event, self.itemizer, label_width, label_height)
        # Önizleme veya güncelleme işlemleri
        self.show_pages()
        print("Sayfa güncelleniyor.")

    # Dinamik gösterimi sağlayacak olan eventFilter işlevi:
    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseMove:
            mouse_pos = event.pos()
            self.show_preview(mouse_pos)
            return True
        return super().eventFilter(source, event)

    def undo_last_action(self):
        """Son işlemi geri alır."""
        self.shortcut_controller.perform_undo()
        self.show_pages()
        print("Undo işlemi tamamlandı.")

    def mousePressEvent(self, event):

        # Sol tıklama ile madde ekle ve bir sonraki öğeye geç
        if event.button() == Qt.LeftButton and self.left_page_label.underMouse():
            print("Sol tıklama algılandı, madde ekleniyor...")
            print(f"Mevcut öğe: {self.itemizer.get_current_item()}")
            self.pdf_processor.add_item_on_click(event, self.itemizer, event.pos().x(), event.pos().y())
            self.itemizer.increase_level()  # Bir sonraki öğeye geç
            print(f"Bir sonraki maddeye geçildi: {self.itemizer.get_next_item()}")
        else:
            print("Sol tıklama algılanmadı veya sol alanda değil.")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Right:  # Sağ ok tuşu
            self.next_page()
        elif event.key() == Qt.Key.Key_Left:  # Sol ok tuşu
            self.previous_page()
        elif event.key() == Qt.Key.Key_Down:  # Yukarı ok tuşu (bir üst katmana geçiş)
            self.itemizer.increase_level()
        elif event.key() == Qt.Key.Key_Up:  # Aşağı ok tuşu (bir alt katmana geçiş)
            self.itemizer.decrease_level()


    def next_page(self):
        if self.pdf_processor.get_current_page() < self.pdf_processor.get_page_count() - 1:
            self.pdf_processor.current_page += 1
            self.show_pages()  # Sayfaları güncelle

    def previous_page(self):
        if self.pdf_processor.get_current_page() > 0:
            self.pdf_processor.current_page -= 1
            self.show_pages()  # Sayfaları güncelle

    def save_pdf(self):
        if self.pdf_processor:
            output_path, _ = QFileDialog.getSaveFileName(self, "PDF Kaydet", "", "PDF Files (*.pdf)")
            if output_path:
                self.pdf_processor.save_pdf(output_path)
                print(f"PDF '{output_path}' olarak kaydedildi.")

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Undo):  # Ctrl+Z kısayolu
            self.undo_last_action()
        else:
            super().keyPressEvent(event)

    def keyPressEvent2(self, event):
        if event.matches(QKeySequence.Undo):  # Ctrl+Z kısayolu
            self.undo_last_action()
        else:
            super().keyPressEvent(event)