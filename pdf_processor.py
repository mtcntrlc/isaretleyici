import fitz
import settings


class PDFProcessor:
    def add_item_on_click(self, page, event, itemizer, label_width, label_height):
        """Verilen sayfa üzerine madde ekler ve geri alma için gereken bilgileri döndürür."""
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

        command = {
            "page_num": page.number,
            "annot": highlight,
            "area": total_area,
            "snapshot": original_pixmap,
            "itemizer_state": itemizer_state_before_add
        }
        return command

    def restore_snapshot(self, page, command):
        """UndoManager'dan gelen komuta göre anlık görüntüyü geri yükler."""
        area_to_restore = command["area"]
        snapshot = command["snapshot"]
        annot_to_delete = command["annot"]

        page.insert_image(area_to_restore, pixmap=snapshot)
        page.delete_annot(annot_to_delete)