"""Config flow for epexprijzen.nl."""
from __future__ import annotations

from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import (
    API_URL,
    CONF_INTERVAL,
    CONF_PROVIDER,
    DOMAIN,
    INTERVAL_HOURLY,
    INTERVAL_QUARTERLY,
    PROVIDERS,
)

INTERVALS = {
    INTERVAL_HOURLY: "Per uur (hourly)",
    INTERVAL_QUARTERLY: "Per kwartier (quarterly)",
}


def _build_schema(
    provider: str = "anwb-energie",
    interval: str = INTERVAL_HOURLY,
) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_PROVIDER, default=provider): SelectSelector(
                SelectSelectorConfig(
                    options=[
                        SelectOptionDict(value=k, label=v)
                        for k, v in PROVIDERS.items()
                    ],
                    mode=SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(CONF_INTERVAL, default=interval): SelectSelector(
                SelectSelectorConfig(
                    options=[
                        SelectOptionDict(value=k, label=v)
                        for k, v in INTERVALS.items()
                    ],
                    mode=SelectSelectorMode.DROPDOWN,
                )
            ),
        }
    )


async def _test_connection(hass: Any, provider: str, interval: str) -> str | None:
    """Return an error key if the connection fails, otherwise None."""
    url = API_URL.format(provider=provider, interval=interval)
    session = async_get_clientsession(hass)
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            resp.raise_for_status()
            data = await resp.json()
            if "today" not in data:
                return "invalid_response"
    except aiohttp.ClientResponseError:
        return "cannot_connect"
    except aiohttp.ClientError:
        return "cannot_connect"
    return None


class EpexPrijzenConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for epexprijzen.nl."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            provider = user_input[CONF_PROVIDER]
            interval = user_input[CONF_INTERVAL]

            # Prevent duplicate entries for the same provider+interval combination.
            await self.async_set_unique_id(f"{provider}_{interval}")
            self._abort_if_unique_id_configured()

            error = await _test_connection(self.hass, provider, interval)
            if error:
                errors["base"] = error
            else:
                provider_name = PROVIDERS.get(provider, provider)
                interval_label = INTERVALS.get(interval, interval)
                return self.async_create_entry(
                    title=f"{provider_name} ({interval_label})",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_build_schema(
                provider=user_input.get(CONF_PROVIDER, "anwb-energie") if user_input else "anwb-energie",
                interval=user_input.get(CONF_INTERVAL, INTERVAL_HOURLY) if user_input else INTERVAL_HOURLY,
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Return the options flow."""
        return EpexPrijzenOptionsFlow()


class EpexPrijzenOptionsFlow(OptionsFlow):
    """Handle options for epexprijzen.nl."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        current_provider = self.config_entry.data.get(CONF_PROVIDER, "anwb-energie")
        current_interval = self.config_entry.data.get(CONF_INTERVAL, INTERVAL_HOURLY)

        if user_input is not None:
            provider = user_input[CONF_PROVIDER]
            interval = user_input[CONF_INTERVAL]

            error = await _test_connection(self.hass, provider, interval)
            if error:
                errors["base"] = error
            else:
                return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=_build_schema(
                provider=user_input.get(CONF_PROVIDER, current_provider) if user_input else current_provider,
                interval=user_input.get(CONF_INTERVAL, current_interval) if user_input else current_interval,
            ),
            errors=errors,
        )
