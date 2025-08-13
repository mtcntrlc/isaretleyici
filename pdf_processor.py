import fitz  # PyMuPDF
import itemizer

class PDFProcessor:
    def __init__(self, file_path):
        self.pdf_document = fitz.open(file_path)
        self.current_page = 0
        self.temp_file_path = "temp_output.pdf"  # Geçici dosya yolu
        self.items_added = []  # Yapı: (page_num, [annot1, annot2, ...], item_text)
        # ... (diğer değişkenler)
        self.backup_path = "temp_output.pdf"

    def get_page(self, page_num):
        if 0 <= page_num < len(self.pdf_document):
            return self.pdf_document[page_num]
        return None

    def get_current_page(self):
        return self.current_page

    def get_page_count(self):
        return self.pdf_document.page_count  # Toplam sayfa sayısını int olarak döndürmeli

    def add_item(self, item, position):
        # ... madde ekleme işlemi ...
        self.items_added.append((item, position))

    def reset_items(self):
        """Eklenen maddeleri sıfırlar."""
        self.items_added.clear()
        print("PDFProcessor üzerindeki maddeler temizlendi.")

    # pdf_processor.py içindeki add_item_on_click fonksiyonunda değişiklikler:

    def add_item_on_click(self, event, itemizer, label_width, label_height):
        # PDF sayfasının boyutunu al
        current_item = itemizer.get_current_item()  # Geçerli maddeyi itemizer'dan al
        print(f"Madde ekleniyor: {current_item} ")
        page = self.pdf_document[self.current_page]
        page_width, page_height = page.rect.width, page.rect.height

        # Ölçek faktörünü hesapla
        scale_factor_x = page_width / label_width
        scale_factor_y = page_height / label_height

        # Ekran koordinatlarını PDF koordinatlarına dönüştür
        x = event.pos().x() * scale_factor_x
        y = event.pos().y() * scale_factor_y

        # Metin pozisyonunu PDF koordinatlarına göre ayarla
        current_position = fitz.Point(x, y)

        # Yeni maddeyi al ve ekle
        item_text = itemizer.get_next_item()
        font_size = 12
        font_name = "times-bold"
        line_height = font_size * 1.2

        # Her karakter için dikdörtgen ve metni birlikte oluştur

        # Her karakter için oluşturulan annot'ları saklamak için liste
        annots = []

        for char in item_text:
            # Arka plan dikdörtgenini metne göre daha fazla yukarı kaydırıyoruz
            char_rect = fitz.Rect(
                current_position - fitz.Point(0, line_height * 0.8),  # Arka planı daha da yukarı çekiyoruz
                current_position + fitz.Point(font_size * 0.6, line_height * 0.4)
            )

            # Arka plan dikdörtgenini ekle
            highlight = page.add_rect_annot(char_rect)
            highlight.set_colors({"stroke": (209 / 255, 199 / 255, 8 / 255), "fill": (209 / 255, 199 / 255, 8 / 255)})
            highlight.update(opacity=0.5)
            annots.append(highlight)  # Annot'ları listeye ekle

            # Harfi ekle
            page.insert_text(
                current_position, char,
                fontname=font_name,
                fontsize=font_size,
                color=(0, 0, 0)
            )

            # Bir sonraki harf için pozisyonu güncelle
            current_position += fitz.Point(font_size * 0.6, 0)

            # Eklenen annot'ları ve bilgileri kaydet
        self.items_added.append((self.current_page, annots, item_text))

        # Geçici dosyayı kaydet ve sayfayı güncelle
        self.save_temp_pdf()

        # add_item_on_click içinde:
        print(f"Eklenen madde pozisyonu: {current_position}")


    def save_temp_pdf(self):
        """PDF dosyasını geçici bir dosyaya kaydeder."""
        try:
            self.pdf_document.save(self.temp_file_path)
            print(f"Geçici PDF kaydedildi: {self.temp_file_path}")
        except Exception as e:
            print(f"Geçici PDF kaydedilemedi: {e}")

    def save_pdf(self, output_path):
        """Son değişiklikleri kalıcı olarak kaydeder."""
        try:
            self.pdf_document.save(output_path)
            print(f"PDF '{output_path}' olarak kaydedildi.")
        except Exception as e:
            print(f"PDF kaydedilemedi: {e}")

    def save_backup(self):
        """PDF'nin geçici bir yedeğini kaydeder."""
        try:
            backup_path = "backup_output.pdf"
            self.pdf_document.save(backup_path)
            print("PDF yedeği alındı.")
            return backup_path
        except Exception as e:
            print(f"PDF yedeği alınamadı: {e}")
            return None

    def undo_last_item(self):
        """Son eklenen maddeyi PDF'den kaldırır."""
        if not self.items_added:
            print("Geri alınacak madde yok.")
            return

        # Son eklenen öğeyi al ve listeden çıkar
        last_item = self.items_added.pop()
        page_num, position, item_text = last_item
        page = self.get_page(page_num)

        if page is None:
            print("Geçerli sayfa bulunamadı.")
            return

        # Tüm annot'ları sil
        for annot in annots:
            page.delete_annot(annot)

        # Pozisyonu kontrol ederek anotasyonu kaldır
        found = False
        tolerance = 5  # Yakınlık toleransı
        for annot in page.annots():
            # Pozisyon eşleşmesini kontrol et
            distance = position - annot.rect.tl
            if abs(distance.x) < tolerance and abs(distance.y) < tolerance:
                page.delete_annot(annot)
                found = True
                # PDF'i yeniden kaydet
                self.save_temp_pdf()
                print(f"Madde kaldırıldı: {item_text}")


        if not found:
            print(f"Madde bulunamadı: {item_text} at {position}")

        # undo_last_item içinde:
        for annot in page.annots():
            print(f"Annot pozisyonu: {annot.rect}")
            print(f"Aranan pozisyon: {position}")

        # PDF'yi kaydet
        self.save_temp_pdf()
        print("PDF güncellendi.")

