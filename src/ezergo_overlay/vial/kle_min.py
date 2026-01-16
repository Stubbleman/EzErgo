from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class KleKey:
    x: float
    y: float
    w: float
    h: float
    labels: list[str]


_LABEL_MAP: list[list[int]] = [
    # 0  1  2  3  4  5  6  7  8  9 10 11   # align flags
    [0, 6, 2, 8, 9, 11, 3, 5, 1, 4, 7, 10],  # 0 = no centering
    [1, 7, -1, -1, 9, 11, 4, -1, -1, -1, -1, 10],  # 1 = center x
    [3, -1, 5, -1, 9, 11, -1, -1, 4, -1, -1, 10],  # 2 = center y
    [4, -1, -1, -1, 9, 11, -1, -1, -1, -1, -1, 10],  # 3 = center x & y
    [0, 6, 2, 8, 10, -1, 3, 5, 1, 4, 7, -1],  # 4 = center front (default)
    [1, 7, -1, -1, 10, -1, 4, -1, -1, -1, -1, -1],  # 5 = center front & x
    [3, -1, 5, -1, 10, -1, -1, -1, 4, -1, -1, -1],  # 6 = center front & y
    [4, -1, -1, -1, 10, -1, -1, -1, -1, -1, -1, -1],  # 7 = center front & x & y
]


def _reorder_labels_in(labels: list[str], align: int) -> list[str]:
    align = int(align)
    if align < 0 or align >= len(_LABEL_MAP):
        align = 4
    ret = [""] * 12
    m = _LABEL_MAP[align]
    for i, lbl in enumerate(labels[:12]):
        if not lbl:
            continue
        dst = m[i]
        if dst >= 0:
            ret[dst] = lbl
    return ret


def deserialize_kle(rows: list[Any]) -> list[KleKey]:
    """
    Minimal KLE deserializer for the subset used by Vial definitions.

    It supports:
    - rows: list[list[str|dict]]
    - dict attributes: x, y, w, h
    - string item: labels separated by '\\n'

    It intentionally ignores rotation, secondary parts (x2/y2/w2/h2), and metadata.
    """
    keys: list[KleKey] = []
    x = 0.0
    y = 0.0
    w = 1.0
    h = 1.0
    align = 4
    cluster_x = 0.0
    cluster_y = 0.0

    for row in rows:
        if not isinstance(row, list):
            continue
        # Row starts at current cluster origin (like vial-gui's current.rotation_x)
        x = cluster_x
        w = 1.0
        h = 1.0
        for item in row:
            if isinstance(item, dict):
                if "a" in item:
                    align = int(item["a"])
                # KLE cluster origin: used heavily by split/ergo thumb clusters.
                # We ignore rotation angle but we must honor the origin to place keys correctly.
                if "rx" in item:
                    cluster_x = float(item["rx"])
                    x = cluster_x
                    y = cluster_y
                if "ry" in item:
                    cluster_y = float(item["ry"])
                    x = cluster_x
                    y = cluster_y
                if "x" in item:
                    x += float(item["x"])
                if "y" in item:
                    y += float(item["y"])
                if "w" in item:
                    w = float(item["w"])
                if "h" in item:
                    h = float(item["h"])
                continue
            if isinstance(item, str):
                raw_labels = item.split("\n") if item else [""]
                labels = _reorder_labels_in(raw_labels, align)
                keys.append(KleKey(x=x, y=y, w=w, h=h, labels=labels))
                x += w
                w = 1.0
                h = 1.0
        y += 1.0

    return keys


