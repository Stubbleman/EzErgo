from __future__ import annotations

import ast
from dataclasses import dataclass
from functools import lru_cache
from importlib.machinery import SourceFileLoader
from pathlib import Path
from types import ModuleType
from typing import Any


def _project_root() -> Path:
    # src/ezergo_overlay/vial/vial_keycodes.py -> repo root is 3 levels up
    return Path(__file__).resolve().parents[3]


def _vial_gui_py_root() -> Path:
    return _project_root() / "third_party" / "vial-gui" / "src" / "main" / "python"


def _load_module_from_path(name: str, path: Path) -> ModuleType:
    loader = SourceFileLoader(name, str(path))
    mod = ModuleType(name)
    loader.exec_module(mod)
    return mod


def _extract_qmk_id_to_label(keycodes_py: Path) -> dict[str, str]:
    """
    Parse vial-gui's keycodes.py and extract Keycode definitions without importing it.

    We look for calls like:
      K("KC_A", "A", ...)
      Keycode("KC_A", "A", ...)
    and capture the first two string args.
    """
    src = keycodes_py.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(src, filename=str(keycodes_py))
    out: dict[str, str] = {}

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Name):
            continue
        if node.func.id not in {"K", "Keycode"}:
            continue
        if len(node.args) < 2:
            continue
        a0, a1 = node.args[0], node.args[1]
        if not (isinstance(a0, ast.Constant) and isinstance(a1, ast.Constant)):
            continue
        if not (isinstance(a0.value, str) and isinstance(a1.value, str)):
            continue
        out[a0.value] = a1.value
    return out


def _compact(label: str) -> str:
    # Keep multi-line labels (Vial style) but remove excessive whitespace.
    label = label.replace("\r\n", "\n").replace("\r", "\n")
    lines = [ln.strip() for ln in label.split("\n")]
    lines = [ln for ln in lines if ln]
    if not lines:
        return ""
    return "\n".join(lines[:2])


@dataclass(frozen=True, slots=True)
class VialKeycodeLabeler:
    code_to_label: dict[int, str]

    def label_for_code(self, code: int) -> str | None:
        return self.code_to_label.get(int(code))


@lru_cache(maxsize=1)
def get_vial_labeler() -> VialKeycodeLabeler | None:
    """
    Build a numeric keycode -> label mapping using vial-gui sources (protocol v6 table).

    Returns None if the third_party folder is missing.
    """
    root = _vial_gui_py_root()
    keycodes_py = root / "keycodes" / "keycodes.py"
    keycodes_v6_py = root / "keycodes" / "keycodes_v6.py"
    if not keycodes_py.exists() or not keycodes_v6_py.exists():
        return None

    qmk_to_label = _extract_qmk_id_to_label(keycodes_py)

    mod = _load_module_from_path("_ezergo_vial_keycodes_v6", keycodes_v6_py)
    # keycodes_v6.py defines a class keycodes_v6 with a kc dict
    kc_cls = getattr(mod, "keycodes_v6", None)
    if kc_cls is None or not hasattr(kc_cls, "kc"):
        return None

    kc: dict[str, Any] = dict(getattr(kc_cls, "kc"))

    code_to_label: dict[int, str] = {}
    for qmk_id, val in kc.items():
        if not isinstance(val, int):
            continue
        label = qmk_to_label.get(qmk_id)
        if label is None:
            # Reasonable fallback when vial-gui doesn't define a label entry.
            if qmk_id.startswith("KC_"):
                label = qmk_id.replace("KC_", "")
            else:
                label = qmk_id
        code_to_label[int(val)] = _compact(label)

    return VialKeycodeLabeler(code_to_label=code_to_label)


def vial_label_for_code(code: int) -> str | None:
    lab = get_vial_labeler()
    if lab is None:
        return None
    return lab.label_for_code(code)

