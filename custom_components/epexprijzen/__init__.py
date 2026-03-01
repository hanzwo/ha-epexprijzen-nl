"""The epexprijzen.nl integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_INTERVAL, CONF_PROVIDER, DOMAIN
from .coordinator import EpexPrijzenCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up epexprijzen.nl from a config entry."""
    # Options (from OptionsFlow) override initial config data.
    config = {**entry.data, **entry.options}
    provider: str = config[CONF_PROVIDER]
    interval: str = config[CONF_INTERVAL]

    coordinator = EpexPrijzenCoordinator(hass, provider, interval)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options updates (provider or interval changed)."""
    await hass.config_entries.async_reload(entry.entry_id)
