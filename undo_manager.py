class UndoManager:
    def __init__(self, document_manager, pdf_processor, itemizer):
        self.document_manager = document_manager
        self.pdf_processor = pdf_processor
        self.itemizer = itemizer
        self.undo_stack = []
        self.redo_stack = []

    def register_action(self, command):
        self.undo_stack.append(command)
        self.redo_stack.clear()
        print(f"Yeni işlem kaydedildi. Undo yığını: {len(self.undo_stack)}")

    def undo(self):
        if not self.undo_stack:
            print("Geri alınacak işlem yok.")
            return False

        command_to_undo = self.undo_stack.pop()
        self.redo_stack.append(command_to_undo)

        page_num = command_to_undo.get("page_num")
        page = self.document_manager.get_page(page_num)

        if page:
            self.pdf_processor.restore_snapshot(page, command_to_undo)
            if command_to_undo.get("type") == "ADD_ITEM":
                itemizer_state = command_to_undo.get("itemizer_state")
                if itemizer_state: self.itemizer.restore_state(itemizer_state)
            print("İşlem geri alındı.")
            return True
        return False

    def redo(self):
        if not self.redo_stack:
            print("Yeniden yapılacak işlem yok.")
            return False

        command_to_redo = self.redo_stack.pop()

        page_num = command_to_redo.get("page_num")
        page = self.document_manager.get_page(page_num)

        if page:
            # İşlemi PDF üzerinde yeniden uygula
            self.pdf_processor.reapply_action(page, command_to_redo)

            # --- DÜZELTME BURADA ---
            # Itemizer'ı (sayacı) ileri sarmak için doğru fonksiyonu çağırıyoruz.
            if command_to_redo.get("type") == "ADD_ITEM":
                self.itemizer.get_next_item()  # Bu, sayacı bir sonraki adıma geçirir.
            # --- DÜZELTME BİTTİ ---

            self.undo_stack.append(command_to_redo)
            print("İşlem yeniden yapıldı.")
            return True
        return False

    def reset(self):
        self.undo_stack.clear()
        self.redo_stack.clear()
        print("Geri alma ve yineleme geçmişi temizlendi.")