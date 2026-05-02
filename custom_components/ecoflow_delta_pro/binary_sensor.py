"""Binary sensor entities for EcoFlow Delta Pro."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import EcoflowCoordinator


@dataclass(frozen=True, kw_only=True)
class EcoflowBinarySensorDescription(BinarySensorEntityDescription):
    is_on_fn: Callable[[dict], bool | None] = lambda _: None


BINARY_SENSORS: tuple[EcoflowBinarySensorDescription, ...] = (
    EcoflowBinarySensorDescription(
        key="ac_input_connected",
        name="AC Input Connected",
        device_class=BinarySensorDeviceClass.PLUG,
        is_on_fn=lambda d: d.get("ac_in_type", 0) != 0,
    ),
    EcoflowBinarySensorDescription(
        key="ac_output_on",
        name="AC Output On",
        device_class=BinarySensorDeviceClass.POWER,
        is_on_fn=lambda d: d.get("ac_out_state", 0) == 1,
    ),
    EcoflowBinarySensorDescription(
        key="dc_output_on",
        name="DC Output On",
        device_class=BinarySensorDeviceClass.POWER,
        is_on_fn=lambda d: d.get("dc24_state", 0) == 1,
    ),
    EcoflowBinarySensorDescription(
        key="car_output_on",
        name="12V Car Output On",
        device_class=BinarySensorDeviceClass.POWER,
        is_on_fn=lambda d: d.get("car_out_state", 0) == 1,
    ),
    EcoflowBinarySensorDescription(
        key="battery_charging",
        name="Battery Charging",
        device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
        is_on_fn=lambda d: (d.get("battery_in_power") or 0) > 0,
    ),
    EcoflowBinarySensorDescription(
        key="solar_charging",
        name="Solar Charging",
        device_class=BinarySensorDeviceClass.POWER,
        is_on_fn=lambda d: (d.get("dc_in_power") or 0) > 0,
        icon="mdi:solar-power",
    ),
    EcoflowBinarySensorDescription(
        key="xboost_on",
        name="X-Boost Active",
        device_class=BinarySensorDeviceClass.POWER,
        is_on_fn=lambda d: d.get("ac_out_xboost", 0) == 1,
        icon="mdi:lightning-bolt",
    ),
    EcoflowBinarySensorDescription(
        key="ac_slow_charge",
        name="AC Slow Charging",
        device_class=BinarySensorDeviceClass.POWER,
        is_on_fn=lambda d: d.get("ac_in_pause", 0) == 1,
        icon="mdi:battery-charging-low",
    ),
    EcoflowBinarySensorDescription(
        key="battery_error",
        name="Battery Fault",
        device_class=BinarySensorDeviceClass.PROBLEM,
        is_on_fn=lambda d: (d.get("battery_fault") or 0) != 0,
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
        EcoflowBinarySensor(coordinator, entry, desc) for desc in BINARY_SENSORS
    )


class EcoflowBinarySensor(CoordinatorEntity[EcoflowCoordinator], BinarySensorEntity):
    """A binary sensor derived from EcoFlow device data."""

    entity_description: EcoflowBinarySensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EcoflowCoordinator,
        entry: ConfigEntry,
        description: EcoflowBinarySensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = _device_info(entry)

    @property
    def is_on(self) -> bool | None:
        if self.coordinator.data is None:
            return None
        return self.entity_description.is_on_fn(self.coordinator.data)
