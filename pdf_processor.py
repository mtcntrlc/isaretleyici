import fitz  # PyMuPDF


class PDFProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.pdf_document = fitz.open(file_path)
        self.current_page = 0
        self.temp_file_path = "temp_output.pdf"

        self.history = []
        # Başlangıç durumunu (hiçbir şey eklenmemiş halini) geçmişe ekle
        self.save_state_to_history(None)

    def save_state_to_history(self, itemizer_state):
        """PDF'in o anki bir kopyasını ve itemizer durumunu geçmiş listesine ekler."""
        pdf_copy = fitz.open(stream=self.pdf_document.write(), filetype="pdf")
        self.history.append((pdf_copy, itemizer_state))
        print(f"Yeni durum geçmişe eklendi. Toplam durum sayısı: {len(self.history)}")

    def get_page(self, page_num):
        if 0 <= page_num < len(self.pdf_document):
            return self.pdf_document[page_num]
        return None

    def get_current_page(self):
        return self.current_page

    def get_page_count(self):
        return self.pdf_document.page_count

    def reset_items(self):
        if self.history:
            # Geçmişi temizle ve sadece orijinal, ilk durumu bırak
            original_doc_copy, _ = self.history[0]
            self.pdf_document = fitz.open(stream=original_doc_copy.write(), filetype="pdf")
            self.history = self.history[:1]
        print("PDFProcessor sıfırlandı, orijinal duruma dönüldü.")
        self.save_temp_pdf()

    def add_item_on_click(self, event, itemizer, label_width, label_height):
        page = self.pdf_document[self.current_page]
        page_width, page_height = page.rect.width, page.rect.height

        scale_factor_x = page_width / label_width
        scale_factor_y = page_height / label_height

        x = event.pos().x() * scale_factor_x
        y = event.pos().y() * scale_factor_y

        # Önce maddeyi al, sayaç ilerlesin
        item_text = itemizer.get_next_item()
        print(f"Madde ekleniyor: {item_text} ")

        font_size = 12
        font_name = "times-bold"
        insert_point = fitz.Point(x, y)

        text_width = fitz.get_text_length(item_text, fontname=font_name, fontsize=font_size)
        text_height = font_size

        text_bbox = fitz.Rect(
            insert_point.x, insert_point.y - text_height,
                            insert_point.x + text_width, insert_point.y
        )

        background_bbox = text_bbox + (-2, -2, 2, 2)
        highlight = page.add_rect_annot(background_bbox)
        highlight.set_colors({"stroke": (209 / 255, 199 / 255, 8 / 255), "fill": (209 / 255, 199 / 255, 8 / 255)})
        highlight.update(opacity=0.5)

        page.insert_text(
            insert_point,
            item_text,
            fontname=font_name,
            fontsize=font_size,
            color=(0, 0, 0)
        )

        # --- MANTIK DÜZELTMESİ BURADA ---
        # İşlem bittikten SONRA o anki durumu kaydet
        current_itemizer_state = itemizer.get_state()
        self.save_state_to_history(current_itemizer_state)

        self.save_temp_pdf()

    def undo_last_item(self):
        if len(self.history) < 2:
            print("Geri alınacak madde yok.")
            return None

        # 1. Mevcut (en son) durumu listeden at
        self.history.pop()

        # 2. Şimdi listenin sonundaki durum, geri dönmek istediğimiz bir önceki durumdur
        previous_doc_copy, previous_itemizer_state = self.history[-1]

        # 3. Mevcut PDF belgesini, geçmişteki o "sağlam" kopya ile değiştir
        self.pdf_document = fitz.open(stream=previous_doc_copy.write(), filetype="pdf")

        self.save_temp_pdf()
        print(f"Bir önceki duruma geri dönüldü. Kalan durum sayısı: {len(self.history)}")

        return previous_itemizer_state

    def save_temp_pdf(self):
        try:
            self.pdf_document.save(self.temp_file_path)
        except Exception as e:
            print(f"Geçici PDF kaydedilemedi: {e}")

    def save_pdf(self, output_path):
        try:
            self.pdf_document.save(output_path)
            print(f"PDF '{output_path}' olarak kaydedildi.")
        except Exception as e:
            print(f"PDF kaydedilemedi: {e}")