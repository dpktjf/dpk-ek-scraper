from dataclasses import dataclass


@dataclass
class ScraperConfig:
    """
    Configuration for the scraper.

    Attributes
    ----------
    origin : str
        The airport origin location code.
    destination : str
        The airport destination location code.
    depart_date : str
        Departure date in YYYY-MM-DD format.
    return_date : str
        Return date in YYYY-MM-DD format.
    max_legs : str
        Maximum number of flight legs.
    max_duration : str
        Maximum duration of the trip.
    clas : str
        Travel class (econ, prem, bus or first).
    """

    origin: str
    destination: str
    departure_date: str
    return_date: str
    max_legs: str
    max_duration: str
    ticket_class: str
    # Add other config properties here
