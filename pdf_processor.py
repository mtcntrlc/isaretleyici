import fitz
import settings


class PDFProcessor:
    def add_item_on_click(self, page, event, itemizer, label_width, label_height):
        itemizer_state_before_add = itemizer.get_state()
        scale_factor_x = page.rect.width / label_width
        scale_factor_y = page.rect.height / label_height
        x = event.pos().x() * scale_factor_x
        y = event.pos().y() * scale_factor_y

        item_text = itemizer.get_next_item()
        font_size = settings.FONT_SIZE
        font_name = settings.FONT_NAME

        insert_point = fitz.Point(x, y)
        text_width = fitz.get_text_length(item_text, fontname=font_name, fontsize=font_size)
        text_height = font_size
        text_bbox = fitz.Rect(insert_point.x, insert_point.y - text_height, insert_point.x + text_width, insert_point.y)

        total_area = text_bbox + (-2, -2, 2, 2)
        original_pixmap = page.get_pixmap(clip=total_area)

        highlight = page.add_rect_annot(total_area)
        highlight.set_colors({"stroke": settings.DEFAULT_BACKGROUND_COLOR, "fill": settings.DEFAULT_BACKGROUND_COLOR})
        highlight.update(opacity=settings.DEFAULT_OPACITY)

        page.insert_text(insert_point, item_text, fontname=font_name, fontsize=font_size, color=(0, 0, 0))

        # Redo için daha fazla bilgi kaydediyoruz
        command = {
            "type": "ADD_ITEM",
            "page_num": page.number,
            "annot": highlight,
            "area": total_area,
            "snapshot": original_pixmap,
            "itemizer_state": itemizer_state_before_add,
            "text": item_text,  # Metnin kendisi
            "insert_point": insert_point  # ve konumu
        }
        return command

    def add_highlight_in_area(self, page, selection_rect, label_width, label_height):
        # ... (Bu fonksiyon aynı kalıyor) ...
        scale_factor_x = page.rect.width / label_width
        scale_factor_y = page.rect.height / label_height
        x0 = selection_rect.x() * scale_factor_x
        y0 = selection_rect.y() * scale_factor_y
        x1 = selection_rect.right() * scale_factor_x
        y1 = selection_rect.bottom() * scale_factor_y
        pdf_rect = fitz.Rect(x0, y0, x1, y1)
        original_pixmap = page.get_pixmap(clip=pdf_rect)
        words = page.get_text("words")
        highlights = []
        for word in words:
            word_rect = fitz.Rect(word[:4])
            if pdf_rect.intersects(word_rect):
                highlight = page.add_highlight_annot(word_rect)
                highlight.set_colors({"stroke": settings.DEFAULT_BACKGROUND_COLOR})
                highlight.update(opacity=settings.DEFAULT_OPACITY)
                highlights.append(highlight)
        if not highlights: return None
        command = {"type": "HIGHLIGHT", "page_num": page.number, "annots": highlights, "area": pdf_rect,
                   "snapshot": original_pixmap}
        return command

    def restore_snapshot(self, page, command):
        # ... (Bu fonksiyon aynı kalıyor) ...
        area_to_restore = command["area"]
        snapshot = command["snapshot"]
        page.insert_image(area_to_restore, pixmap=snapshot)
        if "annot" in command:
            page.delete_annot(command["annot"])
        elif "annots" in command:
            for annot in command["annots"]: page.delete_annot(annot)

    # --- YENİ VE TAMAMLANMIŞ FONKSİYON ---
    def reapply_action(self, page, command):
        """Geri alınmış bir komutu PDF üzerinde yeniden uygular."""
        if command.get("type") == "ADD_ITEM":
            # Madde ekleme işlemini yeniden çiz
            highlight = page.add_rect_annot(command["area"])
            highlight.set_colors(
                {"stroke": settings.DEFAULT_BACKGROUND_COLOR, "fill": settings.DEFAULT_BACKGROUND_COLOR})
            highlight.update(opacity=settings.DEFAULT_OPACITY)

            # Metni de yeniden ekle
            page.insert_text(
                command["insert_point"], command["text"],
                fontname=settings.FONT_NAME, fontsize=settings.FONT_SIZE,
                color=(0, 0, 0)
            )
            # Komut içindeki annot'u yeni oluşturulanla güncelle
            command["annot"] = highlight

        elif command.get("type") == "HIGHLIGHT":
            # Vurgulama işlemini yeniden yap
            new_highlights = []
            for old_annot in command["annots"]:
                new_annot = page.add_highlight_annot(old_annot.rect)
                new_annot.set_colors({"stroke": settings.DEFAULT_BACKGROUND_COLOR})
                new_annot.update(opacity=settings.DEFAULT_OPACITY)
                new_highlights.append(new_annot)
            # Komut içindeki annot listesini yeni oluşturulanlarla güncelle
            command["annots"] = new_highlights
    # --- BİTTİ ---