import heapq

from map.map_elements import Node


class Graph:

    def __init__(self):
        self.nodes = {}
        self.edges = {}
        self.map = {}
        self.bus_routes = {}
        self.gazelle_routes = {}
        self.count = 0
        self.avg_length = 0
        self.is_simplified = False

    def add_node(self, node):

        if node.id not in self.nodes:
            self.nodes[node.id] = node
            self.count += 1
        else:
            raise Exception("Node already exists")

    def add_edge(self, src, dest, walk=False):
        if src not in self.edges:
            self.edges[src] = {(dest, walk)}
        else:
            self.edges[src].add((dest, walk))

    def is_connected(self, src, dest, walk=False):

        if walk:
            return (src in self.edges and ((dest, walk) in self.edges[src] or (dest, False) in self.edges[src])
                    or self.reversed_connected(src, dest, walk))

        return src in self.edges and (dest, walk) in self.edges[src] or self.reversed_connected(src, dest, walk)

    def reversed_connected(self, src, dest, walk):
        node = self.nodes[src]
        reversed_key = f"{node.way_id}:{node.between[1]}:{node.between[0]}"

        if walk:
            return reversed_key in self.edges and ((dest, walk) in self.edges[reversed_key]
                                                   or (dest, False) in self.edges[reversed_key])

        return reversed_key in self.edges and (dest, walk) in self.edges[reversed_key]

    def get_route(self, ref, block):

        route = self.bus_routes.get(ref, None)

        if route is None:
            return []

        if route.outbound_route[0].id == block.id:
            return route.outbound_route

        if route.return_route[0].id == block.id:
            return route.return_route

    def simplify(self, radio):
        simplified_graph = Graph()

        simplified_nodes = {node.id: node for node in self.nodes.values() if node.contains_stop()}

        length_to_start = {key: 0 for key in simplified_nodes.keys()}
        sum_length = 0

        open_set = []

        for node in simplified_nodes.values():
            heapq.heappush(open_set, Node(node.id, g_score=node.length, f_score=0))

        while open_set:

            current_node = heapq.heappop(open_set)
            if current_node.id not in simplified_graph.nodes:
                simplified_graph.add_node(current_node)
                sum_length += current_node.g_score

            if current_node.id in self.edges:
                for neighbor_id, _ in self.edges[current_node.id]:

                    neighbor = self.nodes[neighbor_id]
                    tentative_length = length_to_start[current_node.id] + current_node.g_score

                    if tentative_length > radio and not neighbor.contains_stop():
                        continue

                    simplified_graph.add_edge(current_node.id, neighbor_id)

                    if neighbor_id not in length_to_start or tentative_length < length_to_start[neighbor_id]:
                        length_to_start[neighbor_id] = tentative_length
                        heapq.heappush(open_set, Node(neighbor_id, g_score=neighbor.length, f_score=tentative_length))

        simplified_graph.avg_length = sum_length / simplified_graph.count
        simplified_graph.is_simplified = True
        return simplified_graph
