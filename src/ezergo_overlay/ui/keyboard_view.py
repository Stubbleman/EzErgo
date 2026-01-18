from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QFrame, QGraphicsRectItem, QGraphicsScene, QGraphicsSimpleTextItem, QGraphicsView

from ezergo_overlay.model.keymap_model import Keymap, PhysicalKey
from ezergo_overlay.model.render_map import render_keycode_minimal


class KeyboardView(QGraphicsView):
    layer_changed = Signal(int)

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
        # 按鍵顏色設置
        self._key_bg_color = QColor(255, 255, 255, 22)
        self._key_font_color = QColor("#E6E8EB")
        # 高亮顏色（按下時的顏色）
        self._key_highlight_color = QColor(100, 150, 255, 120)
        # 追蹤被按下的按鍵：{(row, col): True}
        self._pressed_keys: set[tuple[int, int]] = set()

    def set_keymap(self, keymap: Keymap) -> None:
        self._keymap = keymap
        self._layer = 0
        self._max_layers = max(1, int(keymap.layers))
        self._pressed_keys.clear()  # 清除所有高亮狀態
        self._rebuild_scene()

    def set_layer(self, layer: int) -> None:
        if self._keymap is None:
            return
        layer = max(0, min(int(layer), self._max_layers - 1))
        if layer == self._layer:
            return
        self._layer = layer
        self._update_texts()
        self.layer_changed.emit(self._layer)

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
                rect.setBrush(self._key_bg_color)
                self._scene.addItem(rect)
                self._key_rects.append(rect)

                t = QGraphicsSimpleTextItem("")
                t.setFont(font)
                t.setBrush(self._key_font_color)
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
                    rect.setBrush(self._key_bg_color)
                    self._scene.addItem(rect)
                    self._key_rects.append(rect)

                    t = QGraphicsSimpleTextItem("")
                    t.setFont(font)
                    t.setBrush(self._key_font_color)
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

    def set_key_colors(self, bg_r: int, bg_g: int, bg_b: int, bg_alpha: int, font_r: int, font_g: int, font_b: int) -> None:
        """設置按鍵背景顏色和字體顏色"""
        self._key_bg_color = QColor(bg_r, bg_g, bg_b, bg_alpha)
        self._key_font_color = QColor(font_r, font_g, font_b)
        
        # 更新所有現有的按鍵矩形和文字
        # 只更新未按下的按鍵顏色，保留已按下按鍵的高亮
        if self._keymap is not None:
            for idx, rect in enumerate(self._key_rects):
                # 檢查這個按鍵是否被按下
                is_pressed = False
                if self._physical:
                    if idx < len(self._physical):
                        pk = self._physical[idx]
                        is_pressed = (pk.row, pk.col) in self._pressed_keys
                else:
                    cols = self._keymap.matrix.cols
                    row = idx // cols
                    col = idx % cols
                    is_pressed = (row, col) in self._pressed_keys
                
                if not is_pressed:
                    rect.setBrush(self._key_bg_color)
        
        for text in self._key_texts:
            text.setBrush(self._key_font_color)
        
        # 強制重繪
        self._scene.update()

    def _get_key_index_at_pos(self, scene_pos) -> int | None:
        """從場景座標獲取按鍵索引"""
        if self._keymap is None:
            return None
        
        if self._physical:
            key_u = 50
            gap = 8
            step = key_u + gap
            pad = 8
            
            for idx, pk in enumerate(self._physical):
                x = pad + pk.x * step
                y = pad + pk.y * step
                w = pk.w * step - gap
                h = pk.h * step - gap
                
                if x <= scene_pos.x() <= x + w and y <= scene_pos.y() <= y + h:
                    return idx
        else:
            cols = self._keymap.matrix.cols
            key_w, key_h = 56, 56
            gap = 8
            pad = 8
            
            for r in range(self._keymap.matrix.rows):
                for c in range(cols):
                    x = pad + c * (key_w + gap)
                    y = pad + r * (key_h + gap)
                    
                    if x <= scene_pos.x() <= x + key_w and y <= scene_pos.y() <= y + key_h:
                        return r * cols + c
        
        return None

    def _get_key_index_from_matrix(self, row: int, col: int) -> int | None:
        """從矩陣座標 (row, col) 獲取按鍵索引"""
        if self._keymap is None:
            return None
        
        if self._physical:
            # 在 physical_keys 中查找對應的 (row, col)
            for idx, pk in enumerate(self._physical):
                if pk.row == row and pk.col == col:
                    return idx
            return None
        else:
            # 使用矩陣索引計算
            cols = self._keymap.matrix.cols
            if row < 0 or row >= self._keymap.matrix.rows or col < 0 or col >= cols:
                return None
            return row * cols + col

    def highlight_key(self, row: int, col: int) -> None:
        """高亮指定位置的按鍵"""
        idx = self._get_key_index_from_matrix(row, col)
        if idx is None or idx >= len(self._key_rects):
            return
        
        self._pressed_keys.add((row, col))
        rect = self._key_rects[idx]
        rect.setBrush(self._key_highlight_color)
        self._scene.update()

    def unhighlight_key(self, row: int, col: int) -> None:
        """取消高亮指定位置的按鍵"""
        idx = self._get_key_index_from_matrix(row, col)
        if idx is None or idx >= len(self._key_rects):
            return
        
        self._pressed_keys.discard((row, col))
        rect = self._key_rects[idx]
        rect.setBrush(self._key_bg_color)
        self._scene.update()

    def clear_all_highlights(self) -> None:
        """清除所有高亮"""
        for row, col in list(self._pressed_keys):
            self.unhighlight_key(row, col)



