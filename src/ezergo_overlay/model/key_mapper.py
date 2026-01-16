from __future__ import annotations

"""
將系統按鍵名稱映射到 QMK keycode (HID usage code)。

注意：此模組已廢棄，不再使用。
現在使用 Vial matrix tester 方法直接從鍵盤固件獲取矩陣狀態，
不再需要將按鍵名稱轉換為 QMK keycode。
"""

# 按鍵名稱到 QMK keycode 的映射 (HID usage codes)
# 參考: https://www.usb.org/sites/default/files/documents/hut1_12v2.pdf
KEY_NAME_TO_QMK: dict[str, int] = {
    # 字母
    "a": 0x04,
    "b": 0x05,
    "c": 0x06,
    "d": 0x07,
    "e": 0x08,
    "f": 0x09,
    "g": 0x0A,
    "h": 0x0B,
    "i": 0x0C,
    "j": 0x0D,
    "k": 0x0E,
    "l": 0x0F,
    "m": 0x10,
    "n": 0x11,
    "o": 0x12,
    "p": 0x13,
    "q": 0x14,
    "r": 0x15,
    "s": 0x16,
    "t": 0x17,
    "u": 0x18,
    "v": 0x19,
    "w": 0x1A,
    "x": 0x1B,
    "y": 0x1C,
    "z": 0x1D,
    # 數字行
    "1": 0x1E,
    "2": 0x1F,
    "3": 0x20,
    "4": 0x21,
    "5": 0x22,
    "6": 0x23,
    "7": 0x24,
    "8": 0x25,
    "9": 0x26,
    "0": 0x27,
    # 功能鍵
    "enter": 0x28,
    "esc": 0x29,
    "backspace": 0x2A,
    "tab": 0x2B,
    "space": 0x2C,
    "minus": 0x2D,
    "equal": 0x2E,
    "left bracket": 0x2F,
    "right bracket": 0x30,
    "backslash": 0x31,
    "semicolon": 0x33,
    "apostrophe": 0x34,
    "grave": 0x35,
    "comma": 0x36,
    "period": 0x37,
    "slash": 0x38,
    "caps lock": 0x39,
    # F 鍵
    "f1": 0x3A,
    "f2": 0x3B,
    "f3": 0x3C,
    "f4": 0x3D,
    "f5": 0x3E,
    "f6": 0x3F,
    "f7": 0x40,
    "f8": 0x41,
    "f9": 0x42,
    "f10": 0x43,
    "f11": 0x44,
    "f12": 0x45,
    # 其他
    "print screen": 0x46,
    "scroll lock": 0x47,
    "pause": 0x48,
    "insert": 0x49,
    "home": 0x4A,
    "page up": 0x4B,
    "delete": 0x4C,
    "end": 0x4D,
    "page down": 0x4E,
    "right": 0x4F,
    "left": 0x50,
    "down": 0x51,
    "up": 0x52,
    "num lock": 0x53,
    # 修飾鍵
    "left ctrl": 0xE0,
    "left shift": 0xE1,
    "left alt": 0xE2,
    "left windows": 0xE3,
    "right ctrl": 0xE4,
    "right shift": 0xE5,
    "right alt": 0xE6,
    "right windows": 0xE7,
    # 小鍵盤
    "keypad /": 0x54,
    "keypad *": 0x55,
    "keypad -": 0x56,
    "keypad +": 0x57,
    "keypad enter": 0x58,
    "keypad 1": 0x59,
    "keypad 2": 0x5A,
    "keypad 3": 0x5B,
    "keypad 4": 0x5C,
    "keypad 5": 0x5D,
    "keypad 6": 0x5E,
    "keypad 7": 0x5F,
    "keypad 8": 0x60,
    "keypad 9": 0x61,
    "keypad 0": 0x62,
    "keypad .": 0x63,
}


def key_name_to_qmk(key_name: str) -> int | None:
    """
    將按鍵名稱轉換為 QMK keycode (HID usage code)。
    
    Args:
        key_name: keyboard 庫返回的按鍵名稱（小寫）
    
    Returns:
        QMK keycode，如果無法映射則返回 None
    """
    # 標準化按鍵名稱（轉小寫，移除空格）
    normalized = key_name.lower().strip()
    
    # 直接查找
    if normalized in KEY_NAME_TO_QMK:
        return KEY_NAME_TO_QMK[normalized]
    
    # 嘗試處理一些變體
    variants = {
        "return": "enter",
        "back space": "backspace",
        "caps": "caps lock",
        "ctrl": "left ctrl",
        "shift": "left shift",
        "alt": "left alt",
        "win": "left windows",
        "cmd": "left windows",
        "super": "left windows",
    }
    
    if normalized in variants:
        normalized = variants[normalized]
        if normalized in KEY_NAME_TO_QMK:
            return KEY_NAME_TO_QMK[normalized]
    
    return None
