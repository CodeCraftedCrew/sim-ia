from pathlib import Path

import dill
from geopy import distance
from shapely import Point

from map.graph import Graph
from map.map_elements import Element, Block, ElementType, Route
from map.map_handler import MapHandler
from map.osm_elements import Tag, Way
from map.relation_handler import RelationHandler


class MapLoader:

    def __init__(self, city_map_file, municipalities_file):
        self.city_map_file = city_map_file
        self.municipalities_file = municipalities_file
        self.restrictions = ["route", "route_master", "restriction"]
        self.nodes = {}
        self.ways = {}
        self.relations = {}
        self.places_of_interest = {}
        self.bus_routes = {}
        self.gazelle_routes = {}
        self.replaced = set()

    def load_maps(self, path, gazelles_file):

        if path:
            saved_path = Path(f'{path}/graph.pkl')
            if saved_path.exists():
                cached_graph = dill.load(open(saved_path, 'rb'))

                if isinstance(cached_graph, Graph):
                    if Path(f'{path}/simplified_graph.pkl').exists():
                        simplified_graph = dill.load(open(f'{path}/simplified_graph.pkl', 'rb'))

                        if isinstance(simplified_graph, Graph):
                            return cached_graph, simplified_graph

                    simplified_graph = cached_graph.simplify(0.5)
                    dill.dump(simplified_graph, open(f'{path}/simplified_graph.pkl', 'wb'))

                    return cached_graph, simplified_graph

        handler = MapHandler(self.municipalities_file, gazelles_file)
        handler.apply_file(self.city_map_file)
        handler.populate_gazelle_routes()

        self.nodes = handler.nodes
        self.ways = handler.ways
        self.relations = handler.relations

        graph = self.get_graph(handler.places_of_interest)

        if path and Path(path).exists():
            dill.dump(graph, open(f'{path}/graph.pkl', 'wb'))

        simplified_graph = graph.simplify(0.5)

        if path and Path(path).exists():
            dill.dump(simplified_graph, open(f'{path}/simplified_graph.pkl', 'wb'))

        return graph, simplified_graph

    def get_graph(self, places_of_interest):
        relations_by_type = RelationHandler.filter_relations(self.relations, self.restrictions)
        mapped_restrictions, via_nodes_restrictions = RelationHandler.map_restrictions(
            relations_by_type.get("restriction", []))

        graph = Graph()
        roads = [way for way in self.ways.values() if way.is_road]

        sum_value = 0

        for way in roads:

            way_restrictions = mapped_restrictions.get(way.id, {})

            last = None
            last_index = 0
            previous = None

            elements = []
            length = 0.0

            for node_index, node_id in enumerate(way.nodes):

                if last is None:
                    last = self.nodes[node_id]
                    last_index = node_index
                    previous = last
                    continue

                node = self.nodes[node_id]
                length += previous.length_to(node)

                connected_roads = [node_way for node_way in node.part_of if node_way.is_road]

                ref = "ref"

                if node.type:
                    elements.append(Element(node.type, [f"{self.relations[relation_id].tags[ref].value}:{relation_id}"
                                                        for relation_id in node.bus_routes],
                                            length))

                if len(connected_roads) > 1 or node_index == len(way.nodes) - 1:

                    max_speed = way.tags.get("maxspeed", Tag("maxspeed", "50 km/h")).value.split()[0]

                    block = Block(way.id, max_speed, last.location, node.city,
                                  way.tags.get("name", Tag("name", "undefined")).value, length,
                                  (last.id, node_id), elements, way.is_roundabout)

                    sum_value += length

                    for index, bus_route_id in way.bus_routes:
                        bus_route = self.bus_routes.get(bus_route_id, {})
                        bus_route[index] = bus_route.get(index, []) + [block]
                        self.bus_routes[bus_route_id] = bus_route

                    gazelle_ids = []

                    for index, segment, gazelle_route_id in way.gazelle_routes:
                        if segment.start_index <= last_index and segment.end_index >= node_index:
                            gazelle_ids.append(f"{gazelle_route_id[0]}:{gazelle_route_id[1]}")
                            gazelle_route = self.gazelle_routes.get(gazelle_route_id, {})
                            gazelle_route[index] = gazelle_route.get(index, []) + [block]
                            self.gazelle_routes[gazelle_route_id] = gazelle_route

                    if len(gazelle_ids) > 0:
                        elements.append(Element(ElementType.GAZELLE_ROUTE, gazelle_ids, 0))

                    graph.add_node(block)
                    if node.city:
                        graph.nodes_by_municipality[node.city] = graph.nodes_by_municipality.get(node.city, []) + [block.id]

                    self.check_places_of_interest(last.location.latitude, last.location.longitude,
                                            block.id, places_of_interest)

                    graph.map[f"{way.id}:_:{node_id}"] = graph.map.get(f"{way.id}:_:{node_id}", []) + [last.id]
                    graph.map[f"{way.id}:{last.id}:_"] = graph.map.get(f"{way.id}:{last.id}:_", []) + [node_id]

                    if node.id in way_restrictions and "no_u_turn" in way_restrictions[node.id].get(way.id, []):
                        block = Block(way.id, max_speed, last.location, last.city,
                                      way.tags.get("name", Tag("name", "undefined")).value, length,
                                      (node_id, last.id), elements, way.is_roundabout)

                        if last.city:
                            graph.nodes_by_municipality[last.city] = graph.nodes_by_municipality.get(last.city, []) + [block.id]

                        sum_value += length
                        graph.add_node(block)

                        graph.map[f"{way.id}:{node_id}:_"] = graph.map.get(f"{way.id}:{node_id}:_", []) + [last.id]
                        graph.map[f"{way.id}:_:{last.id}"] = graph.map.get(f"{way.id}:_:{last.id}", []) + [node_id]

                    last = node
                    last_index = node_index
                    previous = node
                    length = 0
                    elements = []

        graph.avg_length = sum_value / graph.count

        for way in roads:
            way_restrictions = mapped_restrictions.get(way.id, {})
            way_nodes = [self.nodes[node_id] for node_id in way.nodes]
            self.build_connections(graph, way, way_nodes, way_restrictions)

            if way.is_oneway == "no":
                self.build_connections(graph, way, list(reversed(way_nodes)), way_restrictions, True)

        self.apply_via_restrictions(graph, via_nodes_restrictions)
        graph.bus_routes = self.build_bus_routes(graph, [relation for relation in relations_by_type["route_master"]
                                                         if relation.tags["route_master"].value == "bus"])
        graph.gazelle_routes = self.build_gazelle_routes(graph)
        graph.places_of_interest = self.places_of_interest
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
                turn_to_ordered_node = self.nodes[road.nodes[node_index_in_road - 1 if node_index_in_road > 0 else 1]]
                turn_to_reversed_node = self.nodes[
                    road.nodes[node_index_in_road + 1 if node_index_in_road < len(road.nodes) - 1 else 0]]

                ordered, reverse = Way.turn_to(nodes[0], nodes[-1], turn_to_ordered_node, turn_to_reversed_node)

                to_road_restrictions = node_restrictions.get(road.id, [])

                left, right, straight = RelationHandler.map_restrictions_by_direction(to_road_restrictions)

                connections = graph.map.get(f"{road.id}:{node.id}:_", [])

                if (road.is_oneway in ["yes", "no"] and ((ordered == "left" and left) or (ordered == "right" and right)
                                                         or (ordered == "straight" and straight))):
                    for connection in connections:
                        graph.add_edge(key, f"{road.id}:{node.id}:{connection}")
                else:
                    for connection in connections:
                        graph.add_edge(key, f"{road.id}:{node.id}:{connection}", True)

                connections = graph.map.get(f"{road.id}:_:{node.id}", [])

                if (road.is_oneway in ["-1", "no"] and ((reverse == "left" and left) or (reverse == "right" and right)
                                                        or (reverse == "straight" and straight))):

                    new_key = key

                    if road.is_oneway == "no" and "no_u_turn" in to_road_restrictions:
                        new_key = f"{way.id}:{node.id}:{last}"

                    for connection in connections:
                        graph.add_edge(new_key, f"{road.id}:{connection}:{node.id}")
                else:
                    for connection in connections:
                        graph.add_edge(key, f"{road.id}:{connection}:{node.id}", True)

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
                connected_roads += [road_id for road_id, walk in graph.edges[key] if not walk]

            restrictions = via_nodes_restrictions[via_id]

            for from_id in restrictions.keys():

                from_restrictions = restrictions[from_id]

                from_way = self.ways[from_id]

                idx = f"{from_id}:_:{from_way.nodes[-1]}"

                key = f"{from_id}:{next(iter(graph.map[idx]))}:{from_way.nodes[-1]}"

                self.replaced.update([connection for connection, walk in graph.edges[key] if not walk
                                      and connection.startswith(f"{via_id}:")])

                graph.edges[key] = set([(connection, walk) for connection, walk in graph.edges[key] if walk or
                                        not connection.startswith(f"{via_id}:")])

                for road_key in connected_roads:

                    road_id, start_node, end_node = road_key.split(":")

                    road = self.ways[int(road_id)]

                    if road.id == from_id:
                        continue

                    if road.id in from_restrictions:

                        (left, right, straight) = RelationHandler.map_restrictions_by_direction(
                            from_restrictions[road.id])

                        turn_to_ordered_node = self.nodes[via_way.nodes[len(via_way.nodes) - 1]]
                        turn_to_reversed_node = self.nodes[via_way.nodes[0]]

                        ordered, _ = Way.turn_to(self.nodes[int(start_node)], self.nodes[int(end_node)],
                                                 turn_to_ordered_node, turn_to_reversed_node)

                        if ((ordered == "left" and left) or (ordered == "right" and right)
                                or (ordered == "straight" and straight)):
                            graph.add_edge(key, road_key)
                    else:
                        graph.add_edge(key, road_key)

    def check_places_of_interest(self, latitude, longitude, key, places_of_interest):

        point = Point(latitude, longitude)

        for place_of_interest, (item_location, polygon) in places_of_interest.items():

            if polygon.contains(point):

                distance_value = distance.distance((latitude, longitude), item_location).kilometers

                if place_of_interest in self.places_of_interest:

                    _, length = self.places_of_interest[place_of_interest]

                    if length < distance_value:
                        continue

                self.places_of_interest[place_of_interest] = (key, distance_value)

    def build_bus_routes(self, graph, route_masters):

        bus_routes = {}
        trips = []

        for route_master in route_masters:

            ref = route_master.tags["ref"].value
            if ref in ["180"]:
                continue

            for member in route_master.members:
                if member.type == "r":
                    relation = self.relations[member.id]

                    ordered_items = [blocks for _, blocks
                                     in sorted(self.bus_routes[relation.id].items(), key=lambda x: x[0])]
                    trips.append(self.order_route(graph, ref, member.id, ordered_items))

            bus_routes[ref] = Route(ref, trips[0], trips[1] if len(trips) > 1 else reversed(trips[0]))

        return bus_routes

    def build_gazelle_routes(self, graph):
        gazelle_routes = {}

        for (key, route_index), items in self.gazelle_routes.items():

            route = gazelle_routes.get(key, Route(key, [], []))
            sorted_items = [blocks for _, blocks in sorted(items.items(), key=lambda x: float(x[0]))]

            ordered_route = self.order_route(graph, key, route_index, sorted_items)

            if route_index == 0:
                route.outbound_route = ordered_route
            else:
                route.return_route = ordered_route

            gazelle_routes[key] = route

        return gazelle_routes

    def order_route(self, graph, ref, idx, items):

        if len(items) < 2:
            return items

        first_way = items[0]
        second_way = items[1]

        route = []

        ordered = MapLoader.get_first_order(graph, ref, idx, first_way, second_way)

        if not ordered:
            raise Exception("Route no completely connected")

        route += ordered

        for index, blocks in enumerate(items[1:]):

            if any(block.is_roundabout for block in blocks):
                ordered_blocks = (MapLoader.order_roundabout(graph, ref, idx, route[-1], items[index + 2][0], blocks)
                                  or MapLoader.order_roundabout(graph, ref, idx, route[-1], items[index + 2][-1],
                                                                blocks))
            else:
                ordered_blocks = MapLoader.order_blocks(graph, ref, idx, route[-1], blocks)

            if not ordered_blocks and (blocks[0].id in self.replaced or blocks[-1].id in self.replaced):
                continue

            if not ordered_blocks:
                raise Exception("Route no completely connected")

            route += ordered_blocks

        return route

    @staticmethod
    def order_blocks(graph, ref, idx, block, other_blocks):

        if len(other_blocks) == 0:
            return None

        if graph.is_connected(block.id, other_blocks[-1].id):
            MapLoader.define_route_direction(other_blocks, ref, idx, -1)
            return list(reversed(other_blocks))

        if graph.is_connected(block.id, other_blocks[0].id):
            MapLoader.define_route_direction(other_blocks, ref, idx, 1)
            return other_blocks

        return None

    @staticmethod
    def order_roundabout(graph, ref, idx, start_block, end_block, other_blocks):
        ordered_blocks = []
        index = 0
        found = True
        while True:

            if found and graph.is_connected(other_blocks[index].id, end_block.id):
                ordered_blocks.append(other_blocks[index])
                MapLoader.define_route_direction(ordered_blocks, ref, idx, 1)
                return ordered_blocks

            if not found and graph.is_connected(start_block.id, other_blocks[index].id):
                found = True
                ordered_blocks.append(other_blocks[index])

                if graph.is_connected(other_blocks[index].id, end_block.id):
                    MapLoader.define_route_direction(ordered_blocks, ref, idx, 1)
                    return ordered_blocks

            if found:
                ordered_blocks.append(other_blocks[index])

            index += 1
            if index == len(other_blocks):
                if not found:
                    return None

                if len(ordered_blocks) == len(other_blocks):
                    return None

                index = 0

    @staticmethod
    def get_first_order(graph, ref, idx, first_way, second_way):

        if any(block.is_roundabout for block in second_way):
            if any(graph.is_connected(first_way[0].id, block.id) for block in second_way):
                MapLoader.define_route_direction(first_way, ref, idx, -1)
                return list(reversed(first_way))

            if any(graph.is_connected(first_way[-1].id, block.id) for block in second_way):
                MapLoader.define_route_direction(first_way, ref, idx, 1)

                return first_way

            return None

        if graph.is_connected(first_way[0].id, second_way[0].id) or graph.is_connected(first_way[0].id,
                                                                                       second_way[-1].id):
            MapLoader.define_route_direction(first_way, ref, idx, -1)
            return list(reversed(first_way))
        elif graph.is_connected(first_way[-1].id, second_way[0].id) or graph.is_connected(first_way[-1].id,

                                                                                          second_way[-1].id):
            MapLoader.define_route_direction(first_way, ref, idx, 1)

            return first_way

        return None

    @staticmethod
    def define_route_direction(blocks, ref, idx, direction):

        argument_id = f"{ref}:{idx}"
        new_argument_id = f"{ref}:{direction}"

        for block in blocks:
            for element in block.elements:
                new_arguments = []
                for argument in element.arguments:
                    if argument == argument_id:
                        new_arguments.append(new_argument_id)
                    else:
                        new_arguments.append(argument)
                element.arguments = new_arguments
