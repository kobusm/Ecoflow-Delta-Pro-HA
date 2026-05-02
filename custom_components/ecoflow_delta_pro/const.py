"""Constants for the EcoFlow Delta Pro integration."""
DOMAIN = "ecoflow_delta_pro"

CONF_HOST = "host"
CONF_PORT = "port"

DEFAULT_PORT = 8055
SCAN_INTERVAL = 30  # seconds between forced refresh polls

# DC input type configuration values
DC_IN_TYPES = {
    0: "Auto",
    1: "MPPT",
    2: "Adapter",
    3: "DC",
    4: "JD-Adapter",
    5: "Non-Standard",
}
