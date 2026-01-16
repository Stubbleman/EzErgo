from __future__ import annotations

import json
import lzma
import struct
import time
from dataclasses import dataclass
from typing import Optional

from ezergo_overlay.model.keymap_model import Keymap, MatrixSize, PhysicalKey
from ezergo_overlay.vial.constants import (
    BUFFER_FETCH_CHUNK,
    CMD_VIA_GET_LAYER_COUNT,
    CMD_VIA_GET_PROTOCOL_VERSION,
    CMD_VIA_KEYMAP_GET_BUFFER,
    CMD_VIA_VIAL_PREFIX,
    CMD_VIAL_GET_DEFINITION,
    CMD_VIAL_GET_KEYBOARD_ID,
    CMD_VIAL_GET_SIZE,
    MSG_LEN,
)
from ezergo_overlay.vial.errors import VialProtocolError, VialTimeoutError
from ezergo_overlay.vial.hid_transport import IHidTransport
from ezergo_overlay.vial.kle_min import deserialize_kle
from ezergo_overlay.vial.vial_protocol import VialHidProtocol


@dataclass(frozen=True, slots=True)
class VialDeviceMeta:
    matrix: MatrixSize
    layers: int
    via_protocol: int
    vial_protocol: int
    keyboard_id: int


class VialClient:
    """
    High-level API used by the UI.
    """

    def __init__(self, transport: IHidTransport):
        self._t = VialHidProtocol(transport)
        self._meta: VialDeviceMeta | None = None
        self._definition: dict | None = None

    def close(self) -> None:
        self._t.close()

    def get_device_meta(self) -> VialDeviceMeta:
        if self._meta is not None:
            return self._meta

        via_protocol = self._read_via_protocol()
        vial_protocol, keyboard_id = self._read_vial_keyboard_id()

        definition = self._get_keyboard_definition()
        rows = int(definition["matrix"]["rows"])
        cols = int(definition["matrix"]["cols"])

        layers = self._read_layer_count()
        self._meta = VialDeviceMeta(
            matrix=MatrixSize(rows=rows, cols=cols),
            layers=layers,
            via_protocol=via_protocol,
            vial_protocol=vial_protocol,
            keyboard_id=keyboard_id,
        )
        return self._meta

    def read_full_keymap(self) -> Keymap:
        meta = self.get_device_meta()
        keymap_bytes = self._read_keymap_buffer(meta.layers, meta.matrix)
        layers_data: list[list[int]] = []

        idx = 0
        for _layer in range(meta.layers):
            layer_data: list[int] = []
            for _ in range(meta.matrix.key_count):
                kc = struct.unpack_from(">H", keymap_bytes, idx)[0]
                layer_data.append(int(kc))
                idx += 2
            layers_data.append(layer_data)
        physical = self._extract_physical_keys(self._get_keyboard_definition(), meta.matrix)
        return Keymap(
            matrix=meta.matrix,
            layers=meta.layers,
            layers_data=layers_data,
            physical_keys=physical or None,
        )

    def poll_current_layer(self, timeout_s: float = 0.3) -> int:
        # Note: Vial/VIA protocol does not expose "currently active layer" on the keyboard in a
        # portable way (vial-gui keeps it as a UI-selected layer).
        # We keep this method for future firmware-side support; for now it returns 0.
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            return 0
        raise VialTimeoutError("timeout while polling current layer")

    def ping(self) -> None:
        """
        Lightweight request to keep connection exercised and detect disconnects.
        """
        _ = self._read_layer_count()

    def _read_via_protocol(self) -> int:
        data = self._t.exchange(struct.pack("B", CMD_VIA_GET_PROTOCOL_VERSION))
        # Response format: [cmd][u16 protocol]...
        return int(struct.unpack(">H", data[1:3])[0])

    def _read_layer_count(self) -> int:
        data = self._t.exchange(struct.pack("B", CMD_VIA_GET_LAYER_COUNT))
        # Response format: [cmd][layers]...
        return int(data[1])

    def _read_vial_keyboard_id(self) -> tuple[int, int]:
        data = self._t.exchange(struct.pack("BB", CMD_VIA_VIAL_PREFIX, CMD_VIAL_GET_KEYBOARD_ID))
        # Response format: <I vial_protocol><Q keyboard_id>...
        vial_protocol, keyboard_id = struct.unpack("<IQ", data[0:12])
        return int(vial_protocol), int(keyboard_id)

    def _get_keyboard_definition(self) -> dict:
        if self._definition is not None:
            return self._definition
        self._definition = self._read_keyboard_definition()
        return self._definition

    def _read_keyboard_definition(self) -> dict:
        data = self._t.exchange(struct.pack("BB", CMD_VIA_VIAL_PREFIX, CMD_VIAL_GET_SIZE))
        sz = int(struct.unpack("<I", data[0:4])[0])
        if sz <= 0 or sz > 5_000_000:
            raise VialProtocolError(f"unexpected definition size: {sz}")

        payload = bytearray()
        remaining = sz
        block = 0
        while remaining > 0:
            page = self._t.exchange(
                struct.pack("<BBI", CMD_VIA_VIAL_PREFIX, CMD_VIAL_GET_DEFINITION, block)
            )
            take = min(remaining, MSG_LEN)
            payload += page[:take]
            remaining -= take
            block += 1

        try:
            raw = lzma.decompress(bytes(payload))
            return json.loads(raw)
        except Exception as e:
            raise VialProtocolError("failed to decode keyboard definition") from e

    def _extract_physical_keys(self, definition: dict, matrix: MatrixSize) -> list[PhysicalKey]:
        """
        Extract physical layout from Vial definition.

        We look for KLE keys that embed matrix row/col labels like "r,c".
        If not present, we fall back to empty list (grid view will be used).
        """
        layouts = definition.get("layouts") or {}
        keymap = layouts.get("keymap")
        if not isinstance(keymap, list):
            return []

        out: list[PhysicalKey] = []
        for k in deserialize_kle(keymap):
            row_col: tuple[int, int] | None = None
            for lbl in k.labels:
                if not lbl or "," not in lbl:
                    continue
                a, b = lbl.split(",", 1)
                try:
                    row = int(a.strip())
                    col = int(b.strip())
                except ValueError:
                    continue
                row_col = (row, col)
                break
            if row_col is None:
                continue
            row, col = row_col
            if row < 0 or col < 0 or row >= matrix.rows or col >= matrix.cols:
                continue
            out.append(PhysicalKey(x=k.x, y=k.y, w=k.w, h=k.h, row=row, col=col))

        out.sort(key=lambda kk: (kk.y, kk.x, kk.row, kk.col))
        return out

    def _read_keymap_buffer(self, layers: int, matrix: MatrixSize) -> bytes:
        size = int(layers) * int(matrix.rows) * int(matrix.cols) * 2
        out = bytearray()
        for offset in range(0, size, BUFFER_FETCH_CHUNK):
            sz = min(BUFFER_FETCH_CHUNK, size - offset)
            req = struct.pack(">BHB", CMD_VIA_KEYMAP_GET_BUFFER, offset, sz)
            resp = self._t.exchange(req)
            # Most firmwares echo the 4-byte header, payload begins at offset 4.
            # Some test/mocked stacks only include the cmd byte, so fall back to offset 1.
            if resp[:4] == req:
                start = 4
            elif resp[0:1] == req[0:1]:
                start = 1
            else:
                raise VialProtocolError("unexpected keymap buffer response header")
            out += resp[start : start + sz]
        if len(out) != size:
            raise VialProtocolError(f"keymap buffer size mismatch: {len(out)} != {size}")
        return bytes(out)


