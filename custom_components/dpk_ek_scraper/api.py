"""Sample API Client."""

from __future__ import annotations

import logging
import socket
from threading import Lock
from typing import TYPE_CHECKING, Any

import aiohttp
import async_timeout

from custom_components.dpk_ek_scraper.api_models import Flight, FlightSearchResult

if TYPE_CHECKING:
    from custom_components.dpk_ek_scraper.config import ScraperConfig

_LOGGER = logging.getLogger(__name__)


class ScraperError(Exception):
    """Exception to indicate a general API error."""


class ScraperCommunicationError(
    ScraperError,
):
    """Exception to indicate a communication error."""


class ScraperAuthenticationError(
    ScraperError,
):
    """Exception to indicate an authentication error."""


class ScraperBadRequestError(
    ScraperError,
):
    """Exception to indicate a bad request error."""


class ScraperCalculationError(
    ScraperError,
):
    """Exception to indicate a calculation error."""


class ScraperCalculationStartupError(
    ScraperError,
):
    """Exception to indicate a calculation error - probably due to start-up ."""


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """Verify that the response is valid."""
    if response.status in (401, 403):
        msg = "Invalid credentials"
        raise ScraperAuthenticationError(
            msg,
        )
    response.raise_for_status()


class ScraperApiClient:
    """API Client."""

    def __init__(
        self,
        config: ScraperConfig,
        # name: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Sample API Client."""
        self.config = config
        self._session = session

    async def async_fetch_flights(self) -> FlightSearchResult:
        """Get data from the API."""
        uri = (
            f"origin={self.config.origin}&destination={self.config.destination}"
            f"&depart={self.config.departure_date}&return={self.config.return_date}"
            f"&max_legs={int(self.config.max_legs)}&max_duration={self.config.max_duration}"
            f"&class={self.config.ticket_class}"
        )
        _LOGGER.debug("uri=%s", uri)
        return await self._api_wrapper(
            method="get",
            url=f"http://jupiter:1880/ek-scraper?{uri}",
            headers={"Content-type": "application/json; charset=UTF-8"},
        )

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> Any:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(180):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                )
                _verify_response_or_raise(response)
                raw = await response.json()
                flights = FlightSearchResult.from_dict(raw)
                _LOGGER.debug(
                    "Fetched %d flights, returns %d",
                    len(flights.all_flights),
                    len(flights.return_flights),
                )
                return flights

        except TimeoutError as exception:
            msg = f"Timeout error fetching information - {exception}"
            raise ScraperCommunicationError(
                msg,
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching information - {exception}"
            raise ScraperCommunicationError(
                msg,
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Something really wrong happened! - {exception}"
            raise ScraperBadRequestError(
                msg,
            ) from exception
