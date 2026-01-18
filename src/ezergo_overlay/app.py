from __future__ import annotations

import sys
import threading
import time
from dataclasses import dataclass

from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtWidgets import QApplication, QMessageBox

from ezergo_overlay.model.keymap_model import Keymap
from ezergo_overlay.singleton import SingleInstance
from ezergo_overlay.ui.overlay_window import OverlayWindow
from ezergo_overlay.ui.tray import TrayController
from ezergo_overlay.vial.errors import HidNotAvailableError
from ezergo_overlay.vial.hid_transport import find_first_vial_device, open_hid_path
from ezergo_overlay.vial.vial_client import VialClient


@dataclass(frozen=True, slots=True)
class AppState:
    connected: bool
    status_text: str


class VialWorker(QObject):
    keymap_ready = Signal(object)  # Keymap
    client_ready = Signal(object)  # VialClient
    status_changed = Signal(object)  # AppState

    def __init__(self) -> None:
        super().__init__()
        self._stop = threading.Event()
        self._client: VialClient | None = None
        self._last_layer: int | None = None

    def stop(self) -> None:
        self._stop.set()
        c = self._client
        self._client = None
        if c is not None:
            c.close()

    def reconnect(self) -> None:
        c = self._client
        self._client = None
        if c is not None:
            c.close()
        self._last_layer = None

    def run_loop(self) -> None:
        while not self._stop.is_set():
            if self._client is None:
                try:
                    self._try_connect()
                except HidNotAvailableError:
                    self.status_changed.emit(AppState(connected=False, status_text="缺少 HID 後端"))
                    time.sleep(2.0)
                except Exception as e:
                    msg = str(e).strip().replace("\n", " ")
                    if msg:
                        msg = msg[:80]
                        text = f"連線失敗:{type(e).__name__}:{msg}"
                    else:
                        text = f"連線失敗:{type(e).__name__}"
                    self.status_changed.emit(AppState(connected=False, status_text=text))
                    time.sleep(1.0)
                time.sleep(0.5)
                continue

            try:
                self._client.ping()
                time.sleep(0.6)
            except Exception:
                self.status_changed.emit(AppState(connected=False, status_text="斷線"))
                self.reconnect()
                time.sleep(0.5)

    def _try_connect(self) -> None:
        self.status_changed.emit(AppState(connected=False, status_text="搜尋鍵盤"))
        dev = find_first_vial_device()
        if dev is None:
            return
        try:
            t = open_hid_path(dev.path)
            self._client = VialClient(t)
            keymap: Keymap = self._client.read_full_keymap()
            self.keymap_ready.emit(keymap)
            self.client_ready.emit(self._client)
            self.status_changed.emit(AppState(connected=True, status_text="已連線"))
        except Exception as e:
            msg = str(e).strip().replace("\n", " ")
            if msg:
                msg = msg[:80]
                text = f"連線失敗:{type(e).__name__}:{msg}"
            else:
                text = f"連線失敗:{type(e).__name__}"
            self.status_changed.emit(AppState(connected=False, status_text=text))
            self.reconnect()


def main() -> int:
    # 檢查是否已有實例在運行
    singleton = SingleInstance()
    if singleton.is_running():
        # 需要創建 QApplication 才能顯示訊息框
        app = QApplication(sys.argv)
        QMessageBox.warning(
            None,
            "應用程式已運行",
            "EzErgo Overlay 已經在運行中，無法啟動第二個實例。",
        )
        return 1

    # 獲取鎖並保持應用程式運行期間
    try:
        with singleton:
            app = QApplication(sys.argv)

            win = OverlayWindow()
            win.show()

            worker = VialWorker()
            thread = threading.Thread(target=worker.run_loop, daemon=True)

            def on_reconnect() -> None:
                worker.reconnect()

            tray = TrayController(win, on_reconnect=on_reconnect)
            tray.show()

            worker.keymap_ready.connect(win.set_keymap)
            worker.client_ready.connect(win.set_vial_client)
            worker.status_changed.connect(lambda s: tray.set_status(s.status_text))
            worker.status_changed.connect(lambda s: win.set_status(s.status_text))

            thread.start()

            def on_about_to_quit() -> None:
                worker.stop()

            app.aboutToQuit.connect(on_about_to_quit)

            # Ensure timer exists so Qt keeps event loop responsive on some platforms
            keepalive = QTimer()
            keepalive.start(1000)
            keepalive.timeout.connect(lambda: None)

            return app.exec()
    except (OSError, IOError):
        # 如果無法獲取鎖（理論上不應該發生，因為已經檢查過）
        # 但在極少數情況下可能發生競態條件
        app = QApplication(sys.argv)
        QMessageBox.warning(
            None,
            "啟動失敗",
            "無法啟動應用程式，可能已有實例在運行。",
        )
        return 1


