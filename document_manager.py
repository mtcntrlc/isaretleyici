import fitz


class DocumentManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.pdf_document = fitz.open(file_path)
        self.current_page_index = 0
        self.temp_file_path = "temp_output.pdf"

    def get_document(self):
        return self.pdf_document

    def get_page(self, page_num):
        if 0 <= page_num < self.get_page_count():
            return self.pdf_document[page_num]
        return None

    def get_current_page(self):
        return self.get_page(self.current_page_index)

    def get_page_count(self):
        return len(self.pdf_document)

    def save(self, output_path):
        try:
            self.pdf_document.save(output_path)
            print(f"PDF '{output_path}' olarak kaydedildi.")
            return True
        except Exception as e:
            print(f"PDF kaydedilemedi: {e}")
            return False

    def save_temp(self):
        """Değişiklikleri geçici dosyaya kaydeder."""
        self.save(self.temp_file_path)

    def reset(self):
        self.pdf_document.close()
        self.pdf_document = fitz.open(self.file_path)
        self.current_page_index = 0
        print("Doküman orijinal haline sıfırlandı.")

    def close(self):
        if self.pdf_document:
            self.pdf_document.close()