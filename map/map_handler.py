import json
import math

import osmium
from shapely import Point, Polygon

from map.osm_elements import WaySegment, Node, Location, Tag, Way, Relation, Member, Segment


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


def read_gazelles_file(gazelles_file):
    with open(gazelles_file, "r") as file:
        data: dict[str, dict[str, dict[str, list[int]]]] = json.load(file)

    gazelle_routes = {}
    for key, routes in data.items():
        outbound_dict = routes["outbound"]
        outbound_route = []
        for index, elements in outbound_dict.items():
            outbound_route.append((float(index), WaySegment(*elements)))

        return_dict = routes["return"]
        return_route = []
        for index, elements in return_dict.items():
            return_route.append((index, WaySegment(*elements)))

        gazelle_routes[key] = (outbound_route, return_route)

    return gazelle_routes


class MapHandler(osmium.SimpleHandler):
    def __init__(self, municipalities_file, gazelles_file):
        super(MapHandler, self).__init__()
        self.municipalities_polygons = read_poly_file(municipalities_file)
        self.gazelle_routes = read_gazelles_file(gazelles_file)
        self.nodes = {}
        self.ways = {}
        self.relations = {}
        self.fuel_stations = {}
        self.last_municipality = (
            "playa", next((polygon for name, polygon in self.municipalities_polygons if name == "playa")))

        self.violated_restrictions = [5998635, 5812858, 3877122, 10686278, 13326603, 13414499, 6281993, 13042077,
                                      17082883, 7519120, 15854348, 5558722, 6100445, 14224436, 13102529, 13045496,
                                      12951819, 13438840, 5558759, 5321414, 11851378]

        self.double_way_streets = [419551351, 449293033, 288841336, 623248405, 38834405, 909187518, 369443996,
                                   231735599, 419131443, 1058221850, 262787452, 262609566, 367547663, 370318330,
                                   1066367181, 904481878, 423252680, 415164925, 391096669, 391096672, 391097720,
                                   388735860, 668246994]

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

        new_way = Way(way.id, [], {tag.k: Tag(tag.k, tag.v) for tag in way.tags}, [], [])
        points = []

        for node_ref in way.nodes:
            node = self.nodes.get(node_ref.ref, None)
            if node is not None:
                node.part_of.append(new_way)
                new_way.nodes.append(node_ref.ref)
                points.append((node.location.latitude, node.location.longitude))

        if "amenity" in way.tags and way.tags["amenity"] == "fuel":
            self.fuel_stations[("way", way.id)] = get_polygon_from_points(points)

        if way.id in self.double_way_streets:
            new_way.tags["oneway"] = Tag("oneway", "no")

        self.ways[way.id] = new_way

    def relation(self, relation):

        if relation.id in self.violated_restrictions:
            return

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
                if relation.id == 6185688 and ways[i].id == 700611170:
                    continue

                way = self.get_way(relation.id, ways[i].id)

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

    def populate_gazelle_routes(self):
        for key, routes in self.gazelle_routes.items():
            for route_index, route in enumerate(routes):
                for index, way_segment in route:
                    way: Way = self.ways.get(way_segment.way_id)
                    if way is None:
                        continue

                    try:
                        start_index = way.nodes.index(way_segment.start_node) if way_segment.start_node != 0 else 0
                        end_index = way.nodes.index(way_segment.end_node) if way_segment.end_node != 0 else len(
                            way.nodes) - 1
                    except ValueError:
                        continue

                    new_segment = Segment(start_index, end_index)
                    way.gazelle_routes.append((index, new_segment, (key, route_index)))

    def get_way(self, relation_id, way_id):
        if relation_id == 5504372 and way_id == 1089765795:
            return self.ways.get(1089765794, None)
        elif relation_id == 5504371 and way_id == 1089765795:
            return self.ways.get(1089765794, None)
        elif relation_id == 5972917 and way_id == 1089765795:
            return self.ways.get(1089765794, None)
        elif relation_id == 6185688 and way_id == 849582499:
            return self.ways.get(781656957, None)
        else:
            return self.ways.get(way_id, None)
