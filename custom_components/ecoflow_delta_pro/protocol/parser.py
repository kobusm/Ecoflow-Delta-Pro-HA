"""Parse binary payloads from EcoFlow Delta Pro device responses into dicts."""
from __future__ import annotations

import struct
from typing import Any, Callable, Optional


def _int(data: bytes) -> int:
    return int.from_bytes(data, "little", signed=True)


def _uint(data: bytes) -> int:
    return int.from_bytes(data, "little", signed=False)


def _float(data: bytes) -> float:
    return struct.unpack_from("<f", data)[0]


def _div(divisor: int) -> Callable[[bytes], float]:
    def _convert(data: bytes) -> float:
        return int.from_bytes(data, "little", signed=True) / divisor
    return _convert


def _version(data: bytes) -> str:
    return ".".join(str(b) for b in reversed(data))


def _minutes(data: bytes) -> int:
    return int.from_bytes(data, "little")


def _seconds(data: bytes) -> int:
    return int.from_bytes(data, "little")


def _parse(payload: bytes, fields: list[tuple]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    offset = 0
    for name, size, converter in fields:
        if offset + size > len(payload):
            break
        if name is not None and converter is not None:
            result[name] = converter(payload[offset: offset + size])
        offset += size
    return result


# ── Field definitions ────────────────────────────────────────────────────────

_BMS_FIELDS = [
    ("bms_num", 1, _uint),
    ("bms_battery_type", 1, _uint),
    ("bms_cell_id", 1, _uint),
    ("bms_error", 4, _uint),
    ("bms_version", 4, _version),
    ("battery_level", 1, _uint),
    ("battery_voltage", 4, _div(1000)),
    ("battery_current", 4, _int),
    ("battery_temp", 1, _int),
    ("_open_bms_idx", 1, _uint),
    ("battery_capacity_design", 4, _uint),
    ("battery_capacity_remain", 4, _uint),
    ("battery_capacity_full", 4, _uint),
    ("battery_cycles", 4, _uint),
    ("_soh", 1, _uint),
    ("battery_voltage_max", 2, _div(1000)),
    ("battery_voltage_min", 2, _div(1000)),
    ("battery_temp_max", 1, _int),
    ("battery_temp_min", 1, _int),
    ("battery_mos_temp_max", 1, _int),
    ("battery_mos_temp_min", 1, _int),
    ("battery_fault", 1, _uint),
    ("_sys_stat_reg", 1, _uint),
    ("_tag_chg_current", 4, _uint),
    ("battery_level_f32", 4, _float),
    ("battery_in_power", 4, _uint),
    ("battery_out_power", 4, _uint),
    ("battery_remain_min", 4, _minutes),
]

_EMS_FIELDS = [
    ("_state_charge", 1, _uint),
    ("_chg_cmd", 1, _uint),
    ("_dsg_cmd", 1, _uint),
    ("ems_battery_voltage", 4, _div(1000)),
    ("ems_battery_current", 4, _div(1000)),
    ("_fan_level", 1, _uint),
    ("battery_level_max", 1, _uint),
    ("ems_model", 1, _uint),
    ("ems_battery_level", 1, _uint),
    ("_flag_open_ups", 1, _uint),
    ("ems_battery_warning", 1, _uint),
    ("battery_remain_charge_min", 4, _minutes),
    ("battery_remain_discharge_min", 4, _minutes),
    ("ems_battery_normal", 1, _uint),
    ("ems_battery_level_f32", 4, _float),
    ("_is_connect", 3, _uint),
    ("_max_available_num", 1, _uint),
    ("_open_bms_idx", 1, _uint),
    ("ems_voltage_min", 4, _div(1000)),
    ("ems_voltage_max", 4, _div(1000)),
    ("battery_level_min", 1, _uint),
    ("generator_level_start", 1, _uint),
    ("generator_level_stop", 1, _uint),
]

_INV_FIELDS = [
    ("inv_error", 4, _uint),
    ("inv_version", 4, _version),
    ("ac_in_type", 1, _uint),
    ("ac_in_power", 2, _uint),
    ("ac_out_power", 2, _uint),
    ("ac_type", 1, _uint),
    ("ac_out_voltage", 4, _div(1000)),
    ("ac_out_current", 4, _div(1000)),
    ("ac_out_freq", 1, _uint),
    ("ac_in_voltage", 4, _div(1000)),
    ("ac_in_current", 4, _div(1000)),
    ("ac_in_freq", 1, _uint),
    ("ac_out_temp", 2, _int),
    ("dc_in_voltage_inv", 4, _uint),
    ("dc_in_current_inv", 4, _uint),
    ("ac_in_temp", 2, _int),
    ("fan_state", 1, _uint),
    ("ac_out_state", 1, _uint),
    ("ac_out_xboost", 1, _uint),
    ("ac_out_voltage_cfg", 4, _div(1000)),
    ("ac_out_freq_cfg", 1, _uint),
    ("fan_auto_cfg", 1, _uint),
    ("ac_in_pause", 1, _uint),
    ("ac_in_limit_switch", 1, _uint),
    ("ac_in_limit_max", 2, _uint),
    ("ac_in_limit_custom", 2, _uint),
    ("ac_out_timeout", 2, _uint),
]

_MPPT_FIELDS = [
    ("mppt_error", 4, _uint),
    ("mppt_version", 4, _version),
    ("dc_in_voltage", 4, _div(10)),
    ("dc_in_current", 4, _div(100)),
    ("dc_in_power", 2, _div(10)),
    ("_volt_out", 4, _uint),
    ("_curr_out", 4, _uint),
    ("_watts_out", 2, _uint),
    ("dc_in_temp", 2, _int),
    ("dc_in_type", 1, _uint),
    ("dc_in_type_cfg", 1, _uint),
    ("_dc_in_type2", 1, _uint),
    ("dc_in_state", 1, _uint),
    ("anderson_out_voltage", 4, _uint),
    ("anderson_out_current", 4, _uint),
    ("anderson_out_power", 2, _uint),
    ("car_out_voltage", 4, _div(10)),
    ("car_out_current", 4, _div(100)),
    ("car_out_power", 2, _div(10)),
    ("car_out_temp", 2, _int),
    ("car_out_state", 1, _uint),
    ("dc24_temp", 2, _int),
    ("dc24_state", 1, _uint),
    ("dc_in_pause", 1, _uint),
    ("_dc_in_switch", 1, _uint),
    ("_dc_in_limit_max", 2, _uint),
    ("_dc_in_limit_custom", 2, _uint),
]

_PD_FIELDS = [
    ("pd_model", 1, _uint),
    ("pd_error", 4, _uint),
    ("pd_version", 4, _version),
    ("wifi_version", 4, _version),
    ("wifi_autorecovery", 1, _uint),
    ("pd_battery_level", 1, _uint),
    ("out_power", 2, _uint),
    ("in_power", 2, _uint),
    ("remain_display_min", 4, _minutes),
    ("beep_mode", 1, _uint),
    ("_watts_anderson_out", 1, _uint),
    ("usb_out1_power", 1, _uint),
    ("usb_out2_power", 1, _uint),
    ("usbqc_out1_power", 1, _uint),
    ("usbqc_out2_power", 1, _uint),
    ("typec_out1_power", 1, _uint),
    ("typec_out2_power", 1, _uint),
    ("typec_out1_temp", 1, _int),
    ("typec_out2_temp", 1, _int),
    ("pd_car_out_state", 1, _uint),
    ("pd_car_out_power", 1, _uint),
    ("pd_car_out_temp", 1, _int),
    ("standby_timeout", 2, _uint),
    ("lcd_timeout", 2, _uint),
    ("lcd_brightness", 1, _uint),
    ("car_in_energy", 4, _uint),
    ("mppt_in_energy", 4, _uint),
    ("ac_in_energy", 4, _uint),
    ("car_out_energy", 4, _uint),
    ("ac_out_energy", 4, _uint),
    ("usb_time_sec", 4, _seconds),
    ("typec_time_sec", 4, _seconds),
    ("car_out_time_sec", 4, _seconds),
    ("ac_out_time_sec", 4, _seconds),
    ("ac_in_time_sec", 4, _seconds),
    ("car_in_time_sec", 4, _seconds),
    ("mppt_time_sec", 4, _seconds),
    (None, 2, None),
    ("_ext_rj45", 1, _uint),
    ("_ext_infinity", 1, _uint),
]


def parse_bms(payload: bytes, prefix: str = "") -> dict[str, Any]:
    return {f"{prefix}{k}": v for k, v in _parse(payload, _BMS_FIELDS).items()}


def parse_ems(payload: bytes) -> dict[str, Any]:
    return _parse(payload, _EMS_FIELDS)


def parse_inv(payload: bytes) -> dict[str, Any]:
    return _parse(payload, _INV_FIELDS)


def parse_mppt(payload: bytes) -> dict[str, Any]:
    return _parse(payload, _MPPT_FIELDS)


def parse_pd(payload: bytes) -> dict[str, Any]:
    return _parse(payload, _PD_FIELDS)
