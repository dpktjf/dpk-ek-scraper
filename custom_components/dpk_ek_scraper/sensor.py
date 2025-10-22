"""Sensor platform for scaper."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.dpk_ek_scraper.const import (
    ATTR_ARRIVAL_TIME,
    ATTR_DEPARTURE_TIME,
    ATTR_DESTINATION,
    ATTR_DESTINATION_NAME,
    ATTR_DURATION,
    ATTR_LEGS,
    ATTR_ORIGIN,
    ATTR_ORIGIN_NAME,
    ATTR_OUT_ARRIVE,
    ATTR_OUT_DEPART,
    ATTR_OUT_DURATION,
    ATTR_OUT_LEGS,
    ATTR_OUT_PRICE,
    ATTR_OUTBOUND,
    ATTR_RET_ARRIVE,
    ATTR_RET_DEPART,
    ATTR_RET_DURATION,
    ATTR_RET_LEGS,
    ATTR_RET_PRICE,
    ATTR_RETURN,
    ATTRIBUTION,
    DOMAIN,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from custom_components.dpk_ek_scraper.api_models import Flight, ReturnFlight

    from .coordinator import ScraperDataUpdateCoordinator
    from .data import ScraperConfigEntry

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ScraperConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    """
    # use the typed .flights property
    # skipping individual legs for now - too many sensors
    coordinator: ScraperDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    """
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    """
    sensors = [ScraperSensor(coordinator, flight) for flight in coordinator.flights]
    async_add_entities(sensors)
    """
    _LOGGER.debug("Setting up sensors for return flights")
    _LOGGER.debug("job id=%s", coordinator.data.job_id)
    _LOGGER.debug("Coordinator data: %s", coordinator.is_ok())
    _LOGGER.debug("Return flights: %s", coordinator.return_flights())
    _LOGGER.debug("All data: %s", coordinator.data)
    sensors2 = [
        ScraperReturnSensor(coordinator, flight)
        for flight in coordinator.return_flights()
    ]
    async_add_entities(sensors2)


class ScraperSensor(CoordinatorEntity, SensorEntity):
    """Scraper Sensor class."""

    _attr_should_poll = False
    _attr_attribution = ATTRIBUTION
    _attr_icon = "mdi:airplane"

    def __init__(
        self,
        coordinator: Any,
        flight: Flight,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.coordinator: ScraperDataUpdateCoordinator = coordinator
        self.flight = flight
        self._attr_unique_id = f"{DOMAIN}_{flight.id}"
        self._attr_name = f"Flight {flight.id}"
        # Set device class to monetary
        self._attr_device_class = SensorDeviceClass.MONETARY  # special class for money
        self._attr_native_unit_of_measurement = flight.price.currency
        self._attr_state_class = "total"

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
    def native_value(self) -> float | None:
        """Return the current price of the flight."""
        if self.coordinator.data and hasattr(self.coordinator.data, "all_flights"):
            flight = next(
                (
                    f
                    for f in self.coordinator.data.all_flights
                    if f.id == self.flight.id
                ),
                None,
            )
            return flight.price.amount if flight else None
        return None

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra properties about this flight."""
        return {
            ATTR_ORIGIN: self.flight.departure.airport,
            ATTR_ORIGIN_NAME: self.flight.departure.airport_name,
            ATTR_DEPARTURE_TIME: self.flight.departure.time,
            ATTR_DESTINATION: self.flight.arrival.airport,
            ATTR_DESTINATION_NAME: self.flight.arrival.airport_name,
            ATTR_ARRIVAL_TIME: self.flight.arrival.time,
            ATTR_DURATION: self.flight.duration.length,
            ATTR_LEGS: [leg.flight_number for leg in self.flight.legs],
        }


class ScraperReturnSensor(CoordinatorEntity, SensorEntity):
    """Scraper Sensor class."""

    _attr_should_poll = False
    _attr_attribution = ATTRIBUTION
    _attr_icon = "mdi:airplane"

    def __init__(
        self,
        coordinator: Any,
        flight: ReturnFlight,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.coordinator: ScraperDataUpdateCoordinator = coordinator
        self.flight = flight
        self._attr_unique_id = f"{DOMAIN}_{flight.id}"
        self._attr_name = f"Flight {flight.id}"
        # Set device class to monetary
        self._attr_device_class = SensorDeviceClass.MONETARY  # special class for money
        self._attr_native_unit_of_measurement = flight.price.currency
        self._attr_state_class = "total"

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
    def native_value(self) -> float | None:
        """Return the current price of the flight."""
        if self.coordinator.data and hasattr(self.coordinator.data, "return_flights"):
            flight = next(
                (
                    f
                    for f in self.coordinator.data.return_flights
                    if f.id == self.flight.id
                ),
                None,
            )
            return flight.price.total if flight else None
        return None

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra properties about this flight."""
        return {
            ATTR_OUTBOUND: self.flight.schedule.outbound.airport,
            ATTR_OUT_DEPART: self.flight.schedule.outbound.depart,
            ATTR_OUT_ARRIVE: self.flight.schedule.outbound.arrive,
            ATTR_OUT_DURATION: self.flight.duration.outbound,
            ATTR_OUT_PRICE: self.flight.price.outbound,
            ATTR_OUT_LEGS: self.flight.outbound_legs,
            ATTR_RETURN: self.flight.schedule.return_.airport,
            ATTR_RET_DEPART: self.flight.schedule.return_.depart,
            ATTR_RET_ARRIVE: self.flight.schedule.return_.arrive,
            ATTR_RET_DURATION: self.flight.duration.return_,
            ATTR_RET_PRICE: self.flight.price.return_,
            ATTR_RET_LEGS: self.flight.return_legs,
            ATTR_DURATION: self.flight.duration.total,
            ATTR_LEGS: list(self.flight.outbound_legs) + list(self.flight.return_legs),
        }
