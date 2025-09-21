from dataclasses import dataclass
from typing import Any


@dataclass
class LocationInfo:
    """Represents a departure or arrival point in a flight."""

    time: str
    airport: str
    airport_name: str

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "LocationInfo":
        return LocationInfo(
            time=data["time"],
            airport=data["airport"],
            airport_name=data["airport_name"],
        )


@dataclass
class Duration:
    length: str
    hours: float

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Duration":
        return Duration(
            length=data["length"],
            hours=float(data["hours"]),
        )


@dataclass
class Price:
    currency: str
    amount: float

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Price":
        return Price(
            currency=data["currency"],
            amount=float(data["amount"]),
        )


@dataclass
class Leg:
    flight_number: str
    aircraft: str

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Leg":
        return Leg(
            flight_number=data["flight_number"],
            aircraft=data["aircraft"],
        )


@dataclass
class Flight:
    id: str
    departure: LocationInfo
    arrival: LocationInfo
    duration: Duration
    price: Price
    legs: list[Leg]

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Flight":
        return Flight(
            id=data["id"],
            departure=LocationInfo.from_dict(data["departure"]),
            arrival=LocationInfo.from_dict(data["arrival"]),
            duration=Duration.from_dict(data["duration"]),
            price=Price.from_dict(data["price"]),
            legs=[Leg.from_dict(l) for l in data["legs"]],
        )

    @staticmethod
    def from_list(data: list[dict[str, Any]]) -> list["Flight"]:
        """Convert a list of dicts into a list of Flight objects."""
        return [Flight.from_dict(item) for item in data]
