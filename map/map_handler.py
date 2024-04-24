import math

import osmium
from shapely import Point, Polygon

from map.elements import Relation, Member, Tag, Location, Node, Way


def read_poly_file(poly_file):
    polygons = []
    with open(poly_file, 'r') as f:
        lines = f.readlines()
        polygon_coords = []
        name = ""
        start = True
        for i in range(len(lines)):
            if start:
                name = lines[i].strip()
                start = False
                continue
            if lines[i].strip() == "END":
                polygons.append((name, Polygon(polygon_coords)))
                polygon_coords = []
                start = True
            else:
                coords = tuple(map(float, lines[i].strip().split()))
                polygon_coords.append(coords)
    return polygons


def get_polygon_from_point(latitude, longitude):
    min_lat = latitude - 0.00045
    max_lat = latitude + 0.00045
    min_lon = longitude - 0.00045 / math.cos(latitude)
    max_lon = longitude + 0.00045 / math.cos(latitude)

    coordinates = [
        (min_lat, min_lon),
        (min_lat, max_lon),
        (max_lat, max_lon),
        (max_lat, min_lon),
    ]

    return (latitude, longitude), Polygon(coordinates + [(min_lat, min_lon)])


def get_polygon_from_points(points):
    latitude = sum(lat for lat, lon in points) / len(points)
    longitude = sum(lon for lat, lon in points) / len(points)

    return get_polygon_from_point(latitude, longitude)


class MapHandler(osmium.SimpleHandler):
    def __init__(self, municipalities_file):
        super(MapHandler, self).__init__()
        self.municipalities_polygons = read_poly_file(municipalities_file)
        self.nodes = {}
        self.ways = {}
        self.relations = {}
        self.fuel_stations = {}
        self.last_municipality = (
            "playa", next((polygon for name, polygon in self.municipalities_polygons if name == "playa")))

    def node(self, node):
        self.nodes[node.id] = Node(
            id=node.id,
            city=self.get_municipality(Point(node.location.lon, node.location.lat)),
            location=Location(node.location.lat, node.location.lon),
            tags={tag.k: Tag(tag.k, tag.v) for tag in node.tags},
            part_of=[],
            bus_routes=[])

        if "amenity" in node.tags and node.tags["amenity"] == "fuel":
            self.fuel_stations[("node", node.id)] = get_polygon_from_point(node.location.lat, node.location.lon)

    def way(self, way):

        new_way = Way(way.id, [], {tag.k: Tag(tag.k, tag.v) for tag in way.tags}, [])
        points = []

        for node_ref in way.nodes:
            node = self.nodes.get(node_ref.ref, None)
            if node is not None:
                node.part_of.append(new_way)
                new_way.nodes.append(node_ref.ref)
                points.append((node.location.latitude, node.location.longitude))

        if "amenity" in way.tags and way.tags["amenity"] == "fuel":
            self.fuel_stations[("way", way.id)] = get_polygon_from_points(points)

        self.ways[way.id] = new_way

    def relation(self, relation):

        new_relation = Relation(
            id=relation.id,
            members=[Member(member.role, member.type, member.ref) for member in relation.members],
            tags={tag.k: Tag(tag.k, tag.v) for tag in relation.tags})

        self.relations[relation.id] = new_relation

        if "type" in relation.tags and relation.tags["type"] == "route" and relation.tags["route"] == "bus":
            ways = [member for member in new_relation.members if member.role == "" and member.type == "w"]
            nodes = [member for member in new_relation.members if "stop" in member.role and member.type == "n"]

            for node_member in nodes:
                node = self.nodes.get(node_member.id, None)
                if node:
                    node.bus_routes.append(relation.id)

            for i in range(len(ways)):
                way = self.ways.get(ways[i].id, None)
                if way:
                    way.bus_routes.append((i, relation.id))

    def get_municipality(self, point):

        name, municipality = self.last_municipality

        if municipality.contains(point):
            return name

        for name, municipality in self.municipalities_polygons:
            if municipality.contains(point):
                self.last_municipality = (name, municipality)
                return name

        return None
