from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QKeySequence
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ezergo_overlay.model.settings import OverlaySettings, SettingsManager


class SettingsWindow(QDialog):
    settings_changed = Signal(object)  # 使用 object 類型以支持自定義類型

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("設置")
        self.setModal(True)
        self.setMinimumWidth(400)

        self._settings_manager = SettingsManager()
        self._current_settings = self._settings_manager.get_settings()

        self._setup_ui()
        self._load_current_settings()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        # Always on top
        self._always_on_top_cb = QCheckBox("總是在最上層")
        layout.addWidget(self._always_on_top_cb)

        # Background transparency
        transparency_layout = QHBoxLayout()
        transparency_label = QLabel("背景透明度:")
        transparency_layout.addWidget(transparency_label)
        self._transparency_slider = QSlider(Qt.Horizontal)
        self._transparency_slider.setRange(0, 255)
        self._transparency_slider.setValue(200)
        transparency_layout.addWidget(self._transparency_slider)
        self._transparency_spin = QSpinBox()
        self._transparency_spin.setRange(0, 255)
        self._transparency_spin.setValue(200)
        self._transparency_spin.setSuffix(" / 255")
        transparency_layout.addWidget(self._transparency_spin)
        layout.addLayout(transparency_layout)

        self._transparency_slider.valueChanged.connect(self._transparency_spin.setValue)
        self._transparency_spin.valueChanged.connect(self._transparency_slider.setValue)

        # Background color
        color_layout = QHBoxLayout()
        color_label = QLabel("背景顏色:")
        color_layout.addWidget(color_label)
        self._color_btn = QPushButton()
        self._color_btn.setFixedSize(60, 30)
        self._color_btn.clicked.connect(self._choose_color)
        color_layout.addWidget(self._color_btn)
        color_layout.addStretch()
        layout.addLayout(color_layout)

        # Shortcut key
        shortcut_layout = QHBoxLayout()
        shortcut_label = QLabel("顯示/隱藏快捷鍵:")
        shortcut_layout.addWidget(shortcut_label)
        self._shortcut_btn = QPushButton("F12")
        self._shortcut_btn.setFixedWidth(100)
        self._shortcut_btn.clicked.connect(self._choose_shortcut)
        shortcut_layout.addWidget(self._shortcut_btn)
        shortcut_layout.addStretch()
        layout.addLayout(shortcut_layout)

        # Key background color
        key_bg_layout = QHBoxLayout()
        key_bg_label = QLabel("按鍵背景顏色:")
        key_bg_layout.addWidget(key_bg_label)
        self._key_bg_color_btn = QPushButton()
        self._key_bg_color_btn.setFixedSize(60, 30)
        self._key_bg_color_btn.clicked.connect(self._choose_key_bg_color)
        key_bg_layout.addWidget(self._key_bg_color_btn)
        key_bg_alpha_layout = QHBoxLayout()
        key_bg_alpha_label = QLabel("透明度:")
        key_bg_alpha_layout.addWidget(key_bg_alpha_label)
        self._key_bg_alpha_slider = QSlider(Qt.Horizontal)
        self._key_bg_alpha_slider.setRange(0, 255)
        self._key_bg_alpha_slider.setValue(22)
        key_bg_alpha_layout.addWidget(self._key_bg_alpha_slider)
        self._key_bg_alpha_spin = QSpinBox()
        self._key_bg_alpha_spin.setRange(0, 255)
        self._key_bg_alpha_spin.setValue(22)
        self._key_bg_alpha_spin.setSuffix(" / 255")
        key_bg_alpha_layout.addWidget(self._key_bg_alpha_spin)
        key_bg_layout.addLayout(key_bg_alpha_layout)
        key_bg_layout.addStretch()
        layout.addLayout(key_bg_layout)

        self._key_bg_alpha_slider.valueChanged.connect(self._key_bg_alpha_spin.setValue)
        self._key_bg_alpha_spin.valueChanged.connect(self._key_bg_alpha_slider.setValue)

        # Key font color
        key_font_layout = QHBoxLayout()
        key_font_label = QLabel("按鍵字體顏色:")
        key_font_layout.addWidget(key_font_label)
        self._key_font_color_btn = QPushButton()
        self._key_font_color_btn.setFixedSize(60, 30)
        self._key_font_color_btn.clicked.connect(self._choose_key_font_color)
        key_font_layout.addWidget(self._key_font_color_btn)
        key_font_layout.addStretch()
        layout.addLayout(key_font_layout)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self._cancel_btn = QPushButton("取消")
        self._cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self._cancel_btn)
        self._apply_btn = QPushButton("應用")
        self._apply_btn.clicked.connect(self._apply_settings)
        button_layout.addWidget(self._apply_btn)
        self._ok_btn = QPushButton("確定")
        self._ok_btn.clicked.connect(self._ok_clicked)
        button_layout.addWidget(self._ok_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.setStyleSheet(
            """
            QDialog {
                background-color: #1E1E1E;
                color: #E6E8EB;
            }
            QLabel {
                color: #E6E8EB;
            }
            QCheckBox {
                color: #E6E8EB;
            }
            QPushButton {
                background: rgba(255, 255, 255, 18);
                color: #E6E8EB;
                border: 1px solid rgba(255, 255, 255, 40);
                padding: 6px 16px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 28);
            }
            QSlider::groove:horizontal {
                background: rgba(255, 255, 255, 40);
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #E6E8EB;
                width: 18px;
                height: 18px;
                border-radius: 9px;
                margin: -6px 0;
            }
            QSpinBox {
                background: rgba(255, 255, 255, 18);
                color: #E6E8EB;
                border: 1px solid rgba(255, 255, 255, 40);
                padding: 4px 8px;
                border-radius: 6px;
            }
            """
        )

    def _load_current_settings(self) -> None:
        """加載當前設置到UI"""
        s = self._current_settings
        self._always_on_top_cb.setChecked(s.always_on_top)
        self._transparency_slider.setValue(s.background_transparency)
        self._transparency_spin.setValue(s.background_transparency)
        self._update_color_button(s.background_color_r, s.background_color_g, s.background_color_b)
        self._shortcut_btn.setText(s.shortcut_key)
        # 按鍵顏色
        self._update_key_bg_color_button(s.key_background_r, s.key_background_g, s.key_background_b)
        self._key_bg_alpha_slider.setValue(s.key_background_alpha)
        self._key_bg_alpha_spin.setValue(s.key_background_alpha)
        self._update_key_font_color_button(s.key_font_r, s.key_font_g, s.key_font_b)

    def _update_color_button(self, r: int, g: int, b: int) -> None:
        """更新顏色按鈕的顯示"""
        color = QColor(r, g, b)
        self._color_btn.setStyleSheet(
            f"background-color: {color.name()}; border: 2px solid rgba(255, 255, 255, 60); border-radius: 4px;"
        )

    def _choose_color(self) -> None:
        """選擇背景顏色"""
        s = self._current_settings
        color = QColor(s.background_color_r, s.background_color_g, s.background_color_b)
        color = QColorDialog.getColor(color, self, "選擇背景顏色")
        if color.isValid():
            self._current_settings.background_color_r = color.red()
            self._current_settings.background_color_g = color.green()
            self._current_settings.background_color_b = color.blue()
            self._update_color_button(color.red(), color.green(), color.blue())

    def _choose_shortcut(self) -> None:
        """選擇快捷鍵（簡化版本，暫時只支持F鍵）"""
        # 這裡可以實現更複雜的快捷鍵選擇，暫時簡化為F鍵選擇
        from PySide6.QtWidgets import QInputDialog

        keys = [f"F{i}" for i in range(1, 13)]
        current = self._current_settings.shortcut_key
        try:
            current_idx = keys.index(current)
        except ValueError:
            current_idx = 11  # F12

        key, ok = QInputDialog.getItem(self, "選擇快捷鍵", "選擇顯示/隱藏快捷鍵:", keys, current_idx, False)
        if ok and key:
            self._current_settings.shortcut_key = key
            self._shortcut_btn.setText(key)

    def _update_key_bg_color_button(self, r: int, g: int, b: int) -> None:
        """更新按鍵背景顏色按鈕的顯示"""
        color = QColor(r, g, b)
        self._key_bg_color_btn.setStyleSheet(
            f"background-color: {color.name()}; border: 2px solid rgba(255, 255, 255, 60); border-radius: 4px;"
        )

    def _choose_key_bg_color(self) -> None:
        """選擇按鍵背景顏色"""
        s = self._current_settings
        color = QColor(s.key_background_r, s.key_background_g, s.key_background_b)
        color = QColorDialog.getColor(color, self, "選擇按鍵背景顏色")
        if color.isValid():
            self._current_settings.key_background_r = color.red()
            self._current_settings.key_background_g = color.green()
            self._current_settings.key_background_b = color.blue()
            self._update_key_bg_color_button(color.red(), color.green(), color.blue())

    def _update_key_font_color_button(self, r: int, g: int, b: int) -> None:
        """更新按鍵字體顏色按鈕的顯示"""
        color = QColor(r, g, b)
        self._key_font_color_btn.setStyleSheet(
            f"background-color: {color.name()}; border: 2px solid rgba(255, 255, 255, 60); border-radius: 4px;"
        )

    def _choose_key_font_color(self) -> None:
        """選擇按鍵字體顏色"""
        s = self._current_settings
        color = QColor(s.key_font_r, s.key_font_g, s.key_font_b)
        color = QColorDialog.getColor(color, self, "選擇按鍵字體顏色")
        if color.isValid():
            self._current_settings.key_font_r = color.red()
            self._current_settings.key_font_g = color.green()
            self._current_settings.key_font_b = color.blue()
            self._update_key_font_color_button(color.red(), color.green(), color.blue())

    def _apply_settings(self) -> None:
        """應用設置"""
        # 更新所有設置值到當前設置對象
        self._current_settings.always_on_top = self._always_on_top_cb.isChecked()
        self._current_settings.background_transparency = self._transparency_slider.value()
        self._current_settings.key_background_alpha = self._key_bg_alpha_slider.value()
        # 顏色和快捷鍵已經在 _choose_color、_choose_shortcut、_choose_key_bg_color、_choose_key_font_color 中更新了
        
        # 保存設置
        self._settings_manager.save_settings(self._current_settings)
        
        # 發送信號通知設置已更改
        self.settings_changed.emit(self._current_settings)

    def _ok_clicked(self) -> None:
        """確定按鈕點擊"""
        self._apply_settings()
        self.accept()
