from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QPoint, QEvent, Qt
from PySide6.QtGui import QBrush, QColor, QKeySequence, QPainter, QPen, QShortcut
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSizeGrip, QVBoxLayout, QWidget

from ezergo_overlay.model.settings import OverlaySettings, SettingsManager
from ezergo_overlay.ui.keyboard_listener import KeyboardListener
from ezergo_overlay.ui.keyboard_view import KeyboardView
from ezergo_overlay.ui.settings_window import SettingsWindow

if TYPE_CHECKING:
    from ezergo_overlay.vial.vial_client import VialClient


class OverlayWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("EzErgo Overlay")
        # 先讀取設置，然後根據設置設置窗口標誌
        self._settings_manager = SettingsManager()
        settings = self._settings_manager.get_settings()
        
        base_flags = Qt.Window | Qt.Tool | Qt.FramelessWindowHint
        if settings.always_on_top:
            flags = base_flags | Qt.WindowStaysOnTopHint
        else:
            flags = base_flags
        self.setWindowFlags(flags)
        
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setObjectName("overlayRoot")

        self._drag_pos: QPoint | None = None

        self._title = QLabel("EzErgo Overlay")
        self._title.setStyleSheet("color: #E6E8EB; font-weight: 600;")

        self._layer_label = QLabel("L0")
        self._layer_label.setStyleSheet("color: #C9CDD4;")

        self._status_label = QLabel("啟動中")
        self._status_label.setStyleSheet("color: rgba(201, 205, 212, 180);")

        self._btn_prev_layer = QPushButton("◀")
        self._btn_prev_layer.setFixedWidth(34)
        self._btn_prev_layer.clicked.connect(lambda: self._cycle_layer(-1))

        self._btn_next_layer = QPushButton("▶")
        self._btn_next_layer.setFixedWidth(34)
        self._btn_next_layer.clicked.connect(lambda: self._cycle_layer(+1))

        self._btn_hide = QPushButton("隱藏")
        self._btn_hide.setFixedWidth(64)
        self._btn_hide.clicked.connect(self.hide)

        self._btn_settings = QPushButton("⚙")
        self._btn_settings.setFixedWidth(34)
        self._btn_settings.setToolTip("設置")
        self._btn_settings.clicked.connect(self._show_settings)

        title_row = QHBoxLayout()
        title_row.addWidget(self._title, 1)
        title_row.addWidget(self._status_label, 0)
        title_row.addWidget(self._btn_prev_layer, 0)
        title_row.addWidget(self._layer_label, 0)
        title_row.addWidget(self._btn_next_layer, 0)
        title_row.addWidget(self._btn_hide, 0)
        title_row.addWidget(self._btn_settings, 0)

        self._keyboard = KeyboardView(self)
        # QGraphicsView consumes mouse events; install filters so we can drag the frameless window.
        self._keyboard.installEventFilter(self)
        self._keyboard.viewport().installEventFilter(self)
        # 連接層切換信號以同步層標籤
        self._keyboard.layer_changed.connect(self._sync_layer_label)
        
        # 創建鍵盤監聽器
        self._keyboard_listener = KeyboardListener(self)
        self._keyboard_listener.mo_key_pressed.connect(self._on_mo_key_pressed)
        # 連接按鍵按下/釋放信號以實現高亮
        self._keyboard_listener.key_pressed.connect(self._keyboard.highlight_key)
        self._keyboard_listener.key_released.connect(self._keyboard.unhighlight_key)
        self._vial_client = None

        self._grip = QSizeGrip(self)

        root = QVBoxLayout()
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)
        root.addLayout(title_row)
        root.addWidget(self._keyboard, 1)

        bottom = QHBoxLayout()
        bottom.addStretch(1)
        bottom.addWidget(self._grip, 0, Qt.AlignRight | Qt.AlignBottom)
        root.addLayout(bottom)

        self.setLayout(root)
        self.setMinimumSize(520, 260)

        self._shortcut: QShortcut | None = None
        self._bg_color = (20, 22, 26, 200)  # 默認背景顏色和透明度
        self._apply_settings(settings)  # 應用所有設置（包括背景顏色等）

        self._title_drag_height_px = 54

    def _show_settings(self) -> None:
        """顯示設置窗口"""
        settings_window = SettingsWindow(self)
        settings_window.settings_changed.connect(self._apply_settings)
        settings_window.exec()

    def _apply_settings(self, settings: OverlaySettings) -> None:
        """應用設置到窗口"""
        if not isinstance(settings, OverlaySettings):
            return  # 如果設置對象類型不正確，直接返回
        
        # 應用 always-on-top
        # 需要保留所有原有的標誌
        base_flags = Qt.Window | Qt.Tool | Qt.FramelessWindowHint
        if settings.always_on_top:
            flags = base_flags | Qt.WindowStaysOnTopHint
        else:
            flags = base_flags
        
        # 檢查標誌是否真的改變了
        current_flags = self.windowFlags()
        was_visible = self.isVisible()
        if current_flags != flags:
            self.setWindowFlags(flags)
            # 需要重新顯示才能應用窗口標誌
            # 保存窗口位置和大小
            geometry = self.geometry()
            if was_visible:
                self.hide()
            self.show()
            # 恢復窗口位置和大小
            self.setGeometry(geometry)

        # 保存背景顏色和透明度
        self._bg_color = settings.to_rgba_tuple()
        
        # 應用樣式表（按鈕樣式）
        self.setStyleSheet(
            """
            QPushButton {
              background: rgba(255, 255, 255, 18);
              color: #E6E8EB;
              border: 1px solid rgba(255, 255, 255, 40);
              padding: 6px 10px;
              border-radius: 8px;
            }
            QPushButton:hover { background: rgba(255, 255, 255, 28); }
            """
        )
        
        # 強制重繪以應用背景顏色
        self.update()

        # 應用快捷鍵
        self._setup_shortcut(settings.shortcut_key)

        # 應用按鍵顏色
        self._keyboard.set_key_colors(
            settings.key_background_r,
            settings.key_background_g,
            settings.key_background_b,
            settings.key_background_alpha,
            settings.key_font_r,
            settings.key_font_g,
            settings.key_font_b,
        )

    def _setup_shortcut(self, key: str) -> None:
        """設置顯示/隱藏快捷鍵"""
        if self._shortcut is not None:
            self._shortcut.deleteLater()
            self._shortcut = None

        try:
            key_sequence = QKeySequence(key)
            if not key_sequence.isEmpty():
                self._shortcut = QShortcut(key_sequence, self)
                self._shortcut.activated.connect(self._toggle_visibility)
        except Exception:
            # 如果快捷鍵設置失敗，忽略錯誤
            pass

    def _toggle_visibility(self) -> None:
        """切換窗口顯示/隱藏"""
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()
            self.activateWindow()

    def set_layer(self, layer: int) -> None:
        self._keyboard.set_layer(layer)
        self._keyboard_listener.set_current_layer(layer)
        self._sync_layer_label()
        
    def _on_mo_key_pressed(self, layer: int) -> None:
        """當檢測到 MO(X) 鍵按下時切換層"""
        self.set_layer(layer)

    def set_vial_client(self, client) -> None:
        """設置 Vial 客戶端給鍵盤監聽器"""
        self._vial_client = client
        self._keyboard_listener.set_vial_client(client)
        # 如果 keymap 已經設置，嘗試啟動監聽器
        # 嘗試啟動監聽器（如果 keymap 未設置，start 會返回 False）
        if not self._keyboard_listener.start():
            # 如果啟動失敗，可能是 keymap 還未設置，稍後會在 set_keymap 中重試
            pass
        else:
            self.set_status("已連線")

    def set_keymap(self, keymap) -> None:
        self._keyboard.set_keymap(keymap)
        self._keyboard_listener.set_keymap(keymap)
        # 如果 Vial 客戶端已經設置，嘗試啟動鍵盤監聽器
        if self._vial_client is not None:
            if not self._keyboard_listener.start():
                self.set_status("鍵盤監聽未啟動")
            else:
                self.set_status("已連線")
        else:
            self.set_status("等待鍵盤連接...")
        self._sync_layer_label()

    def set_status(self, text: str) -> None:
        self._status_label.setText(text)

    def _cycle_layer(self, delta: int) -> None:
        self._keyboard.cycle_layer(delta)
        self._sync_layer_label()

    def _sync_layer_label(self) -> None:
        self._layer_label.setText(f"L{self._keyboard.current_layer}")

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            # Allow dragging almost anywhere (Wayland friendly), except interactive controls.
            child = self.childAt(event.position().toPoint())
            if isinstance(child, (QPushButton, QSizeGrip)):
                super().mousePressEvent(event)
                return
            if self._start_system_move():
                event.accept()
                return
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._drag_pos is not None and (event.buttons() & Qt.LeftButton):
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self._drag_pos = None
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def eventFilter(self, watched, event) -> bool:
        t = event.type()
        if t == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
            # Don't start dragging when clicking interactive controls.
            child = self.childAt(self.mapFromGlobal(event.globalPosition().toPoint()))
            if isinstance(child, (QPushButton, QSizeGrip)):
                return False
            if self._start_system_move():
                return True
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            return True
        if t == QEvent.MouseMove and self._drag_pos is not None and (event.buttons() & Qt.LeftButton):
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            return True
        if t == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
            self._drag_pos = None
            return True
        return super().eventFilter(watched, event)

    def paintEvent(self, event) -> None:
        """繪製窗口背景"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        r, g, b, a = self._bg_color
        painter.setBrush(QBrush(QColor(r, g, b, a)))
        painter.setPen(QPen(Qt.NoPen))
        painter.drawRoundedRect(self.rect(), 10, 10)
        super().paintEvent(event)

    def _start_system_move(self) -> bool:
        """
        On Wayland, programmatic QWidget.move() is often ignored for top-level windows.
        Use compositor-assisted system move when available.
        """
        wh = self.windowHandle()
        if wh is None:
            return False
        try:
            return bool(wh.startSystemMove())
        except Exception:
            return False
    
    def closeEvent(self, event) -> None:
        """窗口關閉時停止鍵盤監聽器"""
        self._keyboard_listener.stop()
        super().closeEvent(event)


