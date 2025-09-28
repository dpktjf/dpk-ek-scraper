"""DataUpdateCoordinator for eto_irrigation."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from custom_components.dpk_ek_scraper.api_models import (
    Flight,
    FlightSearchResult,
    ReturnFlight,
)

from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .api import (
        ScraperApiClient,
    )


class ScraperDataUpdateCoordinator(DataUpdateCoordinator[FlightSearchResult]):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, client: ScraperApiClient) -> None:
        """Initialize."""
        self.hass = hass
        self.api = client

        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )

    async def _async_update_data(self) -> FlightSearchResult:
        """Fetch latest data from the API."""
        try:
            return await self.api.async_fetch_flights()
        except Exception as err:
            raise UpdateFailed(f"API error: {err}") from err  # noqa: EM102, TRY003

    @property
    def flights(self) -> list[Flight]:
        """Typed accessor for the coordinator data (never None)."""
        # self.data can be None before first refresh; return empty list in that case
        return list(self.data.all_flights) if self.data else []

    @property
    def return_flights(self) -> list[ReturnFlight]:
        """Typed accessor for the coordinator data (never None)."""
        # self.data can be None before first refresh; return empty list in that case
        return list(self.data.return_flights) if self.data else []
