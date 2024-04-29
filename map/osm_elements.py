from dataclasses import dataclass
import numpy as np
from geopy import distance

from map.map_elements import ElementType, Location


@dataclass
class Tag:
    key: str
    value: str


@dataclass
class Segment:
    start_index: int
    end_index: int


@dataclass
class Way:
    id: str
    nodes: list[str]
    tags: dict[str, Tag]
    bus_routes: list[(int, int)]
    gazelle_routes: list[(int, Segment, (str, int))]

    @property
    def is_roundabout(self):
        return "junction" in self.tags and self.tags["junction"].value in ["roundabout", "circular"]

    @property
    def is_path(self):
        paths = ["footway", "bridleway", "steps", "corridor", "path", "via_ferrata", "pedestrian", "path"]

        return "highway" in self.tags and self.tags["highway"].value in paths

    @property
    def is_road(self):
        roads = ["motorway", "trunk", "primary", "secondary", "tertiary", "unclassified", "residential",
                 "motorway_link",
                 "trunk_link", "primary_link", "secondary_link", "tertiary_link", "living_street", "escape", "road",
                 "bus_way", "service"]

        return "highway" in self.tags and self.tags["highway"].value in roads

    @property
    def is_oneway(self):
        if not self.is_road or "oneway" not in self.tags:
            return "no"
        return self.tags["oneway"].value

    @staticmethod
    def determine_direction(angle: float, cross: float) -> str:
        if angle < 28 or angle >= 152 or cross == 0:
            return "straight"
        elif cross > 0:
            return "left"
        else:
            return "right"

    @staticmethod
    def turn_to(start_node, last_node, ordered_node, reversed_node):
        start_location = (start_node.location.latitude, start_node.location.longitude)
        last_location = (last_node.location.latitude, last_node.location.longitude)

        angle, cross = Way.calculate_angle(start_location, last_location,
                                           (ordered_node.location.latitude, ordered_node.location.longitude))
        ordered = Way.determine_direction(angle, cross)

        angle, cross = Way.calculate_angle(start_location, last_location,
                                           (reversed_node.location.latitude, reversed_node.location.longitude))
        reverse = Way.determine_direction(angle, cross)

        return ordered, reverse

    @staticmethod
    def calculate_angle(road_start, road_end, node):
        v1 = np.array([road_end[0] - node[0], road_end[1] - node[1]])
        v2 = np.array([road_start[0] - node[0], road_start[1] - node[1]])

        n1 = np.linalg.norm(v1)
        n2 = np.linalg.norm(v2)

        if n1 == 0 or n2 == 0:
            return 0, 0

        cos_angle = np.dot(v1, v2) / (n1 * n2)

        if cos_angle < -1:
            cos_angle = -1.0
        elif cos_angle > 1.0:
            cos_angle = 1.0

        angle_rad = np.arccos(cos_angle)

        angle_deg = np.degrees(angle_rad)

        return angle_deg, np.cross(v1, v2)


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

        if ("bus" in self.tags and self.tags["bus"].value == "yes" and "public_transport" in self.tags and self.tags[
                                                                "public_transport"].value == "stop_position"):
            return ElementType.BUS_STOP

        if "highway" in self.tags:

            if self.tags["highway"].value == "bus_stop":
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


@dataclass
class WaySegment:
    way_id: int
    start_node: int
    end_node: int
