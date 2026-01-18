#!/usr/bin/env python3
"""打包腳本：將應用程式打包成可執行檔"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent


def main() -> int:
    """執行打包流程"""
    print("開始打包 EzErgo Overlay...")
    
    # 檢查 PyInstaller 是否已安裝
    try:
        import PyInstaller
    except ImportError:
        print("錯誤：未找到 PyInstaller")
        print("請執行：pip install pyinstaller")
        print("或執行：pip install -e '.[build]'")
        return 1
    
    # 檢查 third_party 目錄是否存在
    third_party = PROJECT_ROOT / "third_party" / "vial-gui"
    if not third_party.exists():
        print("警告：third_party/vial-gui 目錄不存在")
        print("這可能會導致某些功能無法正常工作")
    
    # 執行 PyInstaller
    spec_file = PROJECT_ROOT / "ezergo_overlay.spec"
    if not spec_file.exists():
        print(f"錯誤：找不到 spec 文件 {spec_file}")
        return 1
    
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        str(spec_file),
    ]
    
    print(f"執行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    
    if result.returncode == 0:
        exe_path = PROJECT_ROOT / "dist" / "ezergo-overlay"
        print(f"\n✓ 打包完成！")
        print(f"可執行檔位於: {exe_path}")
        print(f"\n執行方式: {exe_path}")
        return 0
    else:
        print("\n✗ 打包失敗！")
        return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
