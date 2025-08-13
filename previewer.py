from PySide6.QtGui import QImage, QPixmap
import fitz  # PyMuPDF

class Previewer:
    def __init__(self, pdf_processor):
        self.pdf_processor = pdf_processor

    def show_preview(self, page_num):
        """Belirtilen sayfayı yüksek çözünürlükte önizlemede gösterir."""
        page = self.pdf_processor.get_page(page_num)
        if page is None:
            print("Sayfa yüklenemedi, geçersiz sayfa numarası.")
            return QPixmap()  # Boş QPixmap döndür

        # Yüksek çözünürlük için zoom ayarları
        zoom_x, zoom_y = 2.0, 2.0
        mat = fitz.Matrix(zoom_x, zoom_y)
        pix = page.get_pixmap(matrix=mat)

        # Pixmap'i QImage'e dönüştür
        img_format = QImage.Format_RGBA8888 if pix.alpha else QImage.Format_RGB888
        img = QImage(pix.samples, pix.width, pix.height, pix.stride, img_format)

        # QImage'i QPixmap'e dönüştür ve döndür
        qpixmap = QPixmap.fromImage(img)
        return qpixmap
