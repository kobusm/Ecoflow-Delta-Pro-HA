"""Async TCP client for EcoFlow Delta Pro local API (port 8055)."""
from __future__ import annotations

import asyncio
import logging
from typing import Callable

from .packet import (
    KEY_BMS_EXTRA, KEY_BMS_EXTRA2, KEY_BMS_MAIN, KEY_EMS,
    KEY_INV, KEY_MPPT, KEY_PD,
    decode_packet, extract_packets, get_all_queries,
)
from .parser import parse_bms, parse_ems, parse_inv, parse_mppt, parse_pd

_LOGGER = logging.getLogger(__name__)

DataCallback = Callable[[dict], None]

_READ_CHUNK = 4096
_RECONNECT_DELAY = 10  # seconds


class EcoflowClient:
    """Persistent TCP connection to an EcoFlow Delta Pro on port 8055."""

    def __init__(self, host: str, port: int = 8055) -> None:
        self._host = host
        self._port = port
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._buffer = b""
        self._data: dict = {}
        self._callbacks: list[DataCallback] = []
        self._listener_task: asyncio.Task | None = None
        self._running = False

    # ── Public API ──────────────────────────────────────────────────────────

    @property
    def data(self) -> dict:
        return dict(self._data)

    @property
    def connected(self) -> bool:
        return self._writer is not None and not self._writer.is_closing()

    def register_callback(self, cb: DataCallback) -> None:
        self._callbacks.append(cb)

    def remove_callback(self, cb: DataCallback) -> None:
        self._callbacks.discard(cb) if hasattr(self._callbacks, "discard") else None
        if cb in self._callbacks:
            self._callbacks.remove(cb)

    async def start(self) -> None:
        """Connect and start the background listener with auto-reconnect."""
        self._running = True
        self._listener_task = asyncio.create_task(self._run_forever())

    async def stop(self) -> None:
        """Disconnect and stop the background listener."""
        self._running = False
        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass
        self._disconnect()

    async def request_all(self) -> None:
        """Send query commands to request fresh data from the device."""
        if not self.connected:
            return
        for cmd in get_all_queries():
            await self._send_raw(cmd)

    async def send_command(self, packet: bytes) -> None:
        """Send a raw command packet to the device."""
        if not self.connected:
            raise ConnectionError("Not connected to EcoFlow device")
        await self._send_raw(packet)

    # ── Internal ────────────────────────────────────────────────────────────

    async def _run_forever(self) -> None:
        while self._running:
            try:
                await self._connect()
                await self._listen()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                _LOGGER.warning("EcoFlow connection error: %s – reconnecting in %ds", exc, _RECONNECT_DELAY)
            finally:
                self._disconnect()
            if self._running:
                await asyncio.sleep(_RECONNECT_DELAY)

    async def _connect(self) -> None:
        _LOGGER.debug("Connecting to %s:%d", self._host, self._port)
        self._reader, self._writer = await asyncio.wait_for(
            asyncio.open_connection(self._host, self._port), timeout=10
        )
        self._buffer = b""
        _LOGGER.info("Connected to EcoFlow at %s:%d", self._host, self._port)
        await self.request_all()

    def _disconnect(self) -> None:
        if self._writer:
            try:
                self._writer.close()
            except Exception:
                pass
        self._reader = None
        self._writer = None

    async def _listen(self) -> None:
        while self._running:
            chunk = await asyncio.wait_for(self._reader.read(_READ_CHUNK), timeout=60)
            if not chunk:
                _LOGGER.warning("EcoFlow device closed connection")
                break
            self._buffer += chunk
            packets, self._buffer = extract_packets(self._buffer)
            for pkt in packets:
                self._handle_packet(pkt)

    async def _send_raw(self, data: bytes) -> None:
        try:
            self._writer.write(data)
            await self._writer.drain()
        except Exception as exc:
            _LOGGER.error("Failed to send command: %s", exc)

    def _handle_packet(self, packet: bytes) -> None:
        try:
            src, cmd_set, cmd_id, payload = decode_packet(packet)
            key = (src, cmd_set, cmd_id)

            if key == KEY_PD:
                updates = parse_pd(payload)
            elif key == KEY_EMS:
                updates = parse_ems(payload)
            elif key == KEY_INV:
                updates = parse_inv(payload)
            elif key == KEY_MPPT:
                updates = parse_mppt(payload)
            elif key == KEY_BMS_MAIN:
                updates = parse_bms(payload, prefix="")
            elif key in (KEY_BMS_EXTRA, KEY_BMS_EXTRA2):
                updates = parse_bms(payload, prefix="extra_")
            else:
                return

            self._data.update(updates)
            for cb in self._callbacks:
                try:
                    cb(dict(self._data))
                except Exception as exc:
                    _LOGGER.error("Callback error: %s", exc)

        except Exception as exc:
            _LOGGER.debug("Failed to handle packet: %s", exc)
