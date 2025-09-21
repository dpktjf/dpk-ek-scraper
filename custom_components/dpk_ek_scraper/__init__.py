"""
Custom integration to integrate dpk_ek_scraper with Home Assistant.

For more details about this integration, please refer to
https://github.com/dpktjf/dpk-ek-irrigation
"""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.const import (
    CONF_NAME,
    Platform,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.dpk_ek_scraper.config import ScraperConfig

from .api import ScraperApiClient
from .const import (
    DOMAIN,
    CONF_ORIGIN,
    CONF_DEST,
    CONF_DEPART,
    CONF_RETURN,
    CONF_MAX_LEGS,
    CONF_MAX_DURATION,
    CONF_CLASS,
)
from .coordinator import ScraperDataUpdateCoordinator
from .data import ScraperData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import ScraperConfigEntry

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
]

# https://homeassistantapi.readthedocs.io/en/latest/api.html

_LOGGER = logging.getLogger(__name__)

DEFAULT_SCAN_INTERVAL = timedelta(minutes=10)


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(
    hass: HomeAssistant,
    entry: ScraperConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    _name = entry.data[CONF_NAME]
    cfg = ScraperConfig(
        origin=entry.options[CONF_ORIGIN],
        destination=entry.options[CONF_DEST],
        departure_date=entry.options[CONF_DEPART],
        return_date=entry.options[CONF_RETURN],
        max_legs=entry.options[CONF_MAX_LEGS],
        max_duration=entry.options[CONF_MAX_DURATION],
        ticket_class=entry.options[CONF_CLASS],
    )

    api = ScraperApiClient(
        config=cfg,
        name=entry.data[CONF_NAME],
        session=async_get_clientsession(hass),
    )
    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    coordinator = ScraperDataUpdateCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    entry.async_on_unload(entry.add_update_listener(async_update_options))
    # entry.runtime_data = ScraperData(_name, api, coordinator)
    # await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    # return True
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_update_options(hass: HomeAssistant, entry: ScraperConfigEntry) -> None:
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ScraperConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    # return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
