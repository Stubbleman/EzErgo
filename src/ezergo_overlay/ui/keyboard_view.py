from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QFrame, QGraphicsRectItem, QGraphicsScene, QGraphicsSimpleTextItem, QGraphicsView

from ezergo_overlay.model.keymap_model import Keymap, PhysicalKey
from ezergo_overlay.model.render_map import render_keycode_minimal


class KeyboardView(QGraphicsView):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFrameShape(QFrame.NoFrame)
        self.setRenderHint(QPainter.Antialiasing, True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background: transparent;")
        self.setBackgroundBrush(QColor(0, 0, 0, 0))

        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        self._key_rects: list[QGraphicsRectItem] = []
        self._key_texts: list[QGraphicsSimpleTextItem] = []
        self._keymap: Keymap | None = None
        self._physical: list[PhysicalKey] | None = None
        self._layer = 0
        self._max_layers = 1

    def set_keymap(self, keymap: Keymap) -> None:
        self._keymap = keymap
        self._layer = 0
        self._max_layers = max(1, int(keymap.layers))
        self._rebuild_scene()

    def set_layer(self, layer: int) -> None:
        if self._keymap is None:
            return
        layer = max(0, min(int(layer), self._max_layers - 1))
        if layer == self._layer:
            return
        self._layer = layer
        self._update_texts()

    def cycle_layer(self, delta: int) -> int:
        if self._keymap is None:
            return 0
        if self._max_layers <= 0:
            return 0
        nxt = (self._layer + int(delta)) % self._max_layers
        self.set_layer(nxt)
        return self._layer

    @property
    def current_layer(self) -> int:
        return int(self._layer)

    @property
    def max_layers(self) -> int:
        return int(self._max_layers)

    def _rebuild_scene(self) -> None:
        self._scene.clear()
        self._key_rects.clear()
        self._key_texts.clear()
        if self._keymap is None:
            return
        physical = list(self._keymap.physical_keys or [])
        self._physical = physical if physical else None

        key_u = 50
        gap = 8
        step = key_u + gap
        pad = 8
        pen = QPen(QColor(255, 255, 255, 100))
        pen.setWidth(1)
        font = QFont()
        font.setPointSize(9)

        if self._physical:
            for pk in self._physical:
                x = pad + pk.x * step
                y = pad + pk.y * step
                w = pk.w * step - gap
                h = pk.h * step - gap
                rect = QGraphicsRectItem(x, y, w, h)
                rect.setPen(pen)
                rect.setBrush(QColor(255, 255, 255, 22))
                self._scene.addItem(rect)
                self._key_rects.append(rect)

                t = QGraphicsSimpleTextItem("")
                t.setFont(font)
                t.setBrush(QColor("#E6E8EB"))
                self._scene.addItem(t)
                self._key_texts.append(t)
        else:
            rows, cols = self._keymap.matrix.rows, self._keymap.matrix.cols
            key_w, key_h = 56, 56
            for r in range(rows):
                for c in range(cols):
                    x = pad + c * (key_w + gap)
                    y = pad + r * (key_h + gap)
                    rect = QGraphicsRectItem(x, y, key_w, key_h)
                    rect.setPen(pen)
                    rect.setBrush(QColor(255, 255, 255, 22))
                    self._scene.addItem(rect)
                    self._key_rects.append(rect)

                    t = QGraphicsSimpleTextItem("")
                    t.setFont(font)
                    t.setBrush(QColor("#E6E8EB"))
                    self._scene.addItem(t)
                    self._key_texts.append(t)

        self._update_texts()
        self._scene.setSceneRect(self._scene.itemsBoundingRect())
        self.fitInView(self._scene.sceneRect(), Qt.KeepAspectRatio)

    def _update_texts(self) -> None:
        if self._keymap is None:
            return
        key_u = 50
        gap = 8
        step = key_u + gap
        pad = 8

        if self._physical:
            for idx, pk in enumerate(self._physical):
                keycode = self._keymap.keycode_at(self._layer, pk.row, pk.col)
                text = render_keycode_minimal(keycode).text
                item = self._key_texts[idx]
                item.setText(text)

                x = pad + pk.x * step
                y = pad + pk.y * step
                w = pk.w * step - gap
                h = pk.h * step - gap
                br = item.boundingRect()
                item.setPos(x + (w - br.width()) / 2, y + (h - br.height()) / 2)
            return

        cols = self._keymap.matrix.cols
        key_w, key_h = 56, 56

        for r in range(self._keymap.matrix.rows):
            for c in range(cols):
                idx = r * cols + c
                keycode = self._keymap.keycode_at(self._layer, r, c)
                text = render_keycode_minimal(keycode).text
                item = self._key_texts[idx]
                item.setText(text)
                # center text
                br = item.boundingRect()
                x = pad + c * (key_w + gap) + (key_w - br.width()) / 2
                y = pad + r * (key_h + gap) + (key_h - br.height()) / 2
                item.setPos(x, y)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if not self._scene.sceneRect().isNull():
            self.fitInView(self._scene.sceneRect(), Qt.KeepAspectRatio)


