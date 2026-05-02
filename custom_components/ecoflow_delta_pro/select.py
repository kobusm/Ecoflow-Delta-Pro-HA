"""Select entities for EcoFlow Delta Pro — mode and type selection."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import EcoflowCoordinator
from .protocol import packet


@dataclass(frozen=True, kw_only=True)
class EcoflowSelectDescription(SelectEntityDescription):
    data_key: str = ""
    options_map: dict[int, str] = None  # int value → display label
    command_fn: Callable[[int], bytes] = lambda v: b""


def _reverse(options_map: dict[int, str]) -> dict[str, int]:
    return {label: val for val, label in options_map.items()}


_DC_IN_TYPES = {
    0: "Auto",
    1: "MPPT (Solar)",
    2: "Adapter",
    3: "DC",
    4: "JD-Adapter",
    5: "Non-Standard",
}

_AC_OUT_FREQ = {
    50: "50 Hz",
    60: "60 Hz",
}

SELECTS: tuple[EcoflowSelectDescription, ...] = (
    EcoflowSelectDescription(
        key="dc_in_type",
        data_key="dc_in_type_cfg",
        name="DC Input Mode",
        options=list(_DC_IN_TYPES.values()),
        options_map=_DC_IN_TYPES,
        icon="mdi:solar-power-variant",
        command_fn=lambda v: packet.set_dc_in_type(v),
    ),
    EcoflowSelectDescription(
        key="ac_out_freq",
        data_key="ac_out_freq_cfg",
        name="AC Output Frequency",
        options=list(_AC_OUT_FREQ.values()),
        options_map=_AC_OUT_FREQ,
        icon="mdi:sine-wave",
        command_fn=lambda v: packet.set_ac_out(freq=v),
    ),
)


def _device_info(entry: ConfigEntry) -> DeviceInfo:
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name="EcoFlow Delta Pro",
        manufacturer="EcoFlow",
        model="Delta Pro",
    )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: EcoflowCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        EcoflowSelect(coordinator, entry, desc) for desc in SELECTS
    )


class EcoflowSelect(CoordinatorEntity[EcoflowCoordinator], SelectEntity):
    """A select entity that maps integer device values to human-readable options."""

    entity_description: EcoflowSelectDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EcoflowCoordinator,
        entry: ConfigEntry,
        description: EcoflowSelectDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = _device_info(entry)
        self._attr_options = description.options
        self._label_to_value = _reverse(description.options_map)

    @property
    def current_option(self) -> str | None:
        if self.coordinator.data is None:
            return None
        raw = self.coordinator.data.get(self.entity_description.data_key)
        if raw is None:
            return None
        return self.entity_description.options_map.get(int(raw))

    async def async_select_option(self, option: str) -> None:
        value = self._label_to_value.get(option)
        if value is None:
            return
        cmd = self.entity_description.command_fn(value)
        await self.coordinator.async_send_command(cmd)
