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


class MapHandler(osmium.SimpleHandler):
    def __init__(self, municipalities_file):
        super(MapHandler, self).__init__()
        self.municipalities_polygons = read_poly_file(municipalities_file)
        self.nodes = {}
        self.ways = {}
        self.relations = {}
        self.last_municipality = (
            "playa", next((polygon for name, polygon in self.municipalities_polygons if name == "playa")))

    def node(self, node):
        self.nodes[node.id] = Node(
            id=node.id,
            city=self.get_municipality(Point(node.location.lon, node.location.lat)),
            location=Location(node.location.lat, node.location.lon),
            tags={tag.k: Tag(tag.k, tag.v) for tag in node.tags},
            part_of=[])

    def way(self, way):

        new_way = Way(way.id, [], {tag.k: Tag(tag.k, tag.v) for tag in way.tags})

        for node_ref in way.nodes:
            node = self.nodes.get(node_ref.ref, None)
            if node is not None:
                node.part_of.append(new_way)
                new_way.nodes.append(node_ref.ref)

        self.ways[way.id] = new_way

    def relation(self, relation):
        self.relations[relation.id] = Relation(
            id=relation.id,
            members=[Member(member.role, member.type, member.ref) for member in relation.members],
            tags={tag.k: Tag(tag.k, tag.v) for tag in relation.tags})

    def get_municipality(self, point):

        name, municipality = self.last_municipality

        if municipality.contains(point):
            return name

        for name, municipality in self.municipalities_polygons:
            if municipality.contains(point):
                self.last_municipality = (name, municipality)
                return name

        return None