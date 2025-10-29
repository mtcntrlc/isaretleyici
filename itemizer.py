class Itemizer:
    def __init__(self):
        self.num_level = 1
        self.letter_level = 'a'
        self.roman_level = 1
        self.levels = ['num', 'letter', 'roman']
        self.current_level_index = 0

    def get_state(self):
        """Sayacın o anki durumunu bir sözlük olarak döndürür."""
        return {
            'num_level': self.num_level,
            'letter_level': self.letter_level,
            'roman_level': self.roman_level,
            'current_level_index': self.current_level_index,
        }

    def restore_state(self, state):
        """Sayacı, verilen durum sözlüğüne göre ayarlar."""
        self.num_level = state['num_level']
        self.letter_level = state['letter_level']
        self.roman_level = state['roman_level']
        self.current_level_index = state['current_level_index']
        print(f"Sayaç önceki duruma geri yüklendi. Mevcut madde: {self.get_current_item_display()}")

    def get_current_item_display(self):
        """Mevcut sayaca göre görünecek madde metnini oluşturur (sayacı ilerletmez)."""
        if self.current_level_index == 0:
            return f"{self.num_level}"
        elif self.current_level_index == 1:
            return f"{self.num_level}.{self.letter_level}"
        else:
            return f"{self.num_level}.{self.letter_level}.{self.roman_to_string(self.roman_level)}"

    def get_next_item(self):
        """Geçerli madde işaretini döndürür ve sayacı bir sonraki adıma ilerletir."""
        item_text = self.get_current_item_display()
        self.increment_current_level()
        return item_text

    def get_current_item(self):
        """Bu metodun ne amaçla kullanıldığına bağlı olarak yeniden değerlendirilebilir.
           Şimdilik get_current_item_display'i çağırabilir."""
        return self.get_current_item_display()

    def reset_items(self):
        """Tüm maddeleme seviyelerini başa döndürür."""
        self.num_level = 1
        self.letter_level = 'a'
        self.roman_level = 1
        self.current_level_index = 0
        print("Itemizer sıfırlandı, madde '1'den başlayacak.")

    def increase_level(self):
        """Bir alt seviyeye geçiş yapar."""
        if self.current_level_index < 2:
            self.current_level_index += 1
            if self.current_level_index == 1:
                self.letter_level = 'a'
            elif self.current_level_index == 2:
                self.roman_level = 1
            print(f"Alt seviyeye geçildi: {self.levels[self.current_level_index]}")

    def decrease_level(self):
        """Bir üst seviyeye geçiş yapar."""
        if self.current_level_index > 0:
            self.current_level_index -= 1
            print(f"Üst seviyeye geçildi: {self.levels[self.current_level_index]}")

    def increment_current_level(self):
        """Geçerli seviyeye göre sayacı ilerletir."""
        level = self.levels[self.current_level_index]
        if level == 'num':
            self.num_level += 1
        elif level == 'letter':
            if self.letter_level == 'z':
                self.letter_level = 'a'
                # Üst seviyeyi de etkileyebilir, bu mantık projenin ihtiyacına göre ayarlanabilir.
            else:
                self.letter_level = chr(ord(self.letter_level) + 1)
        elif level == 'roman':
            if self.roman_level == 5:
                self.roman_level = 1
            else:
                self.roman_level += 1

    def roman_to_string(self, num):
        """Romen rakamlarını stringe çevirir."""
        romans = {1: 'i', 2: 'ii', 3: 'iii', 4: 'iv', 5: 'v'}
        return romans.get(num, '')