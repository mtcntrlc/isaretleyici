from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QCheckBox, QDoubleSpinBox,
    QPushButton, QDialogButtonBox, QColorDialog
)
from PySide6.QtGui import QColor
import settings


class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.setMinimumWidth(350)

        # Ana layout'lar
        self.main_layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()

        # Ayarlar için Widget'lar
        self.reset_on_page_turn_checkbox = QCheckBox("Reset numbering on each page turn")

        self.opacity_spinbox = QDoubleSpinBox()
        self.opacity_spinbox.setRange(0.1, 1.0)
        self.opacity_spinbox.setSingleStep(0.1)

        self.color_button = QPushButton()
        self.color_button.setToolTip("Click to select the annotation color")

        # Widget'ları form layout'una ekle
        self.form_layout.addRow("Numbering:", self.reset_on_page_turn_checkbox)
        self.form_layout.addRow("Annotation Opacity:", self.opacity_spinbox)
        self.form_layout.addRow("Annotation Color:", self.color_button)

        # OK ve Cancel butonları
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        # Layout'ları ana pencereye ekle
        self.main_layout.addLayout(self.form_layout)
        self.main_layout.addWidget(self.button_box)

        # Sinyalleri bağla
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.color_button.clicked.connect(self.select_color)

        # Değişiklikleri geçici olarak saklamak için
        self.temp_color = settings.DEFAULT_BACKGROUND_COLOR

        # Mevcut ayarları pencereye yükle
        self.load_settings()

    def load_settings(self):
        """Mevcut ayarları settings modülünden okuyup widget'lara yükler."""
        is_per_page = (settings.DEFAULT_NUMBERING_MODE == settings.NumberingMode.PER_PAGE)
        self.reset_on_page_turn_checkbox.setChecked(is_per_page)
        self.opacity_spinbox.setValue(settings.DEFAULT_OPACITY)
        self.update_color_button_style()

    def select_color(self):
        """Renk seçme diyaloğunu açar ve rengi geçici olarak saklar."""
        r, g, b = [int(c * 255) for c in self.temp_color]
        initial_color = QColor(r, g, b)
        color = QColorDialog.getColor(initial_color, self, "Select Annotation Color")
        if color.isValid():
            self.temp_color = (color.redF(), color.greenF(), color.blueF())
            self.update_color_button_style()

    def update_color_button_style(self):
        """Renk butonunun arkaplanını seçilen rengi gösterecek şekilde günceller."""
        r, g, b = [int(c * 255) for c in self.temp_color]
        self.color_button.setStyleSheet(f"background-color: rgb({r}, {g}, {b});")
        self.color_button.setText(f"RGB({r}, {g}, {b})")

    def accept(self):
        """OK'a basıldığında, penceredeki ayarları `settings` modülüne kaydeder."""
        if self.reset_on_page_turn_checkbox.isChecked():
            settings.DEFAULT_NUMBERING_MODE = settings.NumberingMode.PER_PAGE
        else:
            settings.DEFAULT_NUMBERING_MODE = settings.NumberingMode.CONTINUOUS

        settings.DEFAULT_OPACITY = self.opacity_spinbox.value()
        settings.DEFAULT_BACKGROUND_COLOR = self.temp_color

        print("Ayarlar kaydedildi.")
        super().accept()