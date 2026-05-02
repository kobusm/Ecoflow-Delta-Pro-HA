"""Switch entities for EcoFlow Delta Pro."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import EcoflowCoordinator
from .protocol import packet


@dataclass(frozen=True, kw_only=True)
class EcoflowSwitchDescription(SwitchEntityDescription):
    is_on_fn: Callable[[dict], bool | None] = lambda _: None
    turn_on_packet: Callable[[], bytes] = lambda: b""
    turn_off_packet: Callable[[], bytes] = lambda: b""


SWITCHES: tuple[EcoflowSwitchDescription, ...] = (
    EcoflowSwitchDescription(
        key="ac_output",
        name="AC Output",
        device_class=SwitchDeviceClass.OUTLET,
        icon="mdi:power-socket",
        is_on_fn=lambda d: d.get("ac_out_state", 0) == 1,
        turn_on_packet=lambda: packet.set_ac_out(enable=True),
        turn_off_packet=lambda: packet.set_ac_out(enable=False),
    ),
    EcoflowSwitchDescription(
        key="dc_output",
        name="DC Output",
        device_class=SwitchDeviceClass.OUTLET,
        icon="mdi:car-battery",
        is_on_fn=lambda d: d.get("dc24_state", 0) == 1,
        turn_on_packet=lambda: packet.set_dc_out(True),
        turn_off_packet=lambda: packet.set_dc_out(False),
    ),
    EcoflowSwitchDescription(
        key="xboost",
        name="X-Boost",
        device_class=SwitchDeviceClass.SWITCH,
        icon="mdi:lightning-bolt",
        is_on_fn=lambda d: d.get("ac_out_xboost", 0) == 1,
        turn_on_packet=lambda: packet.set_ac_out(xboost=True),
        turn_off_packet=lambda: packet.set_ac_out(xboost=False),
    ),
    EcoflowSwitchDescription(
        key="ac_slow_charge",
        name="AC Slow Charging",
        device_class=SwitchDeviceClass.SWITCH,
        icon="mdi:battery-charging-low",
        is_on_fn=lambda d: d.get("ac_in_pause", 0) == 1,
        turn_on_packet=lambda: packet.set_ac_slow_charge(True),
        turn_off_packet=lambda: packet.set_ac_slow_charge(False),
    ),
    EcoflowSwitchDescription(
        key="usb_output",
        name="USB Output",
        device_class=SwitchDeviceClass.OUTLET,
        icon="mdi:usb",
        is_on_fn=lambda d: (d.get("usb_out1_power", 0) is not None),
        turn_on_packet=lambda: packet.set_usb(True),
        turn_off_packet=lambda: packet.set_usb(False),
    ),
    EcoflowSwitchDescription(
        key="beep",
        name="Beep Sound",
        device_class=SwitchDeviceClass.SWITCH,
        icon="mdi:volume-high",
        # beep_mode=0 means beep on (inverted in hardware)
        is_on_fn=lambda d: d.get("beep_mode", 1) == 0,
        turn_on_packet=lambda: packet.set_beep(True),
        turn_off_packet=lambda: packet.set_beep(False),
    ),
    EcoflowSwitchDescription(
        key="fan_auto",
        name="Fan Auto Speed",
        device_class=SwitchDeviceClass.SWITCH,
        icon="mdi:fan-auto",
        is_on_fn=lambda d: d.get("fan_auto_cfg", 0) == 1,
        turn_on_packet=lambda: packet.set_fan_auto(True),
        turn_off_packet=lambda: packet.set_fan_auto(False),
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
        EcoflowSwitch(coordinator, entry, desc) for desc in SWITCHES
    )


class EcoflowSwitch(CoordinatorEntity[EcoflowCoordinator], SwitchEntity):
    """A switch that sends binary commands to the EcoFlow device."""

    entity_description: EcoflowSwitchDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EcoflowCoordinator,
        entry: ConfigEntry,
        description: EcoflowSwitchDescription,
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

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_send_command(
            self.entity_description.turn_on_packet()
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_send_command(
            self.entity_description.turn_off_packet()
        )
