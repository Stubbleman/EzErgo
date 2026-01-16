from __future__ import annotations

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QMenu, QStyle, QSystemTrayIcon


class TrayController:
    def __init__(self, window, on_reconnect) -> None:
        self._window = window
        self._on_reconnect = on_reconnect

        self._tray = QSystemTrayIcon()
        self._status_text = "啟動中"
        self._tray.setToolTip(f"EzErgo Overlay - {self._status_text}")
        self._tray.setIcon(QApplication.style().standardIcon(QStyle.SP_ComputerIcon))

        menu = QMenu()
        self._act_status = QAction(f"狀態：{self._status_text}", menu)
        self._act_status.setEnabled(False)
        menu.addAction(self._act_status)
        menu.addSeparator()

        self._act_toggle = QAction("顯示/隱藏", menu)
        self._act_toggle.triggered.connect(self._toggle)
        menu.addAction(self._act_toggle)

        self._act_reconnect = QAction("重新連線", menu)
        self._act_reconnect.triggered.connect(self._on_reconnect)
        menu.addAction(self._act_reconnect)

        menu.addSeparator()

        self._act_quit = QAction("退出", menu)
        self._act_quit.triggered.connect(self._quit)
        menu.addAction(self._act_quit)

        self._tray.setContextMenu(menu)
        self._tray.activated.connect(self._on_activated)

    def show(self) -> None:
        self._tray.show()

    def set_status(self, text: str) -> None:
        self._status_text = text
        self._tray.setToolTip(f"EzErgo Overlay - {text}")
        self._act_status.setText(f"狀態：{text}")

    def _toggle(self) -> None:
        if self._window.isVisible():
            self._window.hide()
        else:
            self._window.show()
            self._window.raise_()
            self._window.activateWindow()

    def _quit(self) -> None:
        self._tray.hide()
        QApplication.quit()

    def _on_activated(self, reason) -> None:
        if reason == QSystemTrayIcon.Trigger:
            self._toggle()


