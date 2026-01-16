from __future__ import annotations

# Constants aligned to vial-gui / VIA/Vial rawhid conventions.

MSG_LEN = 32

RAW_HID_USAGE_PAGE = 0xFF60
RAW_HID_USAGE = 0x61

VIAL_SERIAL_NUMBER_MAGIC = "vial:f64c2b3c"

# VIA protocol commands
CMD_VIA_GET_PROTOCOL_VERSION = 0x01
CMD_VIA_GET_LAYER_COUNT = 0x11
CMD_VIA_KEYMAP_GET_BUFFER = 0x12

CMD_VIA_GET_KEYBOARD_VALUE = 0x02
VIA_SWITCH_MATRIX_STATE = 0x03  # used by matrix tester (not for layer)

# Vial prefix commands
CMD_VIA_VIAL_PREFIX = 0xFE
CMD_VIAL_GET_KEYBOARD_ID = 0x00
CMD_VIAL_GET_SIZE = 0x01
CMD_VIAL_GET_DEFINITION = 0x02

# how much of a macro/keymap buffer we can read/write per packet
BUFFER_FETCH_CHUNK = 28


