"""DataUpdateCoordinator for eto_irrigation."""

from __future__ import annotations

import logging
import secrets
from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.components import webhook
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from custom_components.dpk_ek_scraper.api_models import (
    Flight,
    FlightSearchResult,
    ReturnFlight,
    TrackerStep,
)

from .const import (
    CONF_WEBHOOK,
    DOMAIN,
    RAND_MAX_MINUTES,
    RAND_MIN_MINUTES,
    UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .api import (
        ScraperApiClient,
    )


class ScraperDataUpdateCoordinator(DataUpdateCoordinator[FlightSearchResult | None]):
    """Class to manage fetching data from the API."""

    def __init__(
        self, hass: HomeAssistant, client: ScraperApiClient, config: dict
    ) -> None:
        """Initialize."""
        self.hass = hass
        self.api = client
        self.config = config
        self.data: FlightSearchResult | None = None
        self.job_id = client.config.job_id()

        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )

    async def _async_update_data(self) -> FlightSearchResult | None:
        """Queue the scrape job on schedule."""
        try:
            webhook_id = self.config.get(CONF_WEBHOOK)
            url = f"http://192.168.1.174:8123/api/webhook/{webhook_id}"
            if webhook_id is None:
                raise UpdateFailed("Webhook ID is missing in the configuration.")
            url = webhook.async_generate_url(self.hass, webhook_id)
            await self.api.trigger_scrape(url)
        except Exception as err:
            raise UpdateFailed(f"API error: {err}") from err  # noqa: EM102, TRY003
        # ✅ After triggering, randomize the next interval -basically between the
        # rand_min_minutes and rand_max_minutes values in const.py
        # to avoid hitting EK too regularly
        # (which might lead to blocking)
        new_minutes = secrets.randbelow(RAND_MAX_MINUTES) + RAND_MIN_MINUTES
        self.update_interval = timedelta(minutes=new_minutes)
        _LOGGER.debug(
            "Next scrape for %s scheduled in %d minutes", self.job_id, new_minutes
        )
        return self.data

    @callback
    async def async_handle_webhook(self, payload: dict) -> None:
        """Receive results for any job (expecting matching job_id)."""
        self.job_id = payload.get("job_id")
        result: FlightSearchResult = FlightSearchResult.from_dict(payload)
        if result.job_id != self.job_id:
            _LOGGER.warning(
                "Webhook job_id %s does not match this coordinator (%s)",
                result.job_id,
                self.job_id,
            )
            return

        _LOGGER.info(
            "Webhook update for job %s (%d results)",
            result.job_id,
            len(result.return_flights),
        )

        self.async_set_updated_data(result)
        self.data = result

    @property
    def return_flights(self) -> list[ReturnFlight]:
        """Typed accessor for the coordinator data (never None)."""
        # self.data can be None before first refresh; return empty list in that
        # case
        return list(self.data.return_flights) if self.data else []

    @property
    def all_flights(self) -> list[Flight]:
        """Typed accessor for the coordinator data (never None)."""
        # self.data can be None before first refresh; return empty list in that case
        return list(self.data.all_flights) if self.data else []

    @property
    def tracker(self) -> list[TrackerStep]:
        """Typed accessor for the coordinator data (never None)."""
        # self.data can be None before first refresh; return empty list in that case
        return list(self.data.tracker) if self.data else []

    @property
    def is_ok(self) -> bool:
        """Typed accessor for the coordinator data (never None)."""
        """True if self.data exists and result == 0, else False."""
        return bool(self.data and self.data.result == 0)
