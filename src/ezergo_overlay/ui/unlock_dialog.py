from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPen
from PySide6.QtWidgets import QDialog, QLabel, QProgressBar, QVBoxLayout

if TYPE_CHECKING:
    from ezergo_overlay.vial.vial_client import VialClient
    from ezergo_overlay.ui.keyboard_view import KeyboardView


class UnlockDialog(QDialog):
    """解鎖對話框，顯示解鎖進度條和需要按住的按鍵"""

    def __init__(
        self,
        parent,
        vial_client: VialClient,
        keyboard_view: KeyboardView,
        unlock_keys: list[tuple[int, int]],
    ) -> None:
        super().__init__(parent)
        self._vial_client = vial_client
        self._keyboard_view = keyboard_view
        self._unlock_keys = unlock_keys
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._poll_unlock_status)

        self.setWindowTitle("解鎖鍵盤")
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        self.setMinimumWidth(500)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        info_label1 = QLabel(
            "為了繼續操作，鍵盤必須處於解鎖模式。\n"
            "您應該只在信任的電腦上執行此操作。"
        )
        info_label1.setWordWrap(True)
        info_label1.setStyleSheet("color: #E6E8EB;")
        layout.addWidget(info_label1)

        info_label2 = QLabel(
            "要退出此模式，您需要重新插拔鍵盤\n"
            "或從選單中選擇「安全->鎖定」。"
        )
        info_label2.setWordWrap(True)
        info_label2.setStyleSheet("color: #C9CDD4;")
        layout.addWidget(info_label2)

        info_label3 = QLabel(
            "請按住以下按鍵，直到進度條填滿："
        )
        info_label3.setWordWrap(True)
        info_label3.setStyleSheet("color: #E6E8EB; font-weight: 600;")
        layout.addWidget(info_label3)

        self._keyboard_view.setParent(self)
        self._keyboard_view.setFixedHeight(200)  # 設置固定高度以便在對話框中顯示
        self._highlight_unlock_keys()
        layout.addWidget(self._keyboard_view, 0, Qt.AlignHCenter)

        self._progress = QProgressBar()
        self._progress.setMinimum(0)
        self._progress.setMaximum(1)
        self._progress.setValue(0)
        self._progress.setStyleSheet(
            """
            QProgressBar {
                border: 1px solid rgba(255, 255, 255, 40);
                border-radius: 4px;
                text-align: center;
                color: #E6E8EB;
                background: rgba(255, 255, 255, 10);
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4A9EFF, stop:1 #6BB6FF);
                border-radius: 3px;
            }
            """
        )
        layout.addWidget(self._progress)

        self.setLayout(layout)

        self._bg_color = (20, 22, 26, 240)  # 與主窗口類似的背景顏色
        self._start_unlock()

    def paintEvent(self, event) -> None:
        """繪製對話框背景"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        r, g, b, a = self._bg_color
        painter.setBrush(QBrush(QColor(r, g, b, a)))
        painter.setPen(QPen(Qt.NoPen))
        painter.drawRoundedRect(self.rect(), 10, 10)
        super().paintEvent(event)

    def _highlight_unlock_keys(self) -> None:
        """高亮顯示需要按住的解鎖按鍵"""
        for row, col in self._unlock_keys:
            self._keyboard_view.highlight_key(row, col)

    def _start_unlock(self) -> None:
        """開始解鎖流程"""
        self._progress.setMaximum(1)
        self._progress.setValue(0)
        try:
            self._vial_client.unlock_start()
            self._timer.start(200)
        except Exception as e:
            self._progress.setFormat(f"錯誤: {e}")
            self._timer.stop()

    def _poll_unlock_status(self) -> None:
        """輪詢解鎖狀態並更新進度條"""
        try:
            data = self._vial_client.unlock_poll()
            if len(data) < 3:
                return

            unlocked = int(data[0])
            unlock_counter = int(data[2])

            max_val = max(self._progress.maximum(), unlock_counter)
            self._progress.setMaximum(max_val)
            self._progress.setValue(max_val - unlock_counter)

            if unlocked == 1:
                self._timer.stop()
                self._clear_highlights()
                self.accept()
        except Exception as e:
            self._progress.setFormat(f"錯誤: {e}")

    def _clear_highlights(self) -> None:
        """清除所有高亮"""
        for row, col in self._unlock_keys:
            self._keyboard_view.unhighlight_key(row, col)

    def closeEvent(self, event) -> None:
        """關閉對話框時清除高亮"""
        self._timer.stop()
        self._clear_highlights()
        super().closeEvent(event)
