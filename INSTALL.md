# 安裝指南

## 方法 1: 使用虛擬環境（推薦）

創建並激活虛擬環境：

```bash
# 創建虛擬環境
python3 -m venv venv

# 激活虛擬環境
source venv/bin/activate

# 安裝依賴
pip install -e .
```

之後運行應用時，確保虛擬環境已激活：
```bash
source venv/bin/activate
python3 -m ezergo_overlay
```

## 方法 2: 直接安裝到用戶環境

```bash
pip install --user -e .
```

或者只安裝依賴：
```bash
pip install --user PySide6>=6.6 hidapi>=0.15.0 keyboard>=0.13.5
```

## 方法 3: 使用 pipx（如果已安裝）

```bash
pipx install -e .
```

## 驗證安裝

運行以下命令檢查依賴是否已安裝：

```bash
python3 -c "import PySide6; import hidapi; import keyboard; print('所有依賴已安裝')"
```

## 常見問題

### ModuleNotFoundError: No module named 'PySide6'

這表示依賴未安裝。請使用上述方法之一安裝依賴。

### 權限問題

如果遇到鍵盤監聽權限問題，請參考 `KEYBOARD_PERMISSIONS.md`。
