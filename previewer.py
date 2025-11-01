from PySide6.QtGui import QImage, QPixmap
import fitz

class Previewer:
    def __init__(self, document_manager):
        self.document_manager = document_manager

    def show_preview(self, page_num):
        page = self.document_manager.get_page(page_num)
        if page is None:
            return QPixmap()

        zoom_x, zoom_y = 2.0, 2.0
        mat = fitz.Matrix(zoom_x, zoom_y)
        pix = page.get_pixmap(matrix=mat)

        img_format = QImage.Format_RGBA8888 if pix.alpha else QImage.Format_RGB888
        qimage = QImage(pix.samples, pix.width, pix.height, pix.stride, img_format)
        return QPixmap.fromImage(qimage)