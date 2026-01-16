from __future__ import annotations

from PySide6.QtCore import QPoint, QEvent, Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSizeGrip, QVBoxLayout, QWidget

from ezergo_overlay.ui.keyboard_view import KeyboardView


class OverlayWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("EzErgo Overlay")
        self.setWindowFlags(
            Qt.Window
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
            | Qt.FramelessWindowHint
        )
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

        title_row = QHBoxLayout()
        title_row.addWidget(self._title, 1)
        title_row.addWidget(self._status_label, 0)
        title_row.addWidget(self._btn_prev_layer, 0)
        title_row.addWidget(self._layer_label, 0)
        title_row.addWidget(self._btn_next_layer, 0)
        title_row.addWidget(self._btn_hide, 0)

        self._keyboard = KeyboardView(self)
        # QGraphicsView consumes mouse events; install filters so we can drag the frameless window.
        self._keyboard.installEventFilter(self)
        self._keyboard.viewport().installEventFilter(self)

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

        self.setStyleSheet(
            """
            #overlayRoot {
              background-color: rgba(20, 22, 26, 200);
              border-radius: 10px;
            }
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

        self._title_drag_height_px = 54

    def set_layer(self, layer: int) -> None:
        self._keyboard.set_layer(layer)
        self._sync_layer_label()

    def set_keymap(self, keymap) -> None:
        self._keyboard.set_keymap(keymap)
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


