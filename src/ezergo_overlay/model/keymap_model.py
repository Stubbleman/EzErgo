from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True, slots=True)
class MatrixSize:
    rows: int
    cols: int

    @property
    def key_count(self) -> int:
        return self.rows * self.cols


@dataclass(frozen=True, slots=True)
class PhysicalKey:
    """
    Physical key position in KLE units (not pixels).
    """

    x: float
    y: float
    w: float
    h: float
    row: int
    col: int


@dataclass(frozen=True, slots=True)
class Keymap:
    matrix: MatrixSize
    layers: int
    # layers_data[layer][index] => keycode (int)
    layers_data: Sequence[Sequence[int]]
    physical_keys: Sequence[PhysicalKey] | None = None

    def keycode_at(self, layer: int, row: int, col: int) -> int:
        idx = row * self.matrix.cols + col
        return int(self.layers_data[layer][idx])


