# Bu, PDFProcessor'ün bağımsız çalışıp çalışmadığını kontrol etmek için bir test fonksiyonudur.
from pdf_processor import PDFProcessor

def test_pdf_processor(pdf_path, output_path):
    # PDF dosyasını aç
    pdf_processor = PDFProcessor(pdf_path)

    # İlk sayfayı yükle ve göster
    print("İlk sayfa yükleniyor...")
    page = pdf_processor.get_current_page()
    if page:
        print(f"Sayfa {pdf_processor.current_page + 1} yüklendi.")

    # Sonraki sayfaya geç ve göster
    pdf_processor.next_page()
    page = pdf_processor.get_current_page()
    print(f"Sayfa {pdf_processor.current_page + 1} yüklendi.")

    # Bir önceki sayfaya geri dön ve göster
    pdf_processor.previous_page()
    page = pdf_processor.get_current_page()
    print(f"Sayfa {pdf_processor.current_page + 1} yüklendi.")

    # PDF'yi kaydet
    pdf_processor.save_pdf(output_path)
    print(f"PDF '{output_path}' olarak kaydedildi.")

    # PDF'i kapat
    pdf_processor.close()
    print("PDF kapatıldı.")

# Testi çalıştırmak için aşağıdaki yol ve isimleri kendi dosya sisteminize göre ayarlayın.
pdf_path = "ornek.pdf"  # Test etmek istediğiniz PDF dosyasının yolu
output_path = "duzenlenmis_ornek.pdf"  # Kaydetmek istediğiniz yeni PDF dosyasının yolu
test_pdf_processor(pdf_path, output_path)
