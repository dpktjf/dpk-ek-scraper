"""
Custom integration to integrate dpk_ek_scraper with Home Assistant.

For more details about this integration, please refer to
https://github.com/dpktjf/dpk-ek-irrigation
"""

from __future__ import annotations

import datetime
import logging
from typing import TYPE_CHECKING, Any

from homeassistant.const import (
    Platform,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.dpk_ek_scraper.config import ScraperConfig

from .api import ScraperApiClient
from .const import (
    CONF_CLASS,
    CONF_DEPART,
    CONF_DEST,
    CONF_MAX_DURATION,
    CONF_MAX_LEGS,
    CONF_ORIGIN,
    CONF_RETURN,
    DOMAIN,
)
from .coordinator import ScraperDataUpdateCoordinator

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from .data import ScraperConfigEntry

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
]

# https://homeassistantapi.readthedocs.io/en/latest/api.html

_LOGGER = logging.getLogger(__name__)
TODAY = datetime.datetime.now(tz=datetime.UTC).date().isoformat()


def get_option(entry: ConfigEntry, key: str, default: Any = None) -> Any:
    """

    Retrieve an option value from a config entry.

    Checking options first, then data, and falling back to a default.

    Args:
        entry (ConfigEntry): The configuration entry to retrieve the option from.
        key (str): The key of the option to retrieve.
        default (Any, optional): The default value to return if the key is not
        found. Defaults to None.

    Returns:
        Any: The value of the option if found, otherwise the default value.

    """
    return entry.options.get(key, entry.data.get(key, default))


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(
    hass: HomeAssistant,
    entry: ScraperConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    cfg = ScraperConfig(
        origin=get_option(entry, CONF_ORIGIN, "LON"),
        destination=get_option(entry, CONF_DEST, "DXB"),
        departure_date=get_option(entry, CONF_DEPART, TODAY),
        return_date=get_option(entry, CONF_RETURN, TODAY),
        max_legs=get_option(entry, CONF_MAX_LEGS, 2),
        max_duration=get_option(entry, CONF_MAX_DURATION, 15.5),
        ticket_class=get_option(entry, CONF_CLASS, "Economy"),
    )

    api = ScraperApiClient(
        config=cfg,
        session=async_get_clientsession(hass),
    )
    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    coordinator = ScraperDataUpdateCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    entry.async_on_unload(entry.add_update_listener(async_update_options))
    """
    entry.runtime_data = ScraperData(_name, api, coordinator)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    """
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

    """
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    """
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
