from dataclasses import dataclass
from enum import Enum, auto

from geopy import distance


@dataclass
class Location:
    latitude: float
    longitude: float


class ElementType(Enum):
    BUS_STOP = auto()
    STOP = auto()
    TRAFFIC_LIGHT = auto()
    GIVE_WAY = auto()
    CROSSING = auto()
    TRAIN_RAIL = auto()
    GAZELLE_ROUTE = auto()


@dataclass
class Element:
    type: ElementType
    arguments: list[str]
    position: float

    @property
    def is_stop(self):
        return self.type in [ElementType.BUS_STOP, ElementType.GAZELLE_ROUTE]


@dataclass
class Block:
    way_id: str
    max_speed: int
    location: Location
    name: str
    length: float
    between: (int, int)
    elements: list[Element]
    is_roundabout: bool

    @property
    def id(self):
        return f"{self.way_id}:{self.between[0]}:{self.between[1]}"

    def contains_stop(self):
        return any(element.is_stop for element in self.elements)

    def ways_to_arrive(self, from_id):
        _, from_road_a, _ = from_id.split(":")
        is_reversed = int(from_road_a) == self.between[0]
        ways = {"walk"}

        ways.update(
            argument
            for element in self.elements
            if element.is_stop
            for argument in element.arguments
            if (int(argument.split(":")[0]) == -1 and is_reversed)
            or (int(argument.split(":")[0]) == 1 and not is_reversed)
        )

        return ways

    def length_to(self, other):
        return distance.distance((self.location.latitude, self.location.longitude),
                                 (other.location.latitude, other.location.longitude)).kilometers


@dataclass
class Route:
    name: str
    outbound_route: list[Block]
    return_route: list[Block]


class Node:
    def __init__(self, idx, g_score=float('inf'), f_score=float('inf'), parent=None):
        self.id = idx
        self.g_score = g_score
        self.f_score = f_score
        self.parent = parent

    def __lt__(self, other):
        return self.f_score < other.f_score
