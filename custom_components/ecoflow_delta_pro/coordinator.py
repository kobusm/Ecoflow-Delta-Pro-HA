"""DataUpdateCoordinator for EcoFlow Delta Pro."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, SCAN_INTERVAL
from .protocol import EcoflowClient

_LOGGER = logging.getLogger(__name__)


class EcoflowCoordinator(DataUpdateCoordinator[dict]):
    """Manages a single EcoFlow Delta Pro connection and distributes data to entities."""

    def __init__(self, hass: HomeAssistant, client: EcoflowClient) -> None:
        self._client = client
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL),
        )

    async def async_setup(self) -> None:
        """Start the client and register the push-data callback."""
        self._client.register_callback(self._on_device_data)
        await self._client.start()

    async def async_shutdown(self) -> None:
        """Stop the client connection."""
        await self._client.stop()

    def _on_device_data(self, data: dict) -> None:
        """Called by the client whenever the device pushes a data update."""
        self.async_set_updated_data(data)

    async def _async_update_data(self) -> dict:
        """Periodic poll: request fresh data from the device."""
        if not self._client.connected:
            raise UpdateFailed("Not connected to EcoFlow device")
        await self._client.request_all()
        return self._client.data or self.data or {}

    async def async_send_command(self, packet: bytes) -> None:
        """Send a control command to the device."""
        await self._client.send_command(packet)
