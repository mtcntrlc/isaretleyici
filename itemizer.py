from numbering_strategies import HierarchicalStrategy

class Itemizer:
    def __init__(self, strategy=None):
        # Eğer bir strateji verilmezse, varsayılan olarak HierarchicalStrategy'yi kullan.
        self.strategy = strategy if strategy is not None else HierarchicalStrategy()
        print(f"Itemizer, '{type(self.strategy).__name__}' stratejisi ile başlatıldı.")

    def set_strategy(self, strategy):
        """Aktif numaralandırma stratejisini değiştirir."""
        self.strategy = strategy
        self.strategy.reset()
        print(f"Itemizer stratejisi '{type(self.strategy).__name__}' olarak değiştirildi.")

    # Tüm çağrıları doğrudan aktif stratejiye yönlendir
    def get_state(self):
        return self.strategy.get_state()

    def restore_state(self, state):
        self.strategy.restore_state(state)
        print(f"Itemizer durumu geri yüklendi. Mevcut madde: {self.get_current_item_display()}")

    def get_current_item_display(self):
        return self.strategy.get_current_item_display()

    def get_next_item(self):
        item_text = self.get_current_item_display()
        self.strategy.increment()
        return item_text

    def increase_level(self):
        self.strategy.increase_level()

    def decrease_level(self):
        self.strategy.decrease_level()

    def reset(self):
        self.strategy.reset()