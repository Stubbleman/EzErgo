from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, Protocol

from ezergo_overlay.vial.errors import HidNotAvailableError
from ezergo_overlay.vial.constants import RAW_HID_USAGE, RAW_HID_USAGE_PAGE, VIAL_SERIAL_NUMBER_MAGIC


@dataclass(frozen=True, slots=True)
class HidDeviceInfo:
    path: bytes
    vendor_id: int
    product_id: int
    usage_page: int | None = None
    usage: int | None = None
    manufacturer: str | None = None
    product: str | None = None
    serial_number: str | None = None


class IHidTransport(Protocol):
    def write(self, data: bytes) -> int: ...
    def read(self, size: int, timeout_ms: int) -> bytes: ...
    def close(self) -> None: ...


def _require_hid_module():
    try:
        # Prefer `hidraw` (often provided by wheels that bundle native bits).
        # Fallback to `hid` when available.
        import hidraw as hid  # type: ignore
        return hid
    except Exception as e:  # pragma: no cover
        last_err = e
    try:
        import hid  # type: ignore
        return hid
    except Exception as e:  # pragma: no cover
        raise HidNotAvailableError(
            "缺少可用的 HID 後端：請安裝 pip 套件 `hidapi`（提供 hidraw），或安裝系統 hidapi。"
        ) from e


def enumerate_hid_devices() -> list[HidDeviceInfo]:
    hid = _require_hid_module()
    devices = []
    for d in hid.enumerate():
        path = d.get("path")
        if not path:
            continue
        devices.append(
            HidDeviceInfo(
                path=path,
                vendor_id=int(d.get("vendor_id") or 0),
                product_id=int(d.get("product_id") or 0),
                usage_page=(int(d.get("usage_page")) if d.get("usage_page") is not None else None),
                usage=(int(d.get("usage")) if d.get("usage") is not None else None),
                manufacturer=d.get("manufacturer_string"),
                product=d.get("product_string"),
                serial_number=d.get("serial_number"),
            )
        )
    return devices


class HidTransport(IHidTransport):
    def __init__(self, device):
        self._device = device

    def write(self, data: bytes) -> int:
        return int(self._device.write(data))

    def read(self, size: int, timeout_ms: int) -> bytes:
        data = self._device.read(size, timeout_ms)
        return bytes(data)

    def close(self) -> None:
        try:
            self._device.close()
        except Exception:
            pass


def open_hid_path(path: bytes) -> HidTransport:
    hid = _require_hid_module()
    dev = hid.device()
    dev.open_path(path)
    # Let backend handle timeouts in read(); we will pass timeout_ms there.
    # Note: `hidraw` backend may not expose set_nonblocking().
    try:
        set_nb = getattr(dev, "set_nonblocking", None)
        if callable(set_nb):
            set_nb(0)
    except Exception:
        # Non-fatal; we'll rely on read(timeout_ms=...) behavior.
        pass
    return HidTransport(dev)


def find_first_matching_device(
    vendor_ids: Optional[Iterable[int]] = None,
    product_ids: Optional[Iterable[int]] = None,
) -> HidDeviceInfo | None:
    vids = set(vendor_ids or [])
    pids = set(product_ids or [])
    for d in enumerate_hid_devices():
        if vids and d.vendor_id not in vids:
            continue
        if pids and d.product_id not in pids:
            continue
        return d
    return None


def is_vial_rawhid_device(d: HidDeviceInfo) -> bool:
    serial = d.serial_number or ""
    has_vial_serial = VIAL_SERIAL_NUMBER_MAGIC in serial

    # Prefer rawhid usage match when provided; this is what vial-gui checks on Linux.
    has_usage = d.usage_page is not None and d.usage is not None
    has_rawhid_usage = (d.usage_page == RAW_HID_USAGE_PAGE and d.usage == RAW_HID_USAGE)

    if has_usage:
        return has_rawhid_usage
    # Some platforms may not provide usage_page/usage; fall back to serial magic only.
    return has_vial_serial


def find_first_vial_device() -> HidDeviceInfo | None:
    for d in enumerate_hid_devices():
        if is_vial_rawhid_device(d):
            return d
    return None


