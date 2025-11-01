from enum import Enum, auto
from numbering_strategies import HierarchicalStrategy
# --- Davranış Ayarları ---

class WorkMode(Enum):
    ADD_ITEM = auto()      # Madde ekleme modu
    HIGHLIGHT = auto()     # Metin vurgulama modu

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

DEFAULT_NUMBERING_STRATEGY = HierarchicalStrategy()