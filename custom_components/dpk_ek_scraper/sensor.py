"""Sensor platform for scaper."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.dpk_ek_scraper.const import (
    ATTRIBUTION,
    DOMAIN,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import ScraperDataUpdateCoordinator
    from .data import ScraperConfigEntry

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ScraperConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    # use the typed .flights property
    coordinator: ScraperDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    sensors = [ScraperSensor(coordinator, flight.id) for flight in coordinator.flights]
    async_add_entities(sensors)


class ScraperSensor(CoordinatorEntity, SensorEntity):
    """Scraper Sensor class."""

    _attr_should_poll = False
    _attr_attribution = ATTRIBUTION
    _attr_icon = "mdi:airplane"

    def __init__(
        self,
        coordinator,
        flight_id: str,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.coordinator: ScraperDataUpdateCoordinator = coordinator
        self.flight_id = flight_id
        self._attr_unique_id = f"{DOMAIN}_{flight_id}"
        self._attr_name = f"Flight {flight_id}"

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success

    async def async_added_to_hass(self) -> None:
        """Connect to dispatcher listening for entity data notifications."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self) -> None:
        """Get the latest data from OWM and updates the states."""
        await self.coordinator.async_request_refresh()

    @property
    def native_value(self):
        """Return the current price of the flight."""
        flight = next(
            (f for f in self.coordinator.data if f.id == self.flight_id), None
        )
        return flight.price.amount if flight else None
