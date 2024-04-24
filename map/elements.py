from dataclasses import dataclass
from enum import Enum, auto

from geopy import distance
import numpy as np


@dataclass
class Location:
    latitude: float
    longitude: float


@dataclass
class Tag:
    key: str
    value: str


@dataclass
class Way:
    id: str
    nodes: list[str]
    tags: dict[str, Tag]
    bus_routes: list[(int, int)]

    @property
    def is_path(self):
        paths = ["footway", "bridleway", "steps", "corridor", "path", "via_ferrata", "pedestrian", "path"]

        return "highway" in self.tags and self.tags["highway"].value in paths

    @property
    def is_road(self):
        roads = ["motorway", "trunk", "primary", "secondary", "tertiary", "unclassified", "residential", "motorway_lik",
                 "trunk_link", "primary_link", "secondary_link", "tertiary_link", "living_street", "escape", "road",
                 "bus_way", "service"]

        return "highway" in self.tags and self.tags["highway"].value in roads

    @property
    def is_oneway(self):
        if not self.is_road or "oneway" not in self.tags:
            return "no"
        return self.tags["oneway"].value

    def turn_to(self, start_node, last_node, other_node):

        angle = self.calculate_angle((other_node.location.latitude, other_node.location.longitude),
                                     (start_node.location.latitude, start_node.location.longitude),
                                     (last_node.location.latitude, last_node.location.longitude))

        if angle == 180 or angle == 0:
            return "straight", "straight"

        if angle < 180:
            return "left", "right"

        return "right", "left"

    @staticmethod
    def calculate_angle(node_coords, road_start_coords, road_end_coords):
        v1 = np.array([road_start_coords[0] - node_coords[0], road_start_coords[1] - node_coords[1]])
        v2 = np.array([road_end_coords[0] - node_coords[0], road_end_coords[1] - node_coords[1]])

        n1 = np.linalg.norm(v1)
        n2 = np.linalg.norm(v2)

        if n1 == 0 or n2 == 0:
            return 0

        cos_angle = np.dot(v1, v2) / (n1 * n2)

        if cos_angle < -1:
            cos_angle = -1.0
        elif cos_angle > 1.0:
            cos_angle = 1.0

        angle_rad = np.arccos(cos_angle)

        angle_deg = np.degrees(angle_rad)

        return angle_deg


@dataclass
class Node:
    id: str
    city: str
    location: Location
    tags: dict[str, Tag]
    part_of: list[Way]
    bus_routes: list[int]

    @property
    def type(self):

        if "highway" in self.tags:

            if self.tags["highway"].value == "bus_stop" or ("bus" in self.tags and self.tags["bus"].value == "yes"
                                                            and "public_transport" in self.tags and self.tags[
                                                                "public_transport"].value == "stop_position"):
                return ElementType.BUS_STOP

            if self.tags["highway"] == "crossing":
                return ElementType.CROSSING

            elif self.tags["highway"] == "traffic_signals":
                return ElementType.TRAFFIC_LIGHT

            elif self.tags["highway"] in ["give_way", "giveway"]:
                return ElementType.GIVE_WAY

            elif self.tags["highway"] == "stop":
                return ElementType.STOP

        if "railway" in self.tags:
            if self.tags["railway"].value == "crossing":
                return ElementType.CROSSING

            elif self.tags["railway"] == "level_crossing":
                return ElementType.TRAIN_RAIL

        return None

    def length_to(self, other):
        return distance.distance((self.location.latitude, self.location.longitude),
                                 (other.location.latitude, other.location.longitude)).kilometers


@dataclass
class Member:
    role: str
    type: str
    id: int


@dataclass
class Relation:
    id: str
    members: list[Member]
    tags: dict[str, Tag]


@dataclass
class Restriction:
    from_id: str
    to_id: str
    via_id: str
    restriction_type: str


class ElementType(Enum):
    BUS_STOP = auto()
    STOP = auto()
    TRAFFIC_LIGHT = auto()
    GIVE_WAY = auto()
    CROSSING = auto()
    TRAIN_RAIL = auto()


@dataclass
class Element:
    type: ElementType
    arguments: list[str]
    position: float


@dataclass
class Block:
    way_id: str
    max_speed: int
    location: Location
    name: str
    length: float
    between: (int, int)
    elements: list[Element]

    def length_to(self, other):
        return distance.distance((self.location.latitude, self.location.longitude),
                                 (other.location.latitude, other.location.longitude)).kilometers


@dataclass
class Route:
    name: str
    outbound_route: list[Block]
    return_route: list[Block]
