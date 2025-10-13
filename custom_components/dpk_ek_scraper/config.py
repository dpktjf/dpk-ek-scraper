"""
Configuration definitions for the dpk_ek_scraper component.

This module contains dataclasses and related configuration structures for the
scraper.
"""

import re
from dataclasses import dataclass


@dataclass
class ScraperConfig:
    """
    Configuration for the scraper.

    Attributes:
        webhook_id : str
            The unique identifier for the webhook.
        origin : str
            The airport origin location code.
        destination : str
            The airport destination location code.
        depart_date : str
            Departure date in YYYY-MM-DD format.
        return_date : str
            Return date in YYYY-MM-DD format.
        max_legs : int
            Maximum number of flight legs.
        max_duration : float
            Maximum duration of the trip.
        clas : str
            Travel class (econ, prem, bus or first).

    """

    origin: str
    destination: str
    departure_date: str
    return_date: str
    ticket_class: str
    max_legs: int | None = None
    max_duration: float | None = None
    webhook_id: str | None = None
    # Add other config properties here

    def job_id(self) -> str:
        """
        Generate a unique job ID based on the configuration.

        Returns:
            str: A unique identifier string for the job.

        """
        base = (
            f"{self.origin}-{self.destination}-"
            f"{self.ticket_class}-"
            f"{self.departure_date}-{self.return_date}"
        )
        return re.sub(r"[^A-Za-z0-9_]", "_", base).lower()

    def equals(self, other: "ScraperConfig") -> bool:
        """
        Check if this configuration is equal to another configuration.

        Args:
            other (ScraperConfig): The other configuration to compare against.

        Returns:
            bool: True if configurations are equal, False otherwise.

        """
        return (
            self.origin == other.origin
            and self.destination == other.destination
            and self.departure_date == other.departure_date
            and self.return_date == other.return_date
            and self.ticket_class == other.ticket_class
        )
        # Note: max_legs and max_duration are intentionally excluded from
        # equality check
        # as they do not affect the job_id or uniqueness of the config.
