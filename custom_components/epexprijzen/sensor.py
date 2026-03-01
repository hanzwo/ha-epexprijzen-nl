"""Sensor platform for epexprijzen.nl."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_INTERVAL, CONF_PROVIDER, DOMAIN, INTERVAL_QUARTERLY, PROVIDERS
from .coordinator import EpexPrijzenCoordinator

_LOGGER = logging.getLogger(__name__)

PRICE_UNIT = "€/kWh"


@dataclass(frozen=True, kw_only=True)
class EpexPrijzenSensorEntityDescription(SensorEntityDescription):
    """Describes an EP:Exprijzen sensor."""


SENSOR_DESCRIPTIONS: tuple[EpexPrijzenSensorEntityDescription, ...] = (
    EpexPrijzenSensorEntityDescription(
        key="current_price",
        translation_key="current_price",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
    ),
    EpexPrijzenSensorEntityDescription(
        key="today_min",
        translation_key="today_min",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
    ),
    EpexPrijzenSensorEntityDescription(
        key="today_max",
        translation_key="today_max",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
    ),
    EpexPrijzenSensorEntityDescription(
        key="today_avg",
        translation_key="today_avg",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
    ),
    EpexPrijzenSensorEntityDescription(
        key="tomorrow_min",
        translation_key="tomorrow_min",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
    ),
    EpexPrijzenSensorEntityDescription(
        key="tomorrow_max",
        translation_key="tomorrow_max",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
    ),
    EpexPrijzenSensorEntityDescription(
        key="tomorrow_avg",
        translation_key="tomorrow_avg",
        native_unit_of_measurement=PRICE_UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=4,
    ),
)


def _parse_timestamp(ts: str) -> datetime:
    """Parse an ISO‑8601 UTC timestamp string into an aware datetime."""
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def _find_current_price(entries: list[dict[str, Any]]) -> float | None:
    """Return the price for the current period (most recent entry whose time ≤ now)."""
    now = datetime.now(timezone.utc)
    current: float | None = None
    for entry in sorted(entries, key=lambda e: e["t"]):
        if _parse_timestamp(entry["t"]) <= now:
            current = entry["price"]
        else:
            break
    return current


def _find_current_timestamp(entries: list[dict[str, Any]]) -> str | None:
    """Return the timestamp string of the current period."""
    now = datetime.now(timezone.utc)
    current_ts: str | None = None
    for entry in sorted(entries, key=lambda e: e["t"]):
        if _parse_timestamp(entry["t"]) <= now:
            current_ts = entry["t"]
        else:
            break
    return current_ts


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up EP:Exprijzen sensors from a config entry."""
    coordinator: EpexPrijzenCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        EpexPrijzenSensor(coordinator, entry, description)
        for description in SENSOR_DESCRIPTIONS
    )


class EpexPrijzenSensor(CoordinatorEntity[EpexPrijzenCoordinator], SensorEntity):
    """Representation of an EP:Exprijzen sensor."""

    entity_description: EpexPrijzenSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EpexPrijzenCoordinator,
        entry: ConfigEntry,
        description: EpexPrijzenSensorEntityDescription,
    ) -> None:
        """Initialise the sensor."""
        super().__init__(coordinator)
        self.entity_description = description

        config = {**entry.data, **entry.options}
        provider = config[CONF_PROVIDER]
        interval = config[CONF_INTERVAL]
        slug = f"{provider}_{interval}"

        self._attr_unique_id = f"{slug}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, slug)},
            "name": PROVIDERS.get(provider, provider),
            "manufacturer": "epexprijzen.nl",
            "model": f"{PROVIDERS.get(provider, provider)} – {'per kwartier' if interval == INTERVAL_QUARTERLY else 'per uur'}",
            "configuration_url": "https://epexprijzen.nl",
        }

    @property
    def _today(self) -> list[dict[str, Any]]:
        return self.coordinator.data.get("today") or []

    @property
    def _tomorrow(self) -> list[dict[str, Any]]:
        return self.coordinator.data.get("tomorrow") or []

    @property
    def native_value(self) -> float | None:
        """Return the sensor value."""
        key = self.entity_description.key

        if key == "current_price":
            return _find_current_price(self._today)

        if key == "today_min":
            if not self._today:
                return None
            return min(e["price"] for e in self._today)

        if key == "today_max":
            if not self._today:
                return None
            return max(e["price"] for e in self._today)

        if key == "today_avg":
            if not self._today:
                return None
            prices = [e["price"] for e in self._today]
            return round(sum(prices) / len(prices), 6)

        if key == "tomorrow_min":
            if not self._tomorrow:
                return None
            return min(e["price"] for e in self._tomorrow)

        if key == "tomorrow_max":
            if not self._tomorrow:
                return None
            return max(e["price"] for e in self._tomorrow)

        if key == "tomorrow_avg":
            if not self._tomorrow:
                return None
            prices = [e["price"] for e in self._tomorrow]
            return round(sum(prices) / len(prices), 6)

        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        key = self.entity_description.key
        data = self.coordinator.data
        attrs: dict[str, Any] = {}

        if key == "current_price":
            # Expose full price lists so apexcharts-card can read them directly.
            attrs["today"] = self._today
            attrs["tomorrow"] = self._tomorrow if self._tomorrow else None
            attrs["energy_tax"] = data.get("energy_tax")
            attrs["provider_charge"] = data.get("provider_charge")
            attrs["current_period"] = _find_current_timestamp(self._today)

        elif key in ("today_min", "today_max"):
            entries = self._today
            if entries:
                target_price = (
                    min(e["price"] for e in entries)
                    if "min" in key
                    else max(e["price"] for e in entries)
                )
                match = next((e for e in entries if e["price"] == target_price), None)
                if match:
                    attrs["timestamp"] = match["t"]
                    dt = _parse_timestamp(match["t"])
                    local_dt = dt.astimezone()
                    attrs["local_time"] = local_dt.strftime("%H:%M")

        elif key in ("tomorrow_min", "tomorrow_max"):
            entries = self._tomorrow
            if entries:
                target_price = (
                    min(e["price"] for e in entries)
                    if "min" in key
                    else max(e["price"] for e in entries)
                )
                match = next((e for e in entries if e["price"] == target_price), None)
                if match:
                    attrs["timestamp"] = match["t"]
                    dt = _parse_timestamp(match["t"])
                    local_dt = dt.astimezone()
                    attrs["local_time"] = local_dt.strftime("%H:%M")

        return attrs
