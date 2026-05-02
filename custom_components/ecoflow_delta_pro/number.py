"""Number entities for EcoFlow Delta Pro — adjustable settings."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfPower,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import EcoflowCoordinator
from .protocol import packet


@dataclass(frozen=True, kw_only=True)
class EcoflowNumberDescription(NumberEntityDescription):
    data_key: str = ""
    command_fn: Callable[[int | float], bytes] = lambda v: b""


NUMBERS: tuple[EcoflowNumberDescription, ...] = (
    EcoflowNumberDescription(
        key="ac_charging_power",
        data_key="ac_in_limit_custom",
        name="AC Charging Power",
        native_min_value=200,
        native_max_value=3000,
        native_step=100,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=NumberDeviceClass.POWER,
        mode=NumberMode.SLIDER,
        icon="mdi:lightning-bolt",
        command_fn=lambda v: packet.set_ac_in_limit(watts=int(v)),
    ),
    EcoflowNumberDescription(
        key="max_charge_level",
        data_key="battery_level_max",
        name="Max Charge Level",
        native_min_value=30,
        native_max_value=100,
        native_step=5,
        native_unit_of_measurement=PERCENTAGE,
        mode=NumberMode.SLIDER,
        icon="mdi:battery-arrow-up",
        command_fn=lambda v: packet.set_level_max(int(v)),
    ),
    EcoflowNumberDescription(
        key="min_discharge_level",
        data_key="battery_level_min",
        name="Min Discharge Level",
        native_min_value=0,
        native_max_value=30,
        native_step=5,
        native_unit_of_measurement=PERCENTAGE,
        mode=NumberMode.SLIDER,
        icon="mdi:battery-arrow-down",
        command_fn=lambda v: packet.set_level_min(int(v)),
    ),
    EcoflowNumberDescription(
        key="generator_start_level",
        data_key="generator_level_start",
        name="Generator Auto-Start Level",
        native_min_value=0,
        native_max_value=30,
        native_step=1,
        native_unit_of_measurement=PERCENTAGE,
        mode=NumberMode.BOX,
        icon="mdi:engine",
        command_fn=lambda v: packet.set_generate_start(int(v)),
    ),
    EcoflowNumberDescription(
        key="generator_stop_level",
        data_key="generator_level_stop",
        name="Generator Auto-Stop Level",
        native_min_value=50,
        native_max_value=100,
        native_step=1,
        native_unit_of_measurement=PERCENTAGE,
        mode=NumberMode.BOX,
        icon="mdi:engine-off",
        command_fn=lambda v: packet.set_generate_stop(int(v)),
    ),
    EcoflowNumberDescription(
        key="standby_timeout",
        data_key="standby_timeout",
        name="Standby Timeout",
        native_min_value=0,
        native_max_value=5999,
        native_step=1,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        device_class=NumberDeviceClass.DURATION,
        mode=NumberMode.BOX,
        icon="mdi:timer-outline",
        command_fn=lambda v: packet.set_standby_timeout(int(v)),
    ),
    EcoflowNumberDescription(
        key="ac_out_timeout",
        data_key="ac_out_timeout",
        name="AC Output Auto-Off Timeout",
        native_min_value=0,
        native_max_value=5999,
        native_step=1,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        device_class=NumberDeviceClass.DURATION,
        mode=NumberMode.BOX,
        icon="mdi:timer-off-outline",
        command_fn=lambda v: packet.set_ac_timeout(int(v)),
    ),
    EcoflowNumberDescription(
        key="dc_in_current",
        data_key="dc_in_current",
        name="DC Input Charging Current",
        native_min_value=4,
        native_max_value=8,
        native_step=0.1,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=NumberDeviceClass.CURRENT,
        mode=NumberMode.SLIDER,
        icon="mdi:current-dc",
        # set_dc_in_current takes milliamps
        command_fn=lambda v: packet.set_dc_in_current(int(v * 1000)),
    ),
    EcoflowNumberDescription(
        key="lcd_brightness",
        data_key="lcd_brightness",
        name="LCD Brightness",
        native_min_value=0,
        native_max_value=100,
        native_step=1,
        native_unit_of_measurement=PERCENTAGE,
        mode=NumberMode.SLIDER,
        icon="mdi:brightness-6",
        command_fn=lambda v: packet.set_lcd_brightness(int(v)),
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
        EcoflowNumber(coordinator, entry, desc) for desc in NUMBERS
    )


class EcoflowNumber(CoordinatorEntity[EcoflowCoordinator], NumberEntity):
    """A number entity that reads a value and sends the updated value to the device."""

    entity_description: EcoflowNumberDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EcoflowCoordinator,
        entry: ConfigEntry,
        description: EcoflowNumberDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = _device_info(entry)

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data is None:
            return None
        val = self.coordinator.data.get(self.entity_description.data_key)
        return float(val) if val is not None else None

    async def async_set_native_value(self, value: float) -> None:
        cmd = self.entity_description.command_fn(value)
        await self.coordinator.async_send_command(cmd)
