from __future__ import annotations

from ezergo_overlay.vial.vial_imports import get_keycode, is_keycode_available


def vial_label_for_code(code: int) -> str | None:
    """
    使用 vial-gui 的 Keycode 類獲取鍵碼標籤。
    
    Args:
        code: 整數鍵碼
        
    Returns:
        標籤字符串，如果不可用則返回 None
    """
    if not is_keycode_available():
        return None
    
    Keycode = get_keycode()
    if Keycode is None:
        return None
    
    try:
        # 將整數鍵碼轉換為 QMK ID 字符串
        qmk_id = Keycode.serialize(code)
        if qmk_id is None:
            return None
        
        # 獲取標籤
        label = Keycode.label(qmk_id)
        if label is None or label == qmk_id:
            # 如果標籤不可用或與 QMK ID 相同，返回 None
            return None
        
        return label
    except (AttributeError, Exception):
        return None
