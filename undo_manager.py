class UndoManager:
    def __init__(self, document_manager, pdf_processor, itemizer):
        self.document_manager = document_manager
        self.pdf_processor = pdf_processor
        self.itemizer = itemizer
        self.command_stack = []

    def register_action(self, command):
        """Yapılan bir işlemi ve geri alma bilgilerini kaydeder."""
        self.command_stack.append(command)
        print(f"Yeni işlem kaydedildi. Toplam işlem: {len(self.command_stack)}")

    def undo(self):
        """Son işlemi geri alır."""
        if not self.command_stack:
            print("Geri alınacak işlem yok.")
            return False

        last_command = self.command_stack.pop()

        page_num = last_command.get("page_num")
        page = self.document_manager.get_page(page_num)

        if page:
            self.pdf_processor.restore_snapshot(page, last_command)
            previous_itemizer_state = last_command.get("itemizer_state")
            if previous_itemizer_state:
                self.itemizer.restore_state(previous_itemizer_state)

            print("İşlem başarıyla geri alındı.")
            return True
        return False