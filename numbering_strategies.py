class BaseStrategy:
    """Tüm numaralandırma stratejileri için bir şablon görevi görür."""
    def get_state(self):
        raise NotImplementedError
    def restore_state(self, state):
        raise NotImplementedError
    def get_current_item_display(self):
        raise NotImplementedError
    def increment(self):
        raise NotImplementedError
    def increase_level(self):
        raise NotImplementedError
    def decrease_level(self):
        raise NotImplementedError
    def reset(self):
        raise NotImplementedError

class HierarchicalStrategy(BaseStrategy):
    """'1, a, i' formatında hiyerarşik numaralandırma stratejisi."""
    def __init__(self):
        self.reset()

    def get_state(self):
        return {
            'num': self.num_level, 'letter': self.letter_level,
            'roman': self.roman_level, 'index': self.current_level_index
        }

    def restore_state(self, state):
        if state:
            self.num_level = state['num']
            self.letter_level = state['letter']
            self.roman_level = state['roman']
            self.current_level_index = state['index']

    def get_current_item_display(self):
        if self.current_level_index == 0: return f"{self.num_level}"
        elif self.current_level_index == 1: return f"{self.num_level}.{self.letter_level}"
        else: return f"{self.num_level}.{self.letter_level}.{self._roman_to_string(self.roman_level)}"

    def increment(self):
        if self.current_level_index == 0: self.num_level += 1
        elif self.current_level_index == 1: self.letter_level = chr(ord(self.letter_level) + 1)
        elif self.current_level_index == 2:
            if self.roman_level >= 20: self.roman_level = 1
            else: self.roman_level += 1

    def increase_level(self):
        if self.current_level_index < 2:
            self.current_level_index += 1
            if self.current_level_index == 1: self.letter_level = 'a'
            elif self.current_level_index == 2: self.roman_level = 1

    def decrease_level(self):
        if self.current_level_index > 0:
            self.current_level_index -= 1

    def reset(self):
        self.num_level = 1
        self.letter_level = 'a'
        self.roman_level = 1
        self.current_level_index = 0

    def _roman_to_string(self, num):
        if not 1 <= num <= 20: return str(num)
        val = [10, 9, 5, 4, 1]; syb = ["x", "ix", "v", "iv", "i"]
        roman_num = ""; i = 0
        while num > 0:
            for _ in range(num // val[i]): roman_num += syb[i]; num -= val[i]
            i += 1
        return roman_num