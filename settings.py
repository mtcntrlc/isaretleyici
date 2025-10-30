from enum import Enum, auto

# --- Davranış Ayarları ---

class NumberingMode(Enum):
    PER_PAGE = auto()
    CONTINUOUS = auto()

DEFAULT_NUMBERING_MODE = NumberingMode.PER_PAGE

# --- Stil ve Font Ayarları ---

FONT_SIZE = 12
FONT_NAME = "times-bold"

# --- Renk ve Opaklık Ayarları ---
# Varsayılan arka plan rengi (Sarı)
DEFAULT_BACKGROUND_COLOR = (209 / 255, 199 / 255, 8 / 255)

# --- YENİ: Opaklık Ayarı ---
# Değer 0.0 (tamamen şeffaf) ile 1.0 (tamamen opak) arasında olmalıdır.
DEFAULT_OPACITY = 0.5