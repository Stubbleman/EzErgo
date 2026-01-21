#!/usr/bin/env python3
"""檢查鍵碼標籤功能是否可用"""
import sys

def check_keycode_support():
    """檢查 Keycode 支持是否可用"""
    print("檢查鍵碼標籤功能...")
    print(f"Python: {sys.executable}")
    print(f"在虛擬環境中: {hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)}")
    print()
    
    # 檢查 simpleeval
    try:
        import simpleeval
        print(f"✓ simpleeval 已安裝: {simpleeval.__file__}")
    except ImportError:
        print("✗ simpleeval 未安裝")
        print("  解決方案: pip install simpleeval 或 pip install -e '.[vial]'")
        return False
    
    # 檢查 Keycode 導入
    sys.path.insert(0, 'src')
    try:
        from ezergo_overlay.vial.vial_imports import is_keycode_available, get_keycode
        if is_keycode_available():
            print("✓ Keycode 類可用")
            kc = get_keycode()
            if kc:
                # 測試一個鍵碼
                test_code = 0x04
                qmk_id = kc.serialize(test_code)
                label = kc.label(qmk_id)
                print(f"  測試 0x04: {qmk_id} -> {label}")
                print()
                print("✓ 鍵碼標籤功能正常！")
                return True
        else:
            print("✗ Keycode 類不可用")
            return False
    except Exception as e:
        print(f"✗ 檢查失敗: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = check_keycode_support()
    sys.exit(0 if success else 1)
