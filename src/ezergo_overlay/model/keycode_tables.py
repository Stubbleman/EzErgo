from __future__ import annotations

# Minimal, Vial-aligned keycode label tables.
# Source reference: third_party/vial-gui/src/main/python/keycodes/keycodes.py + keycodes_v6.py

# Basic (0x00-0xFF) display labels (single-line, overlay-friendly).
BASIC: dict[int, str] = {
    0x00: "",
    0x01: "▽",  # KC_TRNS
    0x28: "Enter",
    0x29: "Esc",
    0x2A: "Bksp",
    0x2B: "Tab",
    0x2C: "Space",
    0x39: "Caps",
    0x46: "PrtSc",
    0x47: "ScrLk",
    0x48: "Pause",
    0x49: "Ins",
    0x4A: "Home",
    0x4B: "PgUp",
    0x4C: "Del",
    0x4D: "End",
    0x4E: "PgDn",
    0x4F: "→",
    0x50: "←",
    0x51: "↓",
    0x52: "↑",
    0x53: "Num",
    0x54: "/",
    0x55: "*",
    0x56: "-",
    0x57: "+",
    0x58: "Ent",
    0x65: "Menu",
    0xE0: "LCtrl",
    0xE1: "LShift",
    0xE2: "LAlt",
    0xE3: "LGui",
    0xE4: "RCtrl",
    0xE5: "RShift",
    0xE6: "RAlt",
    0xE7: "RGui",
}

# Letters
BASIC.update({0x04 + i: chr(ord("A") + i) for i in range(26)})

# Number row (unshifted)
BASIC.update(
    {
        0x1E: "1",
        0x1F: "2",
        0x20: "3",
        0x21: "4",
        0x22: "5",
        0x23: "6",
        0x24: "7",
        0x25: "8",
        0x26: "9",
        0x27: "0",
    }
)

# Common punctuation (unshifted)
BASIC.update(
    {
        0x2D: "-",
        0x2E: "=",
        0x2F: "[",
        0x30: "]",
        0x31: "\\",
        0x33: ";",
        0x34: "'",
        0x35: "`",
        0x36: ",",
        0x37: ".",
        0x38: "/",
    }
)

# Vial shifted keycodes (e.g. KC_EXLM == 0x021E). These are distinct codes, not "Shift+KC_*" masks.
SHIFTED: dict[int, str] = {
    0x021E: "!",  # KC_EXLM
    0x021F: "@",  # KC_AT
    0x0220: "#",  # KC_HASH
    0x0221: "$",  # KC_DLR
    0x0222: "%",  # KC_PERC
    0x0223: "^",  # KC_CIRC
    0x0224: "&",  # KC_AMPR
    0x0225: "*",  # KC_ASTR
    0x0226: "(",  # KC_LPRN
    0x0227: ")",  # KC_RPRN
    0x022D: "_",  # KC_UNDS
    0x022E: "+",  # KC_PLUS
    0x022F: "{",  # KC_LCBR
    0x0230: "}",  # KC_RCBR
    0x0231: "|",  # KC_PIPE
    0x0233: ":",  # KC_COLN
    0x0234: '"',  # KC_DQUO
    0x0235: "~",  # KC_TILD
    0x0236: "<",  # KC_LT
    0x0237: ">",  # KC_GT
    0x0238: "?",  # KC_QUES
}

# Masked modifiers used by VIA/Vial for LCTL(kc)/LSFT(kc)/... (from keycodes_v6.kc).
MASKED_MOD_OUTER: dict[int, str] = {
    0x0100: "C",  # LCTL(kc)
    0x0200: "S",  # LSFT(kc)
    0x0400: "A",  # LALT(kc)
    0x0800: "G",  # LGUI(kc)
    0x0300: "CS",  # C_S(kc)
    0x0500: "CA",  # LCA(kc)
    0x0900: "CG",  # LCG(kc)
    0x0600: "SA",  # LSA(kc)
    0x0C00: "AG",  # LAG(kc)
    0x0A00: "SG",  # SGUI(kc)
    0x0D00: "CAG",  # LCAG(kc)
    0x0700: "Meh",  # MEH(kc)
    0x0F00: "Hyp",  # HYPR(kc)
    # Right-side modifiers
    0x1100: "RC",  # RCTL(kc)
    0x1200: "RS",  # RSFT(kc)
    0x1400: "RA",  # RALT(kc)
    0x1800: "RG",  # RGUI(kc)
    0x1300: "RCS",  # RCTL + RSFT
    0x1500: "RCA",  # RCTL + RALT
    0x1900: "RCG",  # RCTL + RGUI
    0x1600: "RSA",  # RSFT + RALT
    0x1C00: "RAG",  # RALT + RGUI
    0x1A00: "RSG",  # RSFT + RGUI
    0x1D00: "RCAG",  # RCTL + RALT + RGUI
    0x1700: "RMeh",  # RCTL + RSFT + RALT
    0x1F00: "RHyp",  # RCTL + RSFT + RALT + RGUI
}


# MOD_TAP keycodes (0x2000-0x3FFF): QK_MOD_TAP | (mod << 8) | kc
# These are tap-hold keys like LCTL_T(kc), LSFT_T(kc), etc.
MOD_TAP_OUTER: dict[int, str] = {
    0x2100: "C_T",  # LCTL_T(kc)
    0x2200: "S_T",  # LSFT_T(kc)
    0x2400: "A_T",  # LALT_T(kc)
    0x2800: "G_T",  # LGUI_T(kc)
    0x2300: "CS_T",  # C_S_T(kc)
    0x2500: "CA_T",  # LCA_T(kc)
    0x2900: "CG_T",  # LCG_T(kc)
    0x2600: "SA_T",  # LSA_T(kc)
    0x2C00: "AG_T",  # LAG_T(kc)
    0x2A00: "SG_T",  # SGUI_T(kc)
    0x2D00: "CAG_T",  # LCAG_T(kc)
    0x2700: "Meh_T",  # MEH_T(kc)
    0x2F00: "All_T",  # ALL_T(kc) / HYPR_T(kc)
    0x3100: "RC_T",  # RCTL_T(kc)
    0x3200: "RS_T",  # RSFT_T(kc)
    0x3400: "RA_T",  # RALT_T(kc)
    0x3800: "RG_T",  # RGUI_T(kc)
    0x3900: "RCG_T",  # RCG_T(kc)
    0x3D00: "RCAG_T",  # RCAG_T(kc)
}
