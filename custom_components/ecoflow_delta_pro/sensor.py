"""Sensor entities for EcoFlow Delta Pro."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import EcoflowCoordinator


@dataclass(frozen=True, kw_only=True)
class EcoflowSensorDescription(SensorEntityDescription):
    data_key: str = ""


SENSORS: tuple[EcoflowSensorDescription, ...] = (
    # ── Battery (BMS) ───────────────────────────────────────────────────────
    EcoflowSensorDescription(
        key="battery_level",
        data_key="battery_level",
        name="Battery Level",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    EcoflowSensorDescription(
        key="battery_voltage",
        data_key="battery_voltage",
        name="Battery Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
    EcoflowSensorDescription(
        key="battery_current",
        data_key="battery_current",
        name="Battery Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    EcoflowSensorDescription(
        key="battery_temp",
        data_key="battery_temp",
        name="Battery Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    EcoflowSensorDescription(
        key="battery_cycles",
        data_key="battery_cycles",
        name="Battery Charge Cycles",
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:battery-sync",
    ),
    EcoflowSensorDescription(
        key="battery_capacity_remain",
        data_key="battery_capacity_remain",
        name="Battery Remaining Capacity",
        native_unit_of_measurement="mAh",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery",
    ),
    EcoflowSensorDescription(
        key="battery_capacity_full",
        data_key="battery_capacity_full",
        name="Battery Full Capacity",
        native_unit_of_measurement="mAh",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery-high",
    ),
    EcoflowSensorDescription(
        key="battery_in_power",
        data_key="battery_in_power",
        name="Battery Charging Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    EcoflowSensorDescription(
        key="battery_out_power",
        data_key="battery_out_power",
        name="Battery Discharging Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    EcoflowSensorDescription(
        key="battery_temp_max",
        data_key="battery_temp_max",
        name="Battery Max Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    EcoflowSensorDescription(
        key="battery_voltage_min",
        data_key="battery_voltage_min",
        name="Battery Min Cell Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        entity_registry_enabled_default=False,
    ),
    EcoflowSensorDescription(
        key="battery_voltage_max",
        data_key="battery_voltage_max",
        name="Battery Max Cell Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        entity_registry_enabled_default=False,
    ),

    # ── AC inverter ─────────────────────────────────────────────────────────
    EcoflowSensorDescription(
        key="ac_in_power",
        data_key="ac_in_power",
        name="AC Input Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    EcoflowSensorDescription(
        key="ac_out_power",
        data_key="ac_out_power",
        name="AC Output Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    EcoflowSensorDescription(
        key="ac_in_voltage",
        data_key="ac_in_voltage",
        name="AC Input Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    EcoflowSensorDescription(
        key="ac_out_voltage",
        data_key="ac_out_voltage",
        name="AC Output Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    EcoflowSensorDescription(
        key="ac_in_current",
        data_key="ac_in_current",
        name="AC Input Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
    EcoflowSensorDescription(
        key="ac_out_current",
        data_key="ac_out_current",
        name="AC Output Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
    EcoflowSensorDescription(
        key="ac_in_freq",
        data_key="ac_in_freq",
        name="AC Input Frequency",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    EcoflowSensorDescription(
        key="ac_out_freq",
        data_key="ac_out_freq",
        name="AC Output Frequency",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    EcoflowSensorDescription(
        key="ac_in_temp",
        data_key="ac_in_temp",
        name="AC Input Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    EcoflowSensorDescription(
        key="ac_out_temp",
        data_key="ac_out_temp",
        name="AC Output Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    EcoflowSensorDescription(
        key="ac_in_limit_max",
        data_key="ac_in_limit_max",
        name="AC Charging Limit",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    EcoflowSensorDescription(
        key="ac_out_timeout",
        data_key="ac_out_timeout",
        name="AC Output Standby Timeout",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        icon="mdi:timer-outline",
        entity_registry_enabled_default=False,
    ),

    # ── DC / Solar (MPPT) ───────────────────────────────────────────────────
    EcoflowSensorDescription(
        key="dc_in_voltage",
        data_key="dc_in_voltage",
        name="DC Input Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    EcoflowSensorDescription(
        key="dc_in_current",
        data_key="dc_in_current",
        name="DC Input Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
    EcoflowSensorDescription(
        key="dc_in_power",
        data_key="dc_in_power",
        name="DC Input Power (Solar/MPPT)",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    EcoflowSensorDescription(
        key="dc_in_temp",
        data_key="dc_in_temp",
        name="DC Input Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    EcoflowSensorDescription(
        key="anderson_out_power",
        data_key="anderson_out_power",
        name="Anderson Output Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:power-plug",
    ),
    EcoflowSensorDescription(
        key="car_out_power",
        data_key="car_out_power",
        name="12V Car Output Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:car-electric",
    ),
    EcoflowSensorDescription(
        key="car_out_temp",
        data_key="car_out_temp",
        name="12V Car Output Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    EcoflowSensorDescription(
        key="car_out_voltage",
        data_key="car_out_voltage",
        name="12V Car Output Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),

    # ── Power distribution (PD) ─────────────────────────────────────────────
    EcoflowSensorDescription(
        key="out_power",
        data_key="out_power",
        name="Total Output Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    EcoflowSensorDescription(
        key="in_power",
        data_key="in_power",
        name="Total Input Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    EcoflowSensorDescription(
        key="usb_out1_power",
        data_key="usb_out1_power",
        name="USB Output 1 Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:usb",
    ),
    EcoflowSensorDescription(
        key="usb_out2_power",
        data_key="usb_out2_power",
        name="USB Output 2 Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:usb",
    ),
    EcoflowSensorDescription(
        key="usbqc_out1_power",
        data_key="usbqc_out1_power",
        name="USB QC Output 1 Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:usb",
    ),
    EcoflowSensorDescription(
        key="usbqc_out2_power",
        data_key="usbqc_out2_power",
        name="USB QC Output 2 Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:usb",
    ),
    EcoflowSensorDescription(
        key="typec_out1_power",
        data_key="typec_out1_power",
        name="USB-C Output 1 Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:usb-c-port",
    ),
    EcoflowSensorDescription(
        key="typec_out2_power",
        data_key="typec_out2_power",
        name="USB-C Output 2 Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:usb-c-port",
    ),
    EcoflowSensorDescription(
        key="typec_out1_temp",
        data_key="typec_out1_temp",
        name="USB-C Output 1 Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    EcoflowSensorDescription(
        key="typec_out2_temp",
        data_key="typec_out2_temp",
        name="USB-C Output 2 Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    EcoflowSensorDescription(
        key="standby_timeout",
        data_key="standby_timeout",
        name="Standby Timeout",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        icon="mdi:timer-outline",
        entity_registry_enabled_default=False,
    ),
    EcoflowSensorDescription(
        key="lcd_brightness",
        data_key="lcd_brightness",
        name="LCD Brightness",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:brightness-6",
        entity_registry_enabled_default=False,
    ),

    # ── Energy totals (PD) ──────────────────────────────────────────────────
    EcoflowSensorDescription(
        key="ac_in_energy",
        data_key="ac_in_energy",
        name="AC Total Input Energy",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_registry_enabled_default=False,
    ),
    EcoflowSensorDescription(
        key="ac_out_energy",
        data_key="ac_out_energy",
        name="AC Total Output Energy",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_registry_enabled_default=False,
    ),
    EcoflowSensorDescription(
        key="mppt_in_energy",
        data_key="mppt_in_energy",
        name="Solar Total Input Energy",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_registry_enabled_default=False,
    ),
    EcoflowSensorDescription(
        key="car_in_energy",
        data_key="car_in_energy",
        name="12V Car Total Input Energy",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_registry_enabled_default=False,
    ),
    EcoflowSensorDescription(
        key="car_out_energy",
        data_key="car_out_energy",
        name="12V Car Total Output Energy",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_registry_enabled_default=False,
    ),

    # ── EMS ─────────────────────────────────────────────────────────────────
    EcoflowSensorDescription(
        key="battery_remain_charge_min",
        data_key="battery_remain_charge_min",
        name="Time to Full Charge",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        device_class=SensorDeviceClass.DURATION,
        icon="mdi:battery-charging",
    ),
    EcoflowSensorDescription(
        key="battery_remain_discharge_min",
        data_key="battery_remain_discharge_min",
        name="Time to Empty",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        device_class=SensorDeviceClass.DURATION,
        icon="mdi:battery-minus",
    ),
    EcoflowSensorDescription(
        key="battery_level_max",
        data_key="battery_level_max",
        name="Max Charge Level",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:battery-arrow-up",
        entity_registry_enabled_default=False,
    ),
    EcoflowSensorDescription(
        key="battery_level_min",
        data_key="battery_level_min",
        name="Min Discharge Level",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:battery-arrow-down",
        entity_registry_enabled_default=False,
    ),
    EcoflowSensorDescription(
        key="generator_level_start",
        data_key="generator_level_start",
        name="Generator Auto-Start Level",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:engine",
        entity_registry_enabled_default=False,
    ),
    EcoflowSensorDescription(
        key="generator_level_stop",
        data_key="generator_level_stop",
        name="Generator Auto-Stop Level",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:engine-off",
        entity_registry_enabled_default=False,
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
        EcoflowSensor(coordinator, entry, desc) for desc in SENSORS
    )


class EcoflowSensor(CoordinatorEntity[EcoflowCoordinator], SensorEntity):
    """A sensor reading a single field from EcoFlow device data."""

    entity_description: EcoflowSensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EcoflowCoordinator,
        entry: ConfigEntry,
        description: EcoflowSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = _device_info(entry)

    @property
    def native_value(self) -> Any:
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self.entity_description.data_key)
