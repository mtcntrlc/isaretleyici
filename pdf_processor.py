import fitz
import settings

print(f"pdf_processor.py: 'settings' modülü başarıyla yüklendi -> {settings}")


class PDFProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.pdf_document = fitz.open(file_path)
        self.current_page = 0
        self.temp_file_path = "temp_output.pdf"
        self.command_stack = []

    def get_page(self, page_num):
        if 0 <= page_num < len(self.pdf_document):
            return self.pdf_document[page_num]
        return None

    def get_current_page(self):
        return self.current_page

    def get_page_count(self):
        return self.pdf_document.page_count

    def reset_items(self):
        self.command_stack.clear()
        self.pdf_document.close()
        self.pdf_document = fitz.open(self.file_path)
        print("PDFProcessor sıfırlandı, orijinal duruma dönüldü.")
        self.save_temp_pdf()

    def add_item_on_click(self, event, itemizer, label_width, label_height):
        itemizer_state_before_add = itemizer.get_state()
        page = self.pdf_document[self.current_page]
        page_width, page_height = page.rect.width, page.rect.height
        scale_factor_x = page_width / label_width
        scale_factor_y = page_height / label_height
        x = event.pos().x() * scale_factor_x
        y = event.pos().y() * scale_factor_y
        item_text = itemizer.get_next_item()
        print(f"Madde ekleniyor: {item_text} ")

        font_size = settings.FONT_SIZE
        font_name = settings.FONT_NAME

        insert_point = fitz.Point(x, y)
        text_width = fitz.get_text_length(item_text, fontname=font_name, fontsize=font_size)
        text_height = font_size
        text_bbox = fitz.Rect(
            insert_point.x, insert_point.y - text_height,
                            insert_point.x + text_width, insert_point.y
        )

        # Hem metni hem de arka planı kapsayacak genel alanı belirle
        total_area = text_bbox + (-2, -2, 2, 2)

        # --- YENİ MANTIK: Anlık Görüntü Al ---
        # Değişiklik yapmadan önce, o alanın bir görüntüsünü sakla
        original_pixmap = page.get_pixmap(clip=total_area)
        # --- BİTTİ ---

        background_bbox = text_bbox + (-2, -2, 2, 2)
        highlight = page.add_rect_annot(background_bbox)

        highlight.set_colors({"stroke": settings.DEFAULT_BACKGROUND_COLOR, "fill": settings.DEFAULT_BACKGROUND_COLOR})
        highlight.update(opacity=settings.DEFAULT_OPACITY)

        page.insert_text(
            insert_point,
            item_text,
            fontname=font_name,
            fontsize=font_size,
            color=(0, 0, 0)
        )
        command = {
            "page_num": self.current_page,
            "annot": highlight,
            "area": total_area,  # Artık sadece alanı saklıyoruz
            "snapshot": original_pixmap,  # ve anlık görüntüyü
            "itemizer_state": itemizer_state_before_add
        }
        self.command_stack.append(command)
        self.save_temp_pdf()

    def undo_last_item(self):
        if not self.command_stack:
            print("Geri alınacak madde yok.")
            return None
        last_command = self.command_stack.pop()
        page_num = last_command["page_num"]
        annot_to_delete = last_command["annot"]
        area_to_restore = last_command["area"]
        snapshot = last_command["snapshot"]  # Sakladığımız anlık görüntüyü al
        previous_itemizer_state = last_command["itemizer_state"]

        page = self.get_page(page_num)
        if page:
            # --- YENİ MANTIK: Anlık Görüntüyü Geri Yükle ---
            # Beyaz kutu çizmek yerine, sakladığımız görüntüyü geri yapıştırıyoruz.
            page.insert_image(area_to_restore, pixmap=snapshot)
            # --- BİTTİ ---

            page.delete_annot(annot_to_delete)
            self.save_temp_pdf()
            print("Son madde (anlık görüntü ile) başarıyla geri alındı.")
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