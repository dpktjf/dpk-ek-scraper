"""Custom types for eto_irrigation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

    from .api import ScraperApiClient
    from .coordinator import ScraperDataUpdateCoordinator


type ScraperConfigEntry = ConfigEntry[ScraperData]


@dataclass
class ScraperData:
    """Data for the scraper."""

    name: str
    client: ScraperApiClient
    coordinator: ScraperDataUpdateCoordinator
