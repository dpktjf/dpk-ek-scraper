"""
Data models for representing flight search results and related entities.

This module defines dataclasses for LocationInfo, Duration, Price, Leg, Flight,
and FlightSearchResult, along with methods for deserializing these objects from
dictionaries.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class AirportInfo:
    """Represents a flight segment with departure, airport, and arrival."""

    depart: str
    airport: str
    arrive: str

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "AirportInfo":
        """
        Create an AirportInfo instance from a dictionary.

        Args:
            data (dict[str, Any]): A dictionary containing 'depart', 'airport',
            and 'arrive' keys.

        Returns:
            AirportInfo: An instance of AirportInfo populated with the provided
            data.

        """
        return AirportInfo(
            depart=data["depart"], airport=data["airport"], arrive=data["arrive"]
        )


@dataclass
class LocationInfoReturn:
    """Represents the outbound and return schedule info."""

    outbound: AirportInfo
    return_: AirportInfo

    @staticmethod
    def from_dict(schedule: dict[str, Any]) -> "LocationInfoReturn":
        """
        Create a LocationInfoReturn instance from a dictionary.

        Args:
            schedule (dict[str, Any]): A dictionary containing 'outbound' and
            'return' keys, each mapping to an AirportInfo dictionary.

        Returns:
            LocationInfoReturn: An instance of LocationInfoReturn populated with
            the provided data.

        """
        return LocationInfoReturn(
            outbound=AirportInfo.from_dict(schedule["outbound"]),
            return_=AirportInfo.from_dict(schedule["return"]),
        )


@dataclass
class LocationInfo:
    """Represents a departure or arrival point in a flight."""

    time: str
    airport: str
    airport_name: str

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "LocationInfo":
        """
        Create a LocationInfo instance from a dictionary.

        Args:
            data (dict[str, Any]): A dictionary containing keys 'time',
            'airport', and 'airport_name'.

        Returns:
            LocationInfo: An instance of LocationInfo populated with the
            provided data.

        """
        return LocationInfo(
            time=data["time"],
            airport=data["airport"],
            airport_name=data["airport_name"],
        )


@dataclass
class Duration:
    """
    Represents the duration of a flight.

    Includes its length as a string and total hours as a float.
    """

    length: str
    hours: float

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Duration":
        """
        Create a Duration instance from a dictionary.

        Args:
            data (dict[str, Any]): A dictionary containing keys 'length' and 'hours'.

        Returns:
            Duration: An instance of Duration populated with the provided data.

        """
        return Duration(
            length=data["length"],
            hours=float(data["hours"]),
        )


@dataclass
class DurationReturn:
    """
    Represents the duration details for outbound and return flights.

    Attributes:
        outbound (float): Duration of the outbound flight in hours.
        return_ (float): Duration of the return flight in hours.
        total (float): Total duration of both flights in hours.

    """

    outbound: float
    return_: float
    total: float

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "DurationReturn":
        """
        Create a DurationReturn instance from a dictionary.

        Args:
            data (dict[str, Any]): A dictionary containing keys 'outbound',
            'return', and 'total'.

        Returns:
            DurationReturn: An instance of DurationReturn populated with the
            provided data.

        """
        return DurationReturn(
            outbound=float(data["outbound"]),
            return_=float(data["return"]),
            total=float(data["total"]),
        )


@dataclass
class Price:
    """
    Represents the price of a flight.

    Attributes:
        currency (str): The currency code (e.g., 'USD', 'EUR').
        amount (float): The price amount.

    """

    currency: str
    amount: float

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Price":
        """
        Create a Price instance from a dictionary.

        Args:
            data (dict[str, Any]): A dictionary containing keys 'currency' and 'amount'.

        Returns:
            Price: An instance of Price populated with the provided data.

        """
        return Price(
            currency=data["currency"],
            amount=float(data["amount"]),
        )


@dataclass
class PriceReturn:
    """
    Represents the price details for outbound and return flights.

    Attributes:
        outbound (float): Price of the outbound flight.
        return_ (float): Price of the return flight.
        total (float): Total price of both flights.
        currency (str): The currency code (e.g., 'USD', 'EUR').

    """

    outbound: float
    return_: float
    total: float
    currency: str

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "PriceReturn":
        """
        Create a PriceReturn instance from a dictionary.

        Args:
            data (dict[str, Any]): A dictionary containing keys 'outbound',
            'return', 'total', and 'currency'.

        Returns:
            PriceReturn: An instance of PriceReturn populated with the provided
            data.

        """
        return PriceReturn(
            outbound=float(data["outbound"]),
            return_=float(data["return"]),
            total=float(data["total"]),
            currency=data["currency"],
        )


@dataclass
class Leg:
    """
    Represents a segment (leg) of a flight.

    Attributes:
        flight_number (str): The flight number for this leg.
        aircraft (str): The aircraft type or model used for this leg.

    """

    flight_number: str
    aircraft: str

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Leg":
        """
        Create a Leg instance from a dictionary.

        Args:
            data (dict[str, Any]): A dictionary containing keys 'flight_number'
            and 'aircraft'.

        Returns:
            Leg: An instance of Leg populated with the provided data.

        """
        return Leg(
            flight_number=data["flight_number"],
            aircraft=data["aircraft"],
        )


@dataclass
class Flight:
    """
    Flight information.

    Represents a flight, including its departure and arrival information,
    duration, price, and legs.

    Attributes:
        id (str): Unique identifier for the flight.
        departure (LocationInfo): Departure location information.
        arrival (LocationInfo): Arrival location information.
        duration (Duration): Duration of the flight.
        price (Price): Price information for the flight.
        legs (list[Leg]): List of flight segments (legs).

    """

    id: str
    departure: LocationInfo
    arrival: LocationInfo
    duration: Duration
    price: Price
    legs: list[Leg]

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Flight":
        """
        Create a Flight instance from a dictionary.

        Args:
            data (dict[str, Any]): A dictionary containing flight information.

        Returns:
            Flight: An instance of Flight populated with the provided data.

        """
        return Flight(
            id=data["id"],
            departure=LocationInfo.from_dict(data["departure"]),
            arrival=LocationInfo.from_dict(data["arrival"]),
            duration=Duration.from_dict(data["duration"]),
            price=Price.from_dict(data["price"]),
            legs=[Leg.from_dict(leg) for leg in data["legs"]],
        )

    @staticmethod
    def from_list(data: list[dict[str, Any]]) -> list["Flight"]:
        """Convert a list of dicts into a list of Flight objects."""
        return [Flight.from_dict(item) for item in data]


@dataclass
class ReturnFlight:
    """
    Represents a round-trip flight, including schedule, duration, price, and legs.

    Attributes:
        id (str): Unique identifier for the return flight.
        schedule (LocationInfoReturn): Outbound and return schedule information.
        duration (DurationReturn): Duration details for outbound and return flights.
        price (PriceReturn): Price details for outbound and return flights.
        outbound_legs (list[str]): List of outbound flight leg identifiers.
        return_legs (list[str]): List of return flight leg identifiers.

    """

    id: str
    schedule: LocationInfoReturn
    duration: DurationReturn
    price: PriceReturn
    outbound_legs: list[str]
    return_legs: list[str]

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "ReturnFlight":
        """
        Create a ReturnFlight instance from a dictionary.

        Args:
            data (dict[str, Any]): A dictionary containing keys 'id', 'schedule',
            'duration', 'price', and 'legs' (with 'outbound' and 'return' lists).

        Returns:
            ReturnFlight: An instance of ReturnFlight populated with the
            provided data.

        """
        return ReturnFlight(
            id=data["id"],
            schedule=LocationInfoReturn.from_dict(data["schedule"]),
            duration=DurationReturn.from_dict(data["duration"]),
            price=PriceReturn.from_dict(data["price"]),
            outbound_legs=data["legs"]["outbound"],
            return_legs=data["legs"]["return"],
        )

    @staticmethod
    def from_list(data: list[dict[str, Any]]) -> list["ReturnFlight"]:
        """
        Convert a list of dictionaries into a list of ReturnFlight objects.

        Args:
            data (list[dict[str, Any]]): List of dictionaries representing
            return flights.

        Returns:
            list[ReturnFlight]: List of ReturnFlight instances.

        """
        return [ReturnFlight.from_dict(item) for item in data]


@dataclass
class TrackerStep:
    """Represents a single step in a tracking history."""

    step: str
    timestamp: datetime
    message: str

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "TrackerStep":
        """Parse a dict into a TrackerStep instance."""
        return TrackerStep(
            step=data["step"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            message=data["message"],
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert TrackerStep back to a serializable dict."""
        return {
            "step": self.step,
            "timestamp": self.timestamp.isoformat(),
            "message": self.message,
        }


@dataclass
class FlightSearchResult:
    """
    Represents the result of a flight search.

    Attributes:
        outbound (list[Flight]): List of outbound flights.
        return_ (list[Flight]): List of return flights ("return" is a reserved
        word, so use return_).

    """

    job_id: str
    result: int
    outbound: list[Flight] = field(default_factory=list)
    return_: list[Flight] = field(default_factory=list)
    return_flights: list[ReturnFlight] = field(default_factory=list)
    tracker: list[TrackerStep] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FlightSearchResult":
        """
        Create a FlightSearchResult instance from a dictionary.

        Args:
            data (dict[str, Any]): A dictionary containing keys 'outbound' and 'return',
            each mapping to a list of flight dictionaries.

        Returns:
            FlightSearchResult: An instance of FlightSearchResult populated with
            the provided data.

        """
        return cls(
            job_id=data.get("job_id", ""),
            result=data.get("result", 0),
            outbound=[Flight.from_dict(f) for f in data.get("outbound", [])],
            return_=[Flight.from_dict(f) for f in data.get("return", [])],
            return_flights=[
                ReturnFlight.from_dict(f) for f in data.get("combined", [])
            ],
            tracker=[TrackerStep.from_dict(f) for f in data.get("tracker", [])],
        )

    @property
    def all_flights(self) -> list[Flight]:
        """Combine outbound + return flights into one list."""
        return self.outbound + self.return_
