"""單例執行檢查模組，確保應用程式只能同時執行一次。"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Platform-specific imports for file locking
if sys.platform == "win32":
    import msvcrt
else:
    import fcntl


class SingleInstance:
    """使用文件鎖確保應用程式只能同時執行一次。"""

    def __init__(self, lock_file: str | Path | None = None) -> None:
        """
        初始化單例檢查器。

        Args:
            lock_file: 鎖定文件路徑。如果為 None，使用預設路徑。
        """
        if lock_file is None:
            lock_file = Path.home() / ".ezergo_overlay.lock"
        self.lock_file = Path(lock_file)
        self.lock_fd: int | None = None
        self._is_windows = sys.platform == "win32"

    def _lock_file(self, fd: int) -> None:
        """鎖定文件（跨平台實現）。"""
        if self._is_windows:
            # Windows: 使用 msvcrt.locking
            # 鎖定第一個字節（非阻塞）
            os.lseek(fd, 0, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
        else:
            # Unix/Linux: 使用 fcntl.flock
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

    def _unlock_file(self, fd: int) -> None:
        """解鎖文件（跨平台實現）。"""
        if self._is_windows:
            # Windows: 使用 msvcrt.locking
            os.lseek(fd, 0, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
        else:
            # Unix/Linux: 使用 fcntl.flock
            fcntl.flock(fd, fcntl.LOCK_UN)

    def __enter__(self) -> SingleInstance:
        """進入上下文管理器，嘗試獲取鎖。"""
        try:
            self.lock_fd = os.open(self.lock_file, os.O_CREAT | os.O_WRONLY | os.O_TRUNC)
            self._lock_file(self.lock_fd)
            # 寫入當前進程的 PID
            os.write(self.lock_fd, str(os.getpid()).encode())
            os.fsync(self.lock_fd)
            return self
        except (OSError, IOError):
            if self.lock_fd is not None:
                os.close(self.lock_fd)
                self.lock_fd = None
            raise

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """退出上下文管理器，釋放鎖。"""
        if self.lock_fd is not None:
            try:
                self._unlock_file(self.lock_fd)
                os.close(self.lock_fd)
                if self.lock_file.exists():
                    self.lock_file.unlink()
            except (OSError, IOError):
                pass
            finally:
                self.lock_fd = None

    def is_running(self) -> bool:
        """
        檢查是否有其他實例正在運行。

        Returns:
            如果有其他實例正在運行，返回 True；否則返回 False。
        """
        if not self.lock_file.exists():
            return False

        try:
            # Windows 需要可讀寫模式才能鎖定
            open_flags = os.O_RDWR if self._is_windows else os.O_RDONLY
            fd = os.open(self.lock_file, open_flags)
            try:
                self._lock_file(fd)
                # 如果能獲取鎖，說明沒有其他實例在運行
                self._unlock_file(fd)
                return False
            finally:
                os.close(fd)
        except (OSError, IOError):
            # 無法獲取鎖，說明有其他實例在運行
            return True
