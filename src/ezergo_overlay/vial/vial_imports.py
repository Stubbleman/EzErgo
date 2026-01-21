from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from types import ModuleType


def _project_root() -> Path:
    """獲取專案根目錄，支援打包後的環境"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包後的環境
        base_path = Path(sys.executable).parent
        third_party_path = base_path / 'third_party' / 'vial-gui' / 'src' / 'main' / 'python'
        if third_party_path.exists():
            return base_path
        if hasattr(sys, '_MEIPASS'):
            return Path(sys._MEIPASS)
    # 正常環境：從當前文件位置推算
    return Path(__file__).resolve().parents[3]


def _vial_gui_py_root() -> Path:
    """獲取 vial-gui Python 源碼目錄，支援打包後的環境"""
    if getattr(sys, 'frozen', False):
        base_path = _project_root()
        third_party_path = base_path / 'third_party' / 'vial-gui' / 'src' / 'main' / 'python'
        if third_party_path.exists():
            return third_party_path
        if hasattr(sys, '_MEIPASS'):
            meipass_path = Path(sys._MEIPASS) / 'third_party' / 'vial-gui' / 'src' / 'main' / 'python'
            if meipass_path.exists():
                return meipass_path
    return _project_root() / "third_party" / "vial-gui" / "src" / "main" / "python"


def _ensure_vial_gui_in_path() -> bool:
    """確保 vial-gui 路徑在 sys.path 中，返回是否成功"""
    root = _vial_gui_py_root()
    if not root.exists():
        return False
    root_str = str(root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    return True


# 嘗試導入 Keycode 類
_Keycode: type | None = None
_keycode_available = False

if _ensure_vial_gui_in_path():
    try:
        from keycodes.keycodes import Keycode  # type: ignore[import-untyped]
        _Keycode = Keycode
        # 設置協議版本為 v6
        Keycode.protocol = 6
        _keycode_available = True
    except ModuleNotFoundError as e:
        # 如果缺少依賴（如 simpleeval），記錄錯誤但優雅降級
        if 'simpleeval' in str(e):
            # 可以選擇性地記錄警告，但不影響運行
            pass
        _keycode_available = False
        _Keycode = None
    except (ImportError, AttributeError, Exception):
        # 其他導入錯誤，優雅降級
        _keycode_available = False
        _Keycode = None


def is_keycode_available() -> bool:
    """檢查 Keycode 類是否可用"""
    return _keycode_available


def get_keycode() -> type | None:
    """獲取 Keycode 類，如果不可用則返回 None"""
    return _Keycode
