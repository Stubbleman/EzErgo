# 安裝指南

## 方法 1: 使用虛擬環境（推薦）

創建並啟用虛擬環境：

```bash
# 創建虛擬環境
python3 -m venv venv

# 啟用虛擬環境
source venv/bin/activate

# 安裝套件
pip install -e .
```

之後運行應用時，確保虛擬環境已啟用：
```bash
source venv/bin/activate
python3 -m ezergo_overlay
```

## 方法 2: 直接安裝到用戶環境

```bash
pip install --user -e .
```

或者只安裝套件：
```bash
pip install --user PySide6>=6.6 hidapi>=0.15.0 keyboard>=0.13.5
```

## 方法 3: 使用 pipx（如果已安裝）

```bash
pipx install -e .
```

## 驗證安裝

運行以下命令檢查套件是否已安裝：

```bash
python3 -c "import PySide6; import hidapi; import keyboard; print('所有套件已安裝')"
```

檢查鍵碼標籤功能是否可用：

```bash
python3 -c "import sys; sys.path.insert(0, 'src'); from ezergo_overlay.vial.vial_imports import is_keycode_available; print('鍵碼標籤功能:', '可用' if is_keycode_available() else '不可用（將顯示十六進制）')"
```

## 常見問題

### ModuleNotFoundError: No module named 'PySide6'

這表示套件未安裝。請使用上述方法之一安裝套件。

### 權限問題

如果遇到鍵盤監聽權限問題，請參考 `KEYBOARD_PERMISSIONS.md`。

### 鍵碼顯示為十六進制（如 0x0004）而不是標籤（如 "A"）

這表示 `simpleeval` 套件未安裝或未在正確的 Python 環境中。解決方法：

1. **如果使用虛擬環境**，確保已啟用並安裝套件：
   ```bash
   source venv/bin/activate  # 或 .venv/bin/activate
   pip install -e '.[vial]'
   ```

2. **如果直接安裝到用戶環境**：
   ```bash
   pip install --user simpleeval
   ```

3. **驗證安裝**：
   ```bash
   python3 -c "import simpleeval; print('simpleeval 已安裝')"
   ```

安裝後重新運行應用程式即可看到正確的鍵碼標籤。
