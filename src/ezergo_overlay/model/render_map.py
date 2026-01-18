from __future__ import annotations

from dataclasses import dataclass

from ezergo_overlay.model.keycode_tables import BASIC, MASKED_MOD_OUTER, MOD_TAP_OUTER, SHIFTED
from ezergo_overlay.vial.vial_keycodes import vial_label_for_code


@dataclass(frozen=True, slots=True)
class KeyRender:
    text: str


def render_keycode_minimal(keycode: int) -> KeyRender:
    """
    MVP: keep rendering conservative and predictable.
    Later we can expand to full QMK/Vial keycode decoding.
    """
    kc = int(keycode)

    # Prefer Vial's own display labels when available (full coverage).
    vial_label = vial_label_for_code(kc)
    if vial_label is not None:
        return KeyRender(text=vial_label)

    # 1) Vial shifted keycodes (these are distinct codes like KC_EXLM=0x021E)
    sym = SHIFTED.get(kc)
    if sym is not None:
        return KeyRender(text=sym)

    # 2) Basic keycodes (0x00-0xFF) with Vial-friendly labels
    base = BASIC.get(kc)
    if base is not None:
        return KeyRender(text=base)

    # 3) MOD_TAP keycodes (0x2000-0x3FFF): LCTL_T(kc), LSFT_T(kc), etc.
    # Format: QK_MOD_TAP (0x2000) | (mod << 8) | kc
    if 0x2000 <= kc < 0x4000:
        outer = kc & 0xFF00
        inner = kc & 0x00FF
        mod_tap = MOD_TAP_OUTER.get(outer)
        if mod_tap is not None and inner:
            inner_txt = BASIC.get(inner) or SHIFTED.get(inner) or f"0x{inner:02X}"
            return KeyRender(text=f"{mod_tap}({inner_txt})")

    # 4) Common layer keycodes (protocol v6 style; matches vial-gui keycodes_v6.kc)
    # QK_TO=0x5200, QK_MOMENTARY=0x5220, QK_DEF_LAYER=0x5240, QK_TOGGLE_LAYER=0x5260
    # QK_ONE_SHOT_LAYER=0x5280, QK_LAYER_TAP_TOGGLE=0x52C0, QK_PERSISTENT_DEF_LAYER=0x52E0
    def _range(prefix: int, name: str) -> str | None:
        if prefix <= kc < prefix + 32:
            return f"{name}({kc - prefix})"
        return None

    for p, n in (
        (0x5200, "TO"),
        (0x5220, "MO"),
        (0x5240, "DF"),
        (0x5260, "TG"),
        (0x5280, "OSL"),
        (0x52C0, "TT"),
        (0x52E0, "PDF"),
    ):
        r = _range(p, n)
        if r is not None:
            return KeyRender(text=r)

    # 5) Masked modifiers (LCTL(kc), LSFT(kc), etc) – display compactly like Vial.
    outer = kc & 0xFF00
    inner = kc & 0x00FF
    mod = MASKED_MOD_OUTER.get(outer)
    if mod is not None and inner:
        inner_txt = BASIC.get(inner) or SHIFTED.get(inner) or f"0x{inner:02X}"
        return KeyRender(text=f"{mod}({inner_txt})")

    # 6) Fallback
    return KeyRender(text=f"0x{kc:04X}")


