"""Data update coordinator for epexprijzen.nl."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import API_URL, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class EpexPrijzenCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator that fetches energy price data from epexprijzen.nl."""

    def __init__(self, hass: HomeAssistant, provider: str, interval: str) -> None:
        """Initialise the coordinator."""
        self.provider = provider
        self.interval = interval
        self._url = API_URL.format(provider=provider, interval=interval)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the API."""
        session = async_get_clientsession(self.hass)
        try:
            async with session.get(self._url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                response.raise_for_status()
                data: dict[str, Any] = await response.json()
        except aiohttp.ClientResponseError as err:
            raise UpdateFailed(
                f"Error communicating with epexprijzen.nl (HTTP {err.status}): {err.message}"
            ) from err
        except aiohttp.ClientError as err:
            raise UpdateFailed(
                f"Error communicating with epexprijzen.nl: {err}"
            ) from err

        return data
