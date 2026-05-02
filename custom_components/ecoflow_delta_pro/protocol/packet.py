"""EcoFlow Delta Pro binary packet building and parsing."""
from __future__ import annotations

import struct
from typing import Optional

from .crc import calc_crc8, calc_crc16

MAGIC = bytes([0xAA, 0x02])
# Fixed header bytes at positions 5-12 in outbound command packets
_FIXED_HDR = bytes([0x0D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x20])

# Minimum packet size: 2 magic + 2 len + 1 crc8 + 8 fixed + 3 routing + 2 crc16 = 18
_MIN_PACKET = 18

PRODUCT_DELTA_PRO = 14

# Response type keys: (src_component, cmd_set, cmd_id)
KEY_PD = (2, 32, 2)
KEY_EMS = (3, 32, 2)
KEY_INV = (4, 32, 2)
KEY_MPPT = (5, 32, 2)
KEY_BMS_MAIN = (3, 32, 50)
KEY_BMS_EXTRA = (6, 32, 2)
KEY_BMS_EXTRA2 = (6, 32, 50)


def build_packet(dst: int, cmd_set: int, cmd_id: int, data: bytes = b"") -> bytes:
    size = len(data)
    header = MAGIC + struct.pack("<H", size)
    crc8 = calc_crc8(header)
    body = header + crc8 + _FIXED_HDR + bytes([dst, cmd_set, cmd_id]) + data
    crc16 = calc_crc16(body)
    return body + crc16


# ── Query commands ──────────────────────────────────────────────────────────

def get_product_info(dst: int = PRODUCT_DELTA_PRO) -> bytes:
    return build_packet(dst, 1, 5)

def get_pd() -> bytes:
    return build_packet(2, 32, 2, b"\x00")

def get_ems() -> bytes:
    return build_packet(3, 32, 2)

def get_inverter() -> bytes:
    return build_packet(4, 32, 2)

def get_mppt() -> bytes:
    return build_packet(5, 32, 2)

def get_bms_main() -> bytes:
    return build_packet(3, 32, 50)

def get_bms_extra() -> bytes:
    return build_packet(6, 32, 2)

def get_all_queries() -> list[bytes]:
    return [get_product_info(), get_pd(), get_ems(), get_inverter(), get_mppt(),
            get_bms_main(), get_bms_extra()]


# ── Control commands ────────────────────────────────────────────────────────

def _btoi(value: Optional[bool]) -> int:
    if value is None:
        return 255
    return 1 if value else 0


def set_ac_out(enable: Optional[bool] = None, xboost: Optional[bool] = None,
               freq: int = 255) -> bytes:
    data = bytes([_btoi(enable), _btoi(xboost), 255, 255, 255, 255, freq])
    return build_packet(4, 32, 66, data)


def set_dc_out(enable: bool) -> bytes:
    return build_packet(5, 32, 81, bytes([1 if enable else 0]))


def set_ac_in_limit(watts: int = 0xFFFF, pause: Optional[bool] = None) -> bytes:
    data = bytes([255, 255]) + struct.pack("<H", watts) + bytes([_btoi(pause)])
    return build_packet(4, 32, 69, data)


def set_ac_slow_charge(enable: bool) -> bytes:
    return build_packet(4, 32, 65, bytes([_btoi(enable)]))


def set_beep(enable: bool) -> bytes:
    # inverted: 0 = beep on, 1 = beep off
    return build_packet(2, 32, 38, bytes([0 if enable else 1]))


def set_usb(enable: bool) -> bytes:
    return build_packet(2, 32, 34, bytes([1 if enable else 0]))


def set_lcd_brightness(brightness: int, timeout: int = 0xFFFF) -> bytes:
    data = struct.pack("<H", timeout) + bytes([brightness])
    return build_packet(2, 32, 39, data)


def set_standby_timeout(minutes: int) -> bytes:
    return build_packet(2, 32, 33, struct.pack("<H", minutes))


def set_ac_timeout(minutes: int) -> bytes:
    return build_packet(4, 32, 153, struct.pack("<H", minutes))


def set_level_max(value: int) -> bytes:
    return build_packet(3, 32, 49, bytes([value]))


def set_level_min(value: int) -> bytes:
    return build_packet(3, 32, 51, bytes([value]))


def set_generate_start(value: int) -> bytes:
    return build_packet(3, 32, 52, bytes([value]))


def set_generate_stop(value: int) -> bytes:
    return build_packet(3, 32, 53, bytes([value]))


def set_dc_in_type(value: int) -> bytes:
    return build_packet(5, 32, 82, bytes([value]))


def set_dc_in_current(milliamps: int) -> bytes:
    return build_packet(5, 32, 71, struct.pack("<I", milliamps))


def set_fan_auto(enable: bool) -> bytes:
    return build_packet(4, 32, 73, bytes([1 if enable else 3]))


# ── Packet extraction from stream ───────────────────────────────────────────

def extract_packets(buffer: bytes) -> tuple[list[bytes], bytes]:
    """Extract zero or more complete validated packets from a byte buffer.

    Returns (packets, remaining_buffer).
    """
    packets = []
    while True:
        idx = buffer.find(MAGIC)
        if idx == -1:
            # Preserve the last byte in case it is the start of an incomplete magic header
            buffer = buffer[-1:] if buffer else b""
            break
        if idx > 0:
            buffer = buffer[idx:]

        if len(buffer) < _MIN_PACKET:
            break

        size = struct.unpack_from("<H", buffer, 2)[0]
        total = 18 + size  # 16-byte header + size bytes data + 2 CRC16

        if len(buffer) < total:
            break

        packet = buffer[:total]

        # Validate CRC8 over bytes 0-3
        expected_crc8 = calc_crc8(packet[:4])
        if packet[4:5] != expected_crc8:
            buffer = buffer[2:]  # skip magic and retry
            continue

        # Validate CRC16 over bytes 0..total-3
        expected_crc16 = calc_crc16(packet[: total - 2])
        if packet[total - 2:total] != expected_crc16:
            buffer = buffer[2:]
            continue

        packets.append(packet)
        buffer = buffer[total:]

    return packets, buffer


def decode_packet(packet: bytes) -> tuple[int, int, int, bytes]:
    """Decode a validated packet into (src, cmd_set, cmd_id, payload).

    src corresponds to the originating device component:
      2=PD, 3=EMS/BMS_main, 4=INV, 5=MPPT, 6=BMS_extra
    """
    size = struct.unpack_from("<H", packet, 2)[0]
    src = packet[12]
    cmd_set = packet[14]
    cmd_id = packet[15]
    payload = bytearray(packet[16: 16 + size])

    # XOR deobfuscation when bits 5-6 of byte 5 == 1
    if (packet[5] >> 5) & 0x03 == 1:
        key = packet[19: 19 + 16] if len(packet) > 35 else b""
        if key:
            for i in range(len(payload)):
                payload[i] ^= key[i % len(key)]

    return src, cmd_set, cmd_id, bytes(payload)
