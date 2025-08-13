class Itemizer:
    def __init__(self):
        self.current_item = 1  # Başlangıç değeri
        self.num_level = 1
        self.letter_level = 'a'
        self.roman_level = 1
        self.levels = ['num', 'letter', 'roman']
        self.current_level_index = 0  # Başlangıç seviyesi 'num'

    def get_next_item(self):
        """Geçerli seviyeye göre bir sonraki madde işaretini döndürür."""
        if self.current_level_index == 0:  # Numara seviyesinde
            item = f"{self.num_level}"
        elif self.current_level_index == 1:  # Harf seviyesinde
            item = f"{self.num_level}.{self.letter_level}"
        else:  # Roman rakamı seviyesinde
            item = f"{self.num_level}.{self.letter_level}.{self.roman_to_string(self.roman_level)}"
        
        # Geçerli seviyeye göre ilerle
        self.increment_current_level()
        
        return item

    def get_current_item(self):
        return self.current_item

    def decrement_current_level(self):
        """Geçerli seviyeyi bir adım geri alır."""
        if self.current_level_index == 0 and self.num_level > 1:
            self.num_level -= 1
        print(f"Madde geri alındı. Mevcut madde: {self.num_level}")

    def reset_items(self):
        """Tüm maddeleme seviyelerini başa döndürür."""
        self.current_item = 1
        self.num_level = 1
        self.letter_level = 'a'
        self.roman_level = 1
        self.current_level_index = 0
        print("Itemizer sıfırlandı, madde '1'den başlayacak.")

    def increase_level(self):
        """Bir alt seviyeye geçiş yapar."""
        if self.current_level_index < 2:
            self.current_level_index += 1
            print(f"Alt seviyeye geçildi: {self.levels[self.current_level_index]}")
            # Alt seviyeye geçildiğinde ilgili katman sayacı sıfırlanır
            if self.current_level_index == 1:  # Harf seviyesi
                self.letter_level = 'a'
            elif self.current_level_index == 2:  # Roman rakamı seviyesi
                self.roman_level = 1

    def decrease_level(self):
        """Bir üst seviyeye geçiş yapar."""
        if self.current_level_index > 0:
            self.current_level_index -= 1
            print(f"Üst seviyeye geçildi: {self.levels[self.current_level_index]}")

    def increment_current_level(self):
        """Geçerli seviyeye göre sayacı ilerletir."""
        if self.current_level_index == 0:  # Numara seviyesinde
            self.num_level += 1
        elif self.current_level_index == 1:  # Harf seviyesinde
            self.letter_level = chr(ord(self.letter_level) + 1)
            if self.letter_level > 'z':  # Z'yi geçerse yeniden 'a'ya döner
                self.letter_level = 'a'
                self.num_level += 1  # Numara seviyesi bir ilerler
        elif self.current_level_index == 2:  # Roman rakamı seviyesinde
            self.roman_level += 1
            if self.roman_level > 5:  # V'yi geçerse yeniden 'i'ye döner
                self.roman_level = 1
                self.letter_level = chr(ord(self.letter_level) + 1)
                if self.letter_level > 'z':  # Z'yi geçerse numara seviyesi ilerler
                    self.letter_level = 'a'
                    self.num_level += 1

    def roman_to_string(self, num):
        """Romen rakamlarını stringe çevirir."""
        romans = {1: 'i', 2: 'ii', 3: 'iii', 4: 'iv', 5: 'v'}
        return romans.get(num, '')
