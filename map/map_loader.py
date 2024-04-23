from pathlib import Path

import dill
from geopy import distance
from shapely import Point

from map.elements import Tag, Block
from map.graph import Graph
from map.map_handler import MapHandler
from map.relation_handler import RelationHandler


class MapLoader:

    def __init__(self, city_map_file, municipalities_file):
        self.city_map_file = city_map_file
        self.municipalities_file = municipalities_file
        self.restrictions = ["route", "route_master", "restriction"]
        self.nodes = {}
        self.ways = {}
        self.fuel_stations = {}

    def load_map(self, path):

        if path:
            saved_path = Path(f'{path}/graph.pkl')
            if saved_path.exists():
                cached_graph = dill.load(open(saved_path, 'rb'))

                if isinstance(cached_graph, Graph):
                    return cached_graph

        handler = MapHandler(self.municipalities_file)
        handler.apply_file(self.city_map_file)

        self.nodes = handler.nodes
        self.ways = handler.ways

        graph = self.get_graph(handler.nodes, handler.ways, handler.relations, handler.fuel_stations)

        if path and Path(path).exists():
            dill.dump(graph, open(f'{path}/graph.pkl', 'wb'))

        return graph

    def get_graph(self, nodes, ways, relations, fuel_stations):
        relations_by_type = RelationHandler.filter_relations(relations, self.restrictions)
        mapped_restrictions, via_nodes_restrictions = RelationHandler.map_restrictions(
            relations_by_type.get("restriction", []))

        graph = Graph()
        roads = [way for way in ways.values() if way.is_road]

        sum = 0

        for way in roads:

            way_restrictions = mapped_restrictions.get(way.id, {})

            last = None
            previous = None

            bus_stops = []
            obstacles = []
            length = 0.0

            for node_id in way.nodes:

                if last is None:
                    last = nodes[node_id]
                    previous = last
                    continue

                node = nodes[node_id]
                length += previous.length_to(node)

                connected_roads = [node_way for node_way in node.part_of if node_way.is_road]

                if node.is_bus_stop:
                    bus_stops.append(node_id)

                if node.is_delay:
                    obstacles.append(node_id)

                if len(connected_roads) > 1:

                    max_speed = way.tags.get("maxspeed", Tag("maxspeed", "50 km/h")).value.split()[0]

                    block = Block(way.id, max_speed, last.location, way.tags.get("name", Tag("name", "undefined")).value, length,
                                  (last.id, node_id), bus_stops, obstacles)
                    sum += length
                    graph.add_node(f"{way.id}:{last.id}:{node_id}", block)

                    self.check_gas_stations(last.location.latitude, last.location.longitude,
                                            f"{way.id}:{last.id}:{node_id}", fuel_stations)

                    graph.map[f"{way.id}:_:{node_id}"] = graph.map.get(f"{way.id}:_:{node_id}", []) + [last.id]
                    graph.map[f"{way.id}:{last.id}:_"] = graph.map.get(f"{way.id}:{last.id}:_", []) + [node_id]

                    if node.id in way_restrictions and "no_u_turn" in way_restrictions[node.id].get(way.id, []):
                        block = Block(way.id, max_speed, last.location, way.tags.get("name", Tag("name", "undefined")).value, length,
                                      (node_id, last.id), bus_stops, obstacles)
                        sum += length
                        graph.add_node(f"{way.id}:{node_id}:{last.id}", block)

                        graph.map[f"{way.id}:{node_id}:_"] = graph.map.get(f"{way.id}:{node_id}:_", []) + [last.id]
                        graph.map[f"{way.id}:_:{last.id}"] = graph.map.get(f"{way.id}:_:{last.id}", []) + [node_id]

                    last = node
                    previous = node
                    length = 0
                    bus_stops = []
                    obstacles = []

        graph.avg_length = sum / graph.count

        for way in roads:
            way_restrictions = mapped_restrictions.get(way.id, {})
            way_nodes = [nodes[node_id] for node_id in way.nodes]
            self.build_connections(graph, way, way_nodes, way_restrictions)

            if way.is_oneway == "no":
                self.build_connections(graph, way, list(reversed(way_nodes)), way_restrictions, True)

        self.apply_via_restrictions(graph, via_nodes_restrictions)
        return graph

    def build_connections(self, graph, way, nodes, restrictions, reversed_order=False):

        last = None

        for node in nodes:

            node_restrictions = restrictions.get(node.id, {})

            if last is None:
                last = node.id
                continue

            connected_roads = [node_way for node_way in node.part_of if node_way.is_road]

            if len(connected_roads) < 2:
                continue

            key = f"{way.id}:{last}:{node.id}" if not reversed_order else f"{way.id}:{node.id}:{last}"

            for road in connected_roads:

                node_index_in_road = road.nodes.index(node.id)

                ordered, reverse = road.turn_to(nodes[0], nodes[-1], self.nodes[
                    road.nodes[node_index_in_road - 1 if node_index_in_road > 0 else 1]])

                to_road_restrictions = node_restrictions.get(road.id, [])

                left, right, straight = RelationHandler.map_restrictions_by_direction(to_road_restrictions)

                if (road.is_oneway in ["yes", "no"] and ((ordered == "left" and left) or (ordered == "right" and right)
                                                         or (ordered == "straight" and straight))):
                    connections = graph.map.get(f"{road.id}:{node.id}:_", [])

                    for connection in connections:
                        graph.add_edge(key, f"{road.id}:{node.id}:{connection}")

                if (road.is_oneway in ["-1", "no"] and ((reverse == "left" and left) or (reverse == "right" and right)
                                                        or (reverse == "straight" and straight))):

                    if road.is_oneway == "no" and "no_u_turn" in to_road_restrictions:
                        key = f"{way.id}:{node.id}:{last}"

                    connections = graph.map.get(f"{road.id}:_:{node.id}", [])

                    for connection in connections:
                        graph.add_edge(key, f"{road.id}:{connection}:{node.id}")

            last = node.id

    def apply_via_restrictions(self, graph, via_nodes_restrictions):

        for via_id in via_nodes_restrictions.keys():

            if via_id not in self.ways:
                continue

            via_way = self.ways[via_id]
            last_via_node = self.nodes[via_way.nodes[-1]]

            connected_roads_keys = [key for key in graph.edges.keys() if
                                    key.startswith(f"{via_id}:") and key.endswith(f":{last_via_node.id}")]

            connected_roads = []

            for key in connected_roads_keys:
                connected_roads += graph.edges[key]

            restrictions = via_nodes_restrictions[via_id]

            for from_id in restrictions.keys():

                from_restrictions = restrictions[from_id]

                from_way = self.ways[from_id]

                key = f"{from_id}:{next(iter(graph.map[f"{from_id}:_:{from_way.nodes[-1]}"]))}:{from_way.nodes[-1]}"

                graph.edges[key] = set([connection for connection in graph.edges[key] if
                                        not connection.startswith(f"{via_id}:")])

                for road_key in connected_roads:

                    road_id, start_node, end_node = road_key.split(":")

                    road = self.ways[int(road_id)]

                    if road.id == from_id:
                        continue

                    if road.id in from_restrictions:

                        (left, right, straight) = RelationHandler.map_restrictions_by_direction(
                            from_restrictions[road.id])

                        node_index_in_road = len(via_way.nodes) - 1

                        ordered, _ = via_way.turn_to(self.nodes[int(start_node)], self.nodes[int(end_node)], self.nodes[
                            via_way.nodes[node_index_in_road - 1 if node_index_in_road > 0 else 1]])

                        if ((ordered == "left" and left) or (ordered == "right" and right)
                                or (ordered == "straight" and straight)):
                            graph.add_edge(key, road_key)
                    else:
                        graph.add_edge(key, road_key)

    def check_gas_stations(self, latitude, longitude, key, fuel_stations):

        point = Point(latitude, longitude)

        for gas_station, (item_location, polygon) in fuel_stations.items():

            if polygon.contains(point):

                distance_value = distance.distance((latitude, longitude), item_location).kilometers

                if gas_station in self.fuel_stations:

                    _, length = self.fuel_stations[gas_station]

                    if length < distance_value:
                        continue

                self.fuel_stations[gas_station] = (key, distance_value)
