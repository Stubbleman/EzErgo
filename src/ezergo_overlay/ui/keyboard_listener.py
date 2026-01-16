from __future__ import annotations

import math
import threading
import time
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, Signal

from ezergo_overlay.model.keymap_model import Keymap
from ezergo_overlay.vial.errors import VialProtocolError

if TYPE_CHECKING:
    from ezergo_overlay.vial.vial_client import VialClient


class KeyboardListener(QObject):
    """
    使用 Vial matrix tester 監聽鍵盤按鍵，檢測 MO(X) 鍵並觸發層切換。
    """

    mo_key_pressed = Signal(int)  # 發出層號

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._keymap: Keymap | None = None
        self._current_layer = 0
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._vial_client: VialClient | None = None
        self._unlocked = False
        self._last_matrix_state: dict[tuple[int, int], bool] = {}
        # 追蹤激活的 MO 鍵：{(row, col): (layer, mo_layer)}
        # layer 是 MO 鍵被定義的層，mo_layer 是 MO 鍵要切換到的層
        self._active_mo_keys: dict[tuple[int, int], tuple[int, int]] = {}

    def set_vial_client(self, client: VialClient | None) -> None:
        """設置 Vial 客戶端"""
        self._vial_client = client
        self._unlocked = False

    def set_keymap(self, keymap: Keymap) -> None:
        """設置 keymap 以便查找按鍵"""
        self._keymap = keymap
        self._last_matrix_state.clear()

    def set_current_layer(self, layer: int) -> None:
        """更新當前層"""
        self._current_layer = layer

    def start(self) -> bool:
        """啟動鍵盤監聽"""
        if self._thread is not None and self._thread.is_alive():
            return False

        if self._vial_client is None:
            print("錯誤: 未設置 Vial 客戶端")
            return False

        if self._keymap is None:
            print("錯誤: 未設置 keymap")
            return False

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()
        return True

    def stop(self) -> None:
        """停止鍵盤監聽"""
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=1.0)

    def _ensure_unlocked(self) -> bool:
        """確保鍵盤已解鎖，如果未解鎖則嘗試解鎖"""
        if self._vial_client is None:
            return False

        try:
            # 檢查是否已解鎖
            unlocked = self._vial_client.get_unlock_status()
            if unlocked == 1:
                self._unlocked = True
                return True

            # 如果未解鎖，嘗試解鎖
            if not self._unlocked:
                print("正在解鎖鍵盤...")
                self._vial_client.unlock_start()

                # 輪詢解鎖狀態（最多等待 10 秒）
                deadline = time.monotonic() + 10.0
                while time.monotonic() < deadline:
                    if self._stop_event.is_set():
                        return False

                    try:
                        data = self._vial_client.unlock_poll()
                        if len(data) >= 1:
                            unlocked = data[0]
                            if unlocked == 1:
                                self._unlocked = True
                                print("鍵盤已解鎖")
                                return True
                    except Exception as e:
                        print(f"解鎖輪詢錯誤: {e}")
                        time.sleep(0.2)
                        continue

                    time.sleep(0.2)

                print("警告: 解鎖超時，請手動按住解鎖鍵")
                return False

            return True
        except Exception as e:
            print(f"解鎖檢查錯誤: {type(e).__name__}: {e}")
            return False

    def _parse_matrix_data(self, data: bytes, rows: int, cols: int) -> dict[tuple[int, int], bool]:
        """
        解析 matrix_poll 返回的數據。
        返回: {(row, col): pressed} 的字典
        """
        matrix_state: dict[tuple[int, int], bool] = {}

        # 計算每行需要的字節數（每 8 個按鍵需要 1 個字節）
        row_size = math.ceil(cols / 8)

        # 跳過前 2 個字節（VIAL 標識）
        for row in range(rows):
            row_data_start = 2 + (row * row_size)
            row_data_end = row_data_start + row_size

            if row_data_end > len(data):
                break

            row_data = data[row_data_start:row_data_end]

            # 解析每個列的狀態
            for col in range(cols):
                # 計算該列在哪個字節中
                col_byte = len(row_data) - 1 - math.floor(col / 8)
                if col_byte < 0 or col_byte >= len(row_data):
                    continue

                # 計算該列在字節中的位置
                col_mod = col % 8
                # 讀取該 bit 的狀態
                pressed = (row_data[col_byte] >> col_mod) & 1
                matrix_state[(row, col)] = bool(pressed)

        return matrix_state

    def _listen_loop(self) -> None:
        """鍵盤監聽循環，使用 Vial matrix_poll"""
        if self._vial_client is None or self._keymap is None:
            return

        QK_MOMENTARY = 0x5220
        rows = self._keymap.matrix.rows
        cols = self._keymap.matrix.cols

        print("鍵盤監聽器已啟動（使用 Vial matrix tester）")

        while not self._stop_event.is_set():
            try:
                # 確保鍵盤已解鎖
                if not self._ensure_unlocked():
                    time.sleep(0.5)
                    continue

                # 獲取矩陣狀態
                try:
                    data = self._vial_client.matrix_poll()
                except VialProtocolError as e:
                    print(f"matrix_poll 錯誤: {e}")
                    time.sleep(0.1)
                    continue
                except Exception as e:
                    print(f"matrix_poll 意外錯誤: {type(e).__name__}: {e}")
                    time.sleep(0.1)
                    continue

                # 解析矩陣數據
                current_state = self._parse_matrix_data(data, rows, cols)

                # 檢測按鍵按下和釋放事件
                current_layer = self._current_layer
                
                # 檢查當前激活的 MO 鍵是否仍然被按下
                # 注意：我們需要在 MO 鍵被定義的原始層中檢查，而不是當前激活的層
                released_mo_keys = []
                for (row, col), (original_layer, _) in list(self._active_mo_keys.items()):
                    is_still_pressed = current_state.get((row, col), False)
                    
                    if not is_still_pressed:
                        # MO 鍵被釋放
                        released_mo_keys.append((row, col))
                        del self._active_mo_keys[(row, col)]
                
                # 如果有 MO 鍵被釋放，檢查是否還有其他 MO 鍵被按下
                if released_mo_keys:
                    if len(self._active_mo_keys) == 0:
                        # 所有 MO 鍵都被釋放，切換回層 0
                        print(f"所有 MO 鍵被釋放，切換回層 0")
                        self.mo_key_pressed.emit(0)
                    # 如果還有其他 MO 鍵被按下，保持當前層（由最後按下的 MO 鍵決定）
                
                # 檢測新按下的 MO 鍵
                # 我們需要在所有層中檢查，因為 MO 鍵可能在任何層中被定義
                for (row, col), pressed in current_state.items():
                    was_pressed = self._last_matrix_state.get((row, col), False)

                    if pressed and not was_pressed:
                        # 按鍵剛被按下，檢查在當前層中是否為 MO 鍵
                        # 注意：如果當前層已經被 MO 鍵切換，我們應該在原始層（通常是層 0）中檢查
                        # 但為了簡化，我們先檢查當前層，如果當前層沒有 MO 鍵，再檢查層 0
                        check_layers = [current_layer]
                        if current_layer != 0:
                            check_layers.append(0)
                        
                        for layer_to_check in check_layers:
                            keycode = self._keymap.keycode_at(layer_to_check, row, col)

                            # 檢查是否為 MO(X) 鍵
                            if QK_MOMENTARY <= keycode < QK_MOMENTARY + 32:
                                mo_layer = keycode - QK_MOMENTARY
                                if mo_layer < self._keymap.layers:
                                    print(f"檢測到 MO({mo_layer}) 鍵在位置 ({row}, {col})（層 {layer_to_check}），切換到層 {mo_layer}")
                                    self._active_mo_keys[(row, col)] = (layer_to_check, mo_layer)
                                    self.mo_key_pressed.emit(mo_layer)
                                break  # 找到 MO 鍵後停止檢查其他層

                # 更新狀態
                self._last_matrix_state = current_state

                # 輪詢間隔（約 20ms，與 Vial GUI 一致）
                time.sleep(0.02)

            except Exception as e:
                print(f"鍵盤監聽器錯誤: {type(e).__name__}: {e}")
                time.sleep(0.1)
