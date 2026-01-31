# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for EzErgo Overlay
"""

import sys
import os
from pathlib import Path

block_cipher = None

# Project root directory (spec file location)
# SPECPATH is a built-in variable in PyInstaller spec files
# When running from build.py, the working directory is the project root
project_root = Path(SPECPATH) if 'SPECPATH' in globals() else Path.cwd()

# Source directory
src_dir = project_root / "src"

# Third party directory
third_party_dir = project_root / "third_party"

# Collect all Python files from ezergo_overlay package
a = Analysis(
    [str(src_dir / "ezergo_overlay" / "__main__.py")],
    pathex=[str(src_dir)],
    binaries=[],
    datas=[
        # Include third_party directory as data files
        (str(third_party_dir), "third_party"),
    ],
    hiddenimports=[
        # PySide6/Qt imports
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        # HID API
        "hid",
        "hidapi",
        # Standard library modules that might be dynamically imported
        "threading",
        "dataclasses",
        "functools",
        "importlib.machinery",
        "types",
        "ast",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="ezergo-overlay",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Windows GUI application (no console window)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Can add icon file path here if available
)
