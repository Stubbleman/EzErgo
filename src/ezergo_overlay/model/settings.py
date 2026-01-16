from __future__ import annotations

from dataclasses import dataclass
from PySide6.QtCore import QSettings


@dataclass
class OverlaySettings:
    always_on_top: bool = True
    background_transparency: int = 200  # 0-255
    background_color_r: int = 20
    background_color_g: int = 22
    background_color_b: int = 26
    shortcut_key: str = "F12"  # 顯示/隱藏快捷鍵
    # 按鍵顏色設置
    key_background_r: int = 255
    key_background_g: int = 255
    key_background_b: int = 255
    key_background_alpha: int = 22  # 0-255
    key_font_r: int = 230
    key_font_g: int = 232
    key_font_b: int = 235

    def to_rgba_string(self) -> str:
        """轉換為 CSS rgba 字符串"""
        return f"rgba({self.background_color_r}, {self.background_color_g}, {self.background_color_b}, {self.background_transparency})"

    def to_rgba_tuple(self) -> tuple[int, int, int, int]:
        """轉換為 RGBA 元組"""
        return (
            self.background_color_r,
            self.background_color_g,
            self.background_color_b,
            self.background_transparency,
        )


class SettingsManager:
    _instance: SettingsManager | None = None

    def __new__(cls) -> SettingsManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, "_initialized"):
            return
        self._initialized = True
        self._qsettings = QSettings("EzErgo", "Overlay")
        self._settings = self._load_settings()

    def _load_settings(self) -> OverlaySettings:
        """從 QSettings 加載設置"""
        return OverlaySettings(
            always_on_top=self._qsettings.value("always_on_top", True, bool),
            background_transparency=self._qsettings.value("background_transparency", 200, int),
            background_color_r=self._qsettings.value("background_color_r", 20, int),
            background_color_g=self._qsettings.value("background_color_g", 22, int),
            background_color_b=self._qsettings.value("background_color_b", 26, int),
            shortcut_key=self._qsettings.value("shortcut_key", "F12", str),
            key_background_r=self._qsettings.value("key_background_r", 255, int),
            key_background_g=self._qsettings.value("key_background_g", 255, int),
            key_background_b=self._qsettings.value("key_background_b", 255, int),
            key_background_alpha=self._qsettings.value("key_background_alpha", 22, int),
            key_font_r=self._qsettings.value("key_font_r", 230, int),
            key_font_g=self._qsettings.value("key_font_g", 232, int),
            key_font_b=self._qsettings.value("key_font_b", 235, int),
        )

    def save_settings(self, settings: OverlaySettings) -> None:
        """保存設置到 QSettings"""
        self._settings = settings
        self._qsettings.setValue("always_on_top", settings.always_on_top)
        self._qsettings.setValue("background_transparency", settings.background_transparency)
        self._qsettings.setValue("background_color_r", settings.background_color_r)
        self._qsettings.setValue("background_color_g", settings.background_color_g)
        self._qsettings.setValue("background_color_b", settings.background_color_b)
        self._qsettings.setValue("shortcut_key", settings.shortcut_key)
        self._qsettings.setValue("key_background_r", settings.key_background_r)
        self._qsettings.setValue("key_background_g", settings.key_background_g)
        self._qsettings.setValue("key_background_b", settings.key_background_b)
        self._qsettings.setValue("key_background_alpha", settings.key_background_alpha)
        self._qsettings.setValue("key_font_r", settings.key_font_r)
        self._qsettings.setValue("key_font_g", settings.key_font_g)
        self._qsettings.setValue("key_font_b", settings.key_font_b)
        self._qsettings.sync()

    def get_settings(self) -> OverlaySettings:
        """獲取當前設置"""
        return self._settings
