# EzErgo Overlay

EzErgo Overlay 是一個鍵盤提示應用程式，用於顯示 Vial 鍵盤的鍵位。它會在螢幕上顯示一個半透明的覆蓋視窗，即時顯示當前鍵盤層的按鍵配置。這是我開發來熟悉自製分離式鍵盤的救星😂


## 功能特點

- 自動連接到 Vial 鍵盤設備
- 實時顯示當前鍵盤層的鍵位映射
- 支援多層鍵盤配置切換
- 可自訂的覆蓋視窗樣式（透明度、顏色等）
- 系統工具列圖示，方便管理
- 按鍵醒目顯示（顯示當前按下的按鍵）

## 系統需求

- Python 3.10 或更高版本
- Linux 系統
- 支援 Vial 的鍵盤設備
- Git（用於Clone 倉儲）

## 獲取原始碼

首先，您需要Clone倉儲並初始化子模組：

```bash
# Clone 倉儲
git clone https://github.com/Stubbleman/EzErgo.git EzErgo
cd EzErgo

# 初始化並更新子模組（Vial-GUI）
git submodule update --init --recursive
```

## 安裝

安裝應用程式需要先安裝套件，然後執行打包腳本：

```bash
# 安裝打包套件（PyInstaller 和專案套件）
pip install -e '.[build]'

# 執行打包腳本
python3 build.py
```

打包完成後，可執行檔將位於 `dist/ezergo-overlay`。

**注意**：如果您的系統沒有安裝 pip，請先安裝 Python 的包管理器。在大多數 Linux 發行版中，可以使用：

```bash
# Debian/Ubuntu
sudo apt install python3-pip

# Fedora (Not verify)
sudo dnf install python3-pip

# Arch Linux (Not verify)
sudo pacman -S python-pip
```

## 執行

執行打包後的可執行檔：

```bash
./dist/ezergo-overlay
```

或者使用完整路徑：

```bash
# 設置項目目錄變數（請根據您的實際路徑修改）
PROJECT_DIR="$HOME/Projects/EzErgo"
$PROJECT_DIR/dist/ezergo-overlay
```

## 創建桌面快捷方式

您可以創建一個 `.desktop` 文件來在應用程式選單中新增程式，方便從桌面環境快速啟動應用程式。

1. 創建 `.desktop` 文件：

```bash
# 設置項目目錄變數（請根據您的實際路徑修改）
PROJECT_DIR="$HOME/Projects/EzErgo"

mkdir -p ~/.local/share/applications
cat > ~/.local/share/applications/ezergo-overlay.desktop << EOF
[Desktop Entry]
Name=EzErgo Overlay
Comment=鍵盤提示應用程式，顯示 Vial 鍵盤的鍵位映射
Exec=$PROJECT_DIR/dist/ezergo-overlay
Icon=application-x-executable
Terminal=false
Type=Application
Categories=Utility;
EOF
```

**注意**：請將 `PROJECT_DIR` 變數設置為您實際的項目目錄路徑。

2. 設置執行權限：

```bash
chmod +x ~/.local/share/applications/ezergo-overlay.desktop
```

3. 更新應用程式資料庫（可選）：

```bash
update-desktop-database ~/.local/share/applications
```

### 快速驗測試

創建完成後，您應該能夠：

- 在應用程式選單中找到 "EzErgo Overlay"
- 雙擊桌面上的快捷方式啟動應用程式（如果複製到桌面）

### 自訂圖標（選擇性）

如果您有自訂的應用程式圖示，可以將圖示文件放在 `~/.local/share/icons/` 目錄下，然後在 `.desktop` 文件的 `Icon` 欄位中指定圖示名稱或完整路徑。

## 操作說明

### 解鎖鍵盤

> ⚠️ **警告**：解鎖鍵盤時請務必在**受信任的環境**下操作，避免在可能不安全的電腦或網路環境中進行解鎖動作，以確保您的設備安全。

啟動程式時會先邀請您將鍵盤解鎖，除非您原本就沒有安全設定（不建議這麼做）
您應該要設定```VIAL_UNLOCK_COMBO```

### 系統工具列

應用程式啟動後會在系統工具列中顯示圖示。您可以：

- **點擊工具列圖示**：切換覆蓋視窗的顯示/隱藏
- **右鍵點擊工具列圖示**：打開上下文選單
  - **狀態**：顯示當前連接狀態
  - **顯示/隱藏**：切換覆蓋視窗的顯示/隱藏
  - **重新連線**：重新連接鍵盤設備
  - **退出**：關閉應用程式

### 提示視窗

提示視窗顯示鍵盤的鍵位映射，包含以下功能：

- **◀ 按鈕**：切換到上一層
- **▶ 按鈕**：切換到下一層
- **隱藏按鈕**：隱藏覆蓋視窗（可通過托盤圖標重新顯示）
- **⚙ 按鈕**：打開設置視窗

### 視窗操作

- **拖動視窗**：點擊標題欄區域並拖動來移動視窗位置
- **調整大小**：使用右下角的大小調整手柄來調整視窗大小

### 設置視窗

點擊覆蓋視窗上的 ⚙ 按鈕打開設置視窗，可以調整：

- **總是在最上層**：讓覆蓋視窗始終顯示在其他視窗之上
- **背景透明度**：調整覆蓋視窗背景的透明度（0-255）
- **按鍵顏色**：自訂按鍵的顯示顏色
- **其他視覺設定**：根據需要調整其他顯示選項

### 鍵盤層切換

- 使用覆蓋視窗上的 ◀ 和 ▶ 按鈕手動切換層
- 應用程式會自動偵測鍵盤上的層切換按鍵（MO 鍵），並同步顯示對應的層

### 按鍵提示

當您按下鍵盤上的按鍵時，覆蓋視窗中對應的按鍵會變色顯示，幫助您了解當前按下的鍵位。

## 常見問題

### ModuleNotFoundError: No module named 'PySide6'

這表示套件未安裝。請使用上述安裝方法之一安裝套件。

### 無法連接到鍵盤

- 確保您的鍵盤支援 Vial 協議
- 檢查鍵盤是否已正確連接
- 嘗試點擊托盤圖標的「重新連線」選項
- 確保您有權限訪問 HID 設備（可能需要將用戶添加到相應的用戶組）

### 權限問題

如果遇到鍵盤監聽權限問題，可能需要：

- 將用戶新增到 `input` 或 `plugdev` 用戶組
- 配置 udev 規則以允許訪問 HID 設備

### 應用程式無法啟動（已運行）

應用程式只允許一個實例運行。如果看到此錯誤，表示已經有一個實例在運行中。您可以通過系統工具列圖示來開啟現有實例。

## 開發

### 專案結構

```
src/ezergo_overlay/
├── app.py              # 主應用程式邏輯
├── model/              # 數據模型
│   ├── keymap_model.py
│   ├── settings.py
│   └── ...
├── ui/                 # 用戶界面
│   ├── overlay_window.py
│   ├── tray.py
│   └── ...
└── vial/               # Vial 協議實現
    ├── vial_client.py
    └── ...
```

### 套件

主要套件：
- PySide6 >= 6.6：GUI 框架
- hidapi >= 0.15.0：HID 設備通訊

開發套件：
- pyinstaller >= 6.0：打包工具

## 授權

請查看專案根目錄的授權文件以了解詳細訊息。
