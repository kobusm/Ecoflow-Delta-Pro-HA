# EcoFlow Delta Pro — Home Assistant Integration

A Home Assistant custom integration for the **EcoFlow Delta Pro** portable power station using its **local TCP API** (port 8055). No cloud account or internet connection required after initial device setup.

## Requirements

- EcoFlow Delta Pro with firmware **3.0.2.21 or newer** (enables local port 8055)
- Home Assistant 2024.1 or newer
- Device and HA on the same local network

## Installation

### HACS (recommended)

1. Open HACS → Integrations → ⋮ → Custom repositories
2. Add `https://github.com/kobusm/ecoflow-delta-pro-ha` as an **Integration**
3. Install **EcoFlow Delta Pro**
4. Restart Home Assistant

### Manual

1. Copy `custom_components/ecoflow_delta_pro/` into your HA `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. **Settings → Integrations → Add Integration → EcoFlow Delta Pro**
2. Enter the device's local IP address (find it in your router's DHCP table or the EcoFlow app under Wi-Fi settings)
3. Leave the port as **8055** unless you've changed it

The integration connects immediately and begins receiving real-time data pushed by the device.

## Entities

### Sensors (38)

| Sensor | Unit | Source |
|--------|------|--------|
| Battery Level | % | BMS |
| Battery Voltage | V | BMS |
| Battery Current | A | BMS |
| Battery Temperature | °C | BMS |
| Battery Charge Cycles | — | BMS |
| Battery Remaining Capacity | mAh | BMS |
| Battery Full Capacity | mAh | BMS |
| Battery Charging Power | W | BMS |
| Battery Discharging Power | W | BMS |
| AC Input Power | W | Inverter |
| AC Output Power | W | Inverter |
| AC Input Voltage | V | Inverter |
| AC Output Voltage | V | Inverter |
| AC Input Current | A | Inverter |
| AC Output Current | A | Inverter |
| AC Input Frequency | Hz | Inverter |
| AC Output Frequency | Hz | Inverter |
| DC Input Power (Solar/MPPT) | W | MPPT |
| DC Input Voltage | V | MPPT |
| DC Input Current | A | MPPT |
| Anderson Output Power | W | MPPT |
| 12V Car Output Power | W | MPPT |
| Total Input Power | W | PD |
| Total Output Power | W | PD |
| USB Output 1/2 Power | W | PD |
| USB QC Output 1/2 Power | W | PD |
| USB-C Output 1/2 Power | W | PD |
| Time to Full Charge | min | EMS |
| Time to Empty | min | EMS |
| AC Total Input/Output Energy | Wh | PD |
| Solar Total Input Energy | Wh | PD |
| 12V Car Total Input/Output Energy | Wh | PD |

Several diagnostic sensors (temperatures, cell voltages, SOC limits, timeouts) are available but disabled by default — enable them in the entity settings if needed.

### Binary Sensors (9)

| Sensor | Description |
|--------|-------------|
| AC Input Connected | Shore power or generator plugged in |
| AC Output On | AC inverter active |
| DC Output On | DC/Anderson outputs active |
| 12V Car Output On | 12V car socket active |
| Battery Charging | Charge current flowing into battery |
| Solar Charging | Solar panels producing power |
| X-Boost Active | X-Boost mode engaged |
| AC Slow Charging | Slow/silent AC charging mode active |
| Battery Fault | Any BMS fault code present |

### Switches (7)

| Switch | Description |
|--------|-------------|
| AC Output | Enable / disable AC inverter output |
| DC Output | Enable / disable DC/Anderson outputs |
| X-Boost | Enable X-Boost for high-wattage appliances |
| AC Slow Charging | Silent low-power AC charging mode |
| USB Output | Enable / disable USB ports |
| Beep Sound | Audible feedback on button presses |
| Fan Auto Speed | Automatic fan speed control |

### Number Controls (9)

| Control | Range | Description |
|---------|-------|-------------|
| AC Charging Power | 200–3000 W | Maximum AC input charging rate |
| Max Charge Level | 30–100 % | Upper SOC limit (battery protection) |
| Min Discharge Level | 0–30 % | Lower SOC cutoff |
| Generator Auto-Start Level | 0–30 % | SOC level that triggers smart generator start |
| Generator Auto-Stop Level | 50–100 % | SOC level that stops the generator |
| Standby Timeout | 0–5999 min | Auto power-off when idle (0 = never) |
| AC Output Auto-Off Timeout | 0–5999 min | AC inverter standby timeout |
| DC Input Charging Current | 4–8 A | Max current for car/DC charging |
| LCD Brightness | 0–100 % | Screen brightness |

### Selects (2)

| Select | Options |
|--------|---------|
| DC Input Mode | Auto, MPPT (Solar), Adapter, DC, JD-Adapter, Non-Standard |
| AC Output Frequency | 50 Hz, 60 Hz |

## How It Works

The EcoFlow Delta Pro exposes a local TCP server on port 8055 using a binary framing protocol with CRC8 and CRC16 checksums. The integration:

1. Connects once at startup and queries all five device subsystems (power distribution, energy management, inverter, MPPT controller, battery management)
2. Listens for real-time push updates from the device (typically every few seconds)
3. Polls for fresh data every 30 seconds as a fallback
4. Automatically reconnects if the connection drops

Control commands (switches, numbers, selects) are sent as binary packets in the same protocol and take effect immediately on the device.

## Firmware Note

EcoFlow closed local port 8055 in some firmware versions and reopened it in **3.0.2.21**. If you cannot connect, check your firmware version in the EcoFlow app (Device → About). If you are on older firmware, contact EcoFlow support or check the [EcoFlow community forums](https://community.ecoflow.com) for firmware update options.

## Contributing

Pull requests welcome. If your device sends data that doesn't parse correctly, enabling Home Assistant debug logging for `custom_components.ecoflow_delta_pro` and sharing the output is the fastest way to diagnose issues.

## License

MIT
