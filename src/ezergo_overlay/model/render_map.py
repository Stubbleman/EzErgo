from __future__ import annotations

from dataclasses import dataclass

from ezergo_overlay.vial.vial_imports import get_keycode, is_keycode_available
from ezergo_overlay.vial.vial_keycodes import vial_label_for_code


@dataclass(frozen=True, slots=True)
class KeyRender:
    text: str


def _simplify_label(label: str, prefer_unshifted: bool = False) -> str:
    """
    將 vial-gui 的多行標籤簡化為單行，適合 overlay 顯示。
    
    Args:
        label: 多行標籤（如 "!\n1" 或 "LSft\n(kc)"）
        prefer_unshifted: 如果為 True，對於多行標籤優先取最後一行（未 shift 狀態）
    
    例如：
        "!\n1" -> "1" (prefer_unshifted=True) 或 "!" (prefer_unshifted=False)
        "LSft\n(kc)" -> "LSft"
    """
    if not label:
        return ""
    lines = [ln.strip() for ln in label.split("\n") if ln.strip()]
    if not lines:
        return ""
    # 對於多行標籤，根據 prefer_unshifted 選擇行
    if prefer_unshifted and len(lines) > 1:
        return lines[-1]  # 取最後一行（未 shift 狀態）
    return lines[0]  # 默認取第一行


def render_keycode_minimal(keycode: int) -> KeyRender:
    """
    使用 vial-gui 的 Keycode 類渲染鍵碼標籤。
    優先使用 vial-gui 的標籤，如果不可用則使用 serialize() 作為回退。
    """
    kc = int(keycode)
    
    # 優先使用 Vial 的標籤（完整覆蓋，包括所有複雜鍵碼）
    vial_label = vial_label_for_code(kc)
    if vial_label is not None:
        # 對於基本鍵碼（0x00-0xFF），優先顯示未 shift 狀態
        # 對於其他鍵碼，使用第一行
        is_basic = kc < 0x0100
        simplified = _simplify_label(vial_label, prefer_unshifted=is_basic)
        if simplified:
            return KeyRender(text=simplified)
    
    # 回退：使用 Keycode.serialize() 獲取 QMK ID
    if is_keycode_available():
        Keycode = get_keycode()
        if Keycode is not None:
            try:
                qmk_id = Keycode.serialize(kc)
                if qmk_id and qmk_id != hex(kc):
                    # 如果 serialize 返回有意義的 QMK ID，使用它
                    return KeyRender(text=qmk_id)
            except (AttributeError, Exception):
                pass
    
    # 最終回退：顯示十六進制
    return KeyRender(text=f"0x{kc:04X}")
