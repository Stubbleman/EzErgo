from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Final

from ezergo_overlay.vial.errors import VialProtocolError
from ezergo_overlay.vial.hid_transport import IHidTransport
from ezergo_overlay.vial.constants import MSG_LEN


@dataclass(frozen=True, slots=True)
class VialPacket:
    """
    Raw 32-byte HID payload (without report id).
    """

    data: bytes


def ensure_report_size(data: bytes, report_size: int) -> bytes:
    if len(data) > report_size:
        raise VialProtocolError(f"packet too large: {len(data)} > {report_size}")
    return data.ljust(report_size, b"\x00")


class VialHidProtocol:
    """
    Minimal HID framing compatible with Vial/VIA rawhid usage.

    - payload length is fixed to 32 bytes (MSG_LEN)
    - HID write requires a leading report id 0x00, so we write 33 bytes total
    """

    _report_id: Final[bytes] = b"\x00"

    def __init__(self, transport: IHidTransport, timeout_ms: int = 500, retries: int = 3) -> None:
        self._t = transport
        self._timeout_ms = int(timeout_ms)
        self._retries = int(retries)

    def close(self) -> None:
        self._t.close()

    def exchange(self, msg: bytes) -> bytes:
        """
        Send a single command and read back the 32-byte response.
        """
        payload = ensure_report_size(msg, MSG_LEN)
        last_err: Exception | None = None
        for attempt in range(max(1, self._retries)):
            if attempt:
                time.sleep(0.15)
            try:
                written = self._t.write(self._report_id + payload)
                if written < 1:
                    continue
                data = self._t.read(MSG_LEN, timeout_ms=self._timeout_ms)
                if not data:
                    continue
                if len(data) != MSG_LEN:
                    # Some stacks may return shorter reads; pad defensively.
                    data = data.ljust(MSG_LEN, b"\x00")
                return data
            except Exception as e:
                last_err = e
                continue
        if last_err is not None:
            raise VialProtocolError(
                f"failed to communicate with the device over HID: {type(last_err).__name__}: {last_err}"
            ) from last_err
        raise VialProtocolError("failed to communicate with the device over HID: empty response")


